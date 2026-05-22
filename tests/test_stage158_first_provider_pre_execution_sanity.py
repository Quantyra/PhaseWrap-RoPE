from __future__ import annotations

import json

from qrope.stage158_first_provider_pre_execution_sanity import (
    run_stage158_pre_execution_sanity,
    write_stage158_outputs,
)


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _write_jsonl(path, records) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(record, sort_keys=True) + "\n" for record in records), encoding="utf-8")


def _sources(tmp_path, *, result_records=None):
    job_shard = tmp_path / "jobs.jsonl"
    provider_results = tmp_path / "provider_job_results.jsonl"
    _write_jsonl(job_shard, [{"job_id": "job_a"}])
    if result_records is not None:
        _write_jsonl(provider_results, result_records)
    command = (
        "python runner.py "
        f"--job-shard {job_shard.as_posix()} --provider-results {provider_results.as_posix()} "
        "--stage111-results stage111.json --stage118-results stage118.json --stage129-results stage129.json "
        "--allow-live-submit --submitter qrope.provider_adapters.ibm_runtime:submit"
    )
    stage133 = tmp_path / "stage133.json"
    stage157 = tmp_path / "stage157.json"
    _write_json(
        stage133,
        {
            "decision": "AUTHORIZED_RUNNER_COMMANDS_PREPARED_EXECUTION_BLOCKED",
            "command_records": [
                {
                    "provider": "ibm_runtime",
                    "window_id": "window_0",
                    "job_count": 1,
                    "command_authorized": True,
                    "live_submit_command_available": True,
                    "live_submit_command": command,
                }
            ],
        },
    )
    _write_json(
        stage157,
        {
            "decision": "FIRST_PROVIDER_LIVE_RUN_APPROVAL_PACKET_READY",
            "first_unlock_provider": "ibm_runtime",
            "approval_phrase_required": "APPROVE IBM RUNTIME STAGE133 LIVE RUN",
            "approval_records": [
                {
                    "provider": "ibm_runtime",
                    "window_id": "window_0",
                    "job_count": 1,
                    "command_authorized": True,
                    "live_submit_command_available": True,
                }
            ],
        },
    )
    return stage133, stage157


def test_stage158_ready_when_approval_matches_and_result_file_empty(tmp_path) -> None:
    stage133, stage157 = _sources(tmp_path)

    result = run_stage158_pre_execution_sanity(stage133_results_path=stage133, stage157_results_path=stage157)

    assert result["decision"] == "FIRST_PROVIDER_PRE_EXECUTION_SANITY_READY_AWAITING_APPROVAL"
    assert result["ready_record_count"] == 1
    assert result["authorized_job_count"] == 1
    assert result["runnable_commands_recorded"] is False
    assert result["pre_execution_records"][0]["ready"] is True


def test_stage158_blocks_when_provider_results_already_contains_records(tmp_path) -> None:
    stage133, stage157 = _sources(tmp_path, result_records=[{"job_id": "job_a"}])

    result = run_stage158_pre_execution_sanity(stage133_results_path=stage133, stage157_results_path=stage157)

    assert result["decision"] == "FIRST_PROVIDER_PRE_EXECUTION_SANITY_BLOCKED"
    assert "pre_execution_record_blockers_present" in result["blockers"]
    assert "provider_results_file_not_empty" in result["pre_execution_records"][0]["blockers"]


def test_stage158_outputs_do_not_record_live_submit_command(tmp_path) -> None:
    stage133, stage157 = _sources(tmp_path)
    result = run_stage158_pre_execution_sanity(stage133_results_path=stage133, stage157_results_path=stage157)

    paths = write_stage158_outputs(result, tmp_path / "out")
    written = (tmp_path / "out" / "results.json").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert "--allow-live-submit" not in written
