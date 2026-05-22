from __future__ import annotations

import json

from qrope.stage133_authorized_runner_command_packet import run_stage133_packet, write_stage133_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _fixture(tmp_path, *, authorized: bool = False):
    status = "ready_to_run" if authorized else "blocked"
    _write_json(
        tmp_path / "stage116.json",
        {
            "decision": "PROVIDER_RUNNER_PLAN_READY_FOR_EXECUTION" if authorized else "PROVIDER_RUNNER_PLAN_PREPARED_EXECUTION_BLOCKED",
            "runner_records": [
                {
                    "provider": "ibm_runtime",
                    "window_id": "window_0",
                    "status": status,
                    "job_count": 2,
                    "blockers": [] if authorized else ["stage111_provider_not_ready"],
                    "runner_command": (
                        "python scripts/provider_runners/run_ibm_runtime_stage112_jobs.py "
                        "--job-shard jobs.jsonl --provider-results results.jsonl "
                        "--stage111-results stage111.json --stage118-results stage118.json --stage129-results stage129.json"
                    ),
                }
            ],
        },
    )
    _write_json(
        tmp_path / "stage129.json",
        {
            "decision": "LIVE_CUTOVER_AUTHORIZED" if authorized else "LIVE_CUTOVER_BLOCKED_READINESS_REQUIRED",
            "provider_records": [
                {
                    "provider": "ibm_runtime",
                    "cutover_authorized": authorized,
                    "blockers": [] if authorized else ["stage106:not_ready"],
                }
            ],
        },
    )
    _write_json(
        tmp_path / "stage132.json",
        {
            "decision": "GUARDED_SDK_FACTORIES_IMPLEMENTED_CUTOVER_BLOCKED",
            "provider_records": [{"provider": "ibm_runtime", "ready": True}],
        },
    )
    return tmp_path / "stage116.json", tmp_path / "stage129.json", tmp_path / "stage132.json"


def test_stage133_blocks_commands_until_cutover_authorized(tmp_path) -> None:
    stage116, stage129, stage132 = _fixture(tmp_path, authorized=False)

    result = run_stage133_packet(stage116_results_path=stage116, stage129_results_path=stage129, stage132_results_path=stage132)

    record = result["command_records"][0]
    assert result["decision"] == "AUTHORIZED_RUNNER_COMMANDS_PREPARED_EXECUTION_BLOCKED"
    assert result["authorized_runner_count"] == 0
    assert record["command_authorized"] is False
    assert record["live_submit_command_available"] is False
    assert record["live_submit_command"] == ""
    assert "stage129:cutover_not_authorized" in record["blockers"]


def test_stage133_authorizes_only_complete_command_records(tmp_path) -> None:
    stage116, stage129, stage132 = _fixture(tmp_path, authorized=True)

    result = run_stage133_packet(stage116_results_path=stage116, stage129_results_path=stage129, stage132_results_path=stage132)

    assert result["decision"] == "AUTHORIZED_RUNNER_COMMANDS_READY"
    assert result["authorized_runner_count"] == 1
    assert result["command_records"][0]["command_authorized"] is True
    assert result["command_records"][0]["live_submit_command_available"] is True
    assert "--allow-live-submit" in result["command_records"][0]["live_submit_command"]
    assert "--submitter qrope.provider_adapters.ibm_runtime:submit" in result["command_records"][0]["live_submit_command"]


def test_stage133_outputs_are_written(tmp_path) -> None:
    stage116, stage129, stage132 = _fixture(tmp_path, authorized=False)
    result = run_stage133_packet(stage116_results_path=stage116, stage129_results_path=stage129, stage132_results_path=stage132)

    paths = write_stage133_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert manifest["runner_count"] == 1
    assert "ibm_runtime" in summary
    assert "stage129:cutover_not_authorized" in summary
