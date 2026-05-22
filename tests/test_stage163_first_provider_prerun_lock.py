from __future__ import annotations

import json

from qrope.stage163_first_provider_prerun_lock import run_stage163_prerun_lock, write_stage163_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _write_jsonl(path, records) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(record, sort_keys=True) + "\n" for record in records), encoding="utf-8")


def _sources(tmp_path, *, result_records=None):
    stage157 = tmp_path / "stage157.json"
    stage162 = tmp_path / "stage162.json"
    stage114 = tmp_path / "stage114"
    window_id = "ibm_runtime__independent_window_00"
    _write_json(
        stage157,
        {
            "decision": "FIRST_PROVIDER_LIVE_RUN_APPROVAL_PACKET_READY",
            "first_unlock_provider": "ibm_runtime",
            "approval_phrase_required": "APPROVE IBM RUNTIME STAGE133 LIVE RUN",
            "approval_records": [
                {
                    "provider": "ibm_runtime",
                    "window_id": window_id,
                    "job_count": 2,
                    "command_authorized": True,
                    "live_submit_command_available": True,
                }
            ],
        },
    )
    _write_json(
        stage162,
        {
            "decision": "FIRST_PROVIDER_APPROVAL_DOSSIER_READY_FOR_HUMAN_GO_NO_GO",
            "authorized_first_provider_job_count": 2,
        },
    )
    _write_jsonl(
        stage114 / "job_shards" / "ibm_runtime" / window_id / "jobs.jsonl",
        [
            {"job_id": "job_a", "provider": "ibm_runtime", "shots": 1000, "window_id": window_id},
            {"job_id": "job_b", "provider": "ibm_runtime", "shots": 4096, "window_id": window_id},
        ],
    )
    if result_records is not None:
        _write_jsonl(stage114 / "provider_results" / "ibm_runtime" / window_id / "provider_job_results.jsonl", result_records)
    return stage157, stage162, stage114


def test_stage163_locks_job_shard_hashes_when_results_are_empty(tmp_path) -> None:
    stage157, stage162, stage114 = _sources(tmp_path)

    result = run_stage163_prerun_lock(
        stage157_results_path=stage157,
        stage162_results_path=stage162,
        stage114_output_dir=stage114,
    )

    assert result["decision"] == "FIRST_PROVIDER_PRERUN_LOCK_READY_AWAITING_APPROVAL"
    assert result["locked_job_count"] == 2
    assert result["locked_total_shots"] == 5096
    assert len(result["window_locks"][0]["job_shard_sha256"]) == 64
    assert len(result["aggregate_job_shard_lock_sha256"]) == 64
    assert result["runnable_commands_recorded"] is False


def test_stage163_blocks_when_result_file_already_has_records(tmp_path) -> None:
    stage157, stage162, stage114 = _sources(tmp_path, result_records=[{"job_id": "job_a"}])

    result = run_stage163_prerun_lock(
        stage157_results_path=stage157,
        stage162_results_path=stage162,
        stage114_output_dir=stage114,
    )

    assert result["decision"] == "FIRST_PROVIDER_PRERUN_LOCK_BLOCKED"
    assert "window_lock_blockers_present" in result["blockers"]
    assert "provider_results_not_empty" in result["window_locks"][0]["blockers"]


def test_stage163_outputs_do_not_record_live_commands_or_secrets(tmp_path) -> None:
    stage157, stage162, stage114 = _sources(tmp_path)
    result = run_stage163_prerun_lock(
        stage157_results_path=stage157,
        stage162_results_path=stage162,
        stage114_output_dir=stage114,
    )

    paths = write_stage163_outputs(result, tmp_path / "out")
    written = (tmp_path / "out" / "results.json").read_text(encoding="utf-8")
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert "--allow-live-submit" not in written
    assert "--allow-live-submit" not in summary
    assert "IBM_QUANTUM_TOKEN" not in written
    assert "crn:v1" not in written
