from __future__ import annotations

import json

from qrope.stage134_runner_result_intake_alignment_audit import run_stage134_audit, write_stage134_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _fixture(tmp_path, *, ready: bool = False):
    output_path = "logs/provider_results/ibm_runtime/window_0/provider_job_results.jsonl"
    runner_command = f"python runner.py --job-shard jobs.jsonl --provider-results {output_path} --stage129-results stage129.json"
    _write_json(
        tmp_path / "stage133.json",
        {
            "decision": "AUTHORIZED_RUNNER_COMMANDS_READY" if ready else "AUTHORIZED_RUNNER_COMMANDS_PREPARED_EXECUTION_BLOCKED",
            "command_records": [
                {
                    "provider": "ibm_runtime",
                    "window_id": "window_0",
                    "job_count": 2,
                    "command_authorized": ready,
                    "live_submit_command_available": ready,
                    "runner_command": runner_command,
                    "live_submit_command": f"{runner_command} --allow-live-submit" if ready else "",
                }
            ],
        },
    )
    _write_json(
        tmp_path / "stage115.json",
        {
            "decision": "PROVIDER_RESULTS_COLLECTED_FOR_STAGE113" if ready else "PROVIDER_RESULTS_COLLECTION_BLOCKED_RESULTS_MISSING",
            "wrote_stage113_input": ready,
            "stage152_write_ready": ready,
            "stage152_write_blockers": [],
            "stage152_first_provider_runner_command_count": 1 if ready else 0,
            "stage152_first_provider_authorized_runner_count": 1 if ready else 0,
            "stage152_first_provider_live_submit_ready_count": 1 if ready else 0,
            "stage152_all_first_provider_commands_authorized": ready,
            "stage152_all_first_provider_commands_live_submit_ready": ready,
            "shard_records": [
                {
                    "provider": "ibm_runtime",
                    "window_id": "window_0",
                    "expected_job_count": 2,
                    "missing_job_count": 0 if ready else 2,
                    "ready": ready,
                    "result_path": output_path,
                    "missing_evidence": [] if ready else ["provider_result_file_missing", "job_results_missing"],
                }
            ],
        },
    )
    return tmp_path / "stage115.json", tmp_path / "stage133.json"


def test_stage134_blocks_until_command_and_collector_are_ready(tmp_path) -> None:
    stage115, stage133 = _fixture(tmp_path, ready=False)

    result = run_stage134_audit(stage115_results_path=stage115, stage133_results_path=stage133)

    record = result["intake_records"][0]
    assert result["decision"] == "RUNNER_RESULT_INTAKE_ALIGNED_EXECUTION_BLOCKED"
    assert result["ready_intake_count"] == 0
    assert record["stage113_ready_after_collection"] is False
    assert "stage133_command_not_authorized" in record["blockers"]
    assert "stage115:provider_result_file_missing" in record["blockers"]
    assert "stage115_not_collected_for_stage113" in record["blockers"]
    assert "stage133_blocked_command_exposes_live_submit_command" not in record["blockers"]


def test_stage134_reports_ready_when_command_and_collector_are_ready(tmp_path) -> None:
    stage115, stage133 = _fixture(tmp_path, ready=True)

    result = run_stage134_audit(stage115_results_path=stage115, stage133_results_path=stage133)

    assert result["decision"] == "RUNNER_RESULT_INTAKE_READY_FOR_STAGE113"
    assert result["ready_intake_count"] == 1
    assert result["intake_records"][0]["stage113_ready_after_collection"] is True
    assert result["intake_records"][0]["stage115_handoff_ready"] is True
    assert result["intake_records"][0]["live_submit_command_available"] is True
    assert result["intake_records"][0]["live_submit_command_present"] is True


def test_stage134_blocks_ready_shard_without_stage115_stage113_handoff(tmp_path) -> None:
    stage115, stage133 = _fixture(tmp_path, ready=True)
    payload = json.loads(stage115.read_text(encoding="utf-8"))
    payload["decision"] = "PROVIDER_RESULTS_READY_TO_COLLECT"
    payload["wrote_stage113_input"] = False
    payload["stage152_write_ready"] = False
    payload["stage152_write_blockers"] = ["stage152_live_execution_guard_not_ready"]
    _write_json(stage115, payload)

    result = run_stage134_audit(stage115_results_path=stage115, stage133_results_path=stage133)

    record = result["intake_records"][0]
    assert result["decision"] == "RUNNER_RESULT_INTAKE_ALIGNED_EXECUTION_BLOCKED"
    assert record["collector_ready"] is True
    assert record["stage115_handoff_ready"] is False
    assert "stage115_not_collected_for_stage113" in record["blockers"]
    assert "stage115_did_not_write_stage113_input" in record["blockers"]
    assert "stage115_stage152_write_not_ready" in record["blockers"]


def test_stage134_blocks_authorized_command_without_live_submit_command(tmp_path) -> None:
    stage115, stage133 = _fixture(tmp_path, ready=True)
    payload = json.loads(stage133.read_text(encoding="utf-8"))
    payload["command_records"][0]["live_submit_command_available"] = False
    payload["command_records"][0]["live_submit_command"] = ""
    _write_json(stage133, payload)

    result = run_stage134_audit(stage115_results_path=stage115, stage133_results_path=stage133)

    record = result["intake_records"][0]
    assert result["decision"] == "RUNNER_RESULT_INTAKE_ALIGNED_EXECUTION_BLOCKED"
    assert "stage133_authorized_command_missing_live_submit_command" in record["blockers"]


def test_stage134_blocks_blocked_command_that_exposes_live_submit_command(tmp_path) -> None:
    stage115, stage133 = _fixture(tmp_path, ready=False)
    payload = json.loads(stage133.read_text(encoding="utf-8"))
    payload["command_records"][0]["live_submit_command_available"] = True
    payload["command_records"][0]["live_submit_command"] = payload["command_records"][0]["runner_command"] + " --allow-live-submit"
    _write_json(stage133, payload)

    result = run_stage134_audit(stage115_results_path=stage115, stage133_results_path=stage133)

    record = result["intake_records"][0]
    assert "stage133_blocked_command_exposes_live_submit_command" in record["blockers"]


def test_stage134_outputs_are_written(tmp_path) -> None:
    stage115, stage133 = _fixture(tmp_path, ready=False)
    result = run_stage134_audit(stage115_results_path=stage115, stage133_results_path=stage133)

    paths = write_stage134_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert manifest["runner_count"] == 1
    assert "ibm_runtime" in summary
