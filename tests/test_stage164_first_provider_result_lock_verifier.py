from __future__ import annotations

import hashlib
import json

from qrope.stage164_first_provider_result_lock_verifier import run_stage164_result_lock_verifier, write_stage164_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _write_jsonl(path, records) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(record, sort_keys=True) + "\n" for record in records), encoding="utf-8")


def _sha(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _result(job_id):
    return {
        "job_id": job_id,
        "job_or_task_id": f"task-{job_id}",
        "backend_metadata": {"backend": "ibm_test"},
        "submitted_at_utc": "2026-05-22T00:00:00Z",
        "completed_at_utc": "2026-05-22T00:01:00Z",
        "counts": {"00": 10},
    }


def _stage163(tmp_path, *, write_results=False, tamper_hash=False):
    shard = tmp_path / "jobs.jsonl"
    results = tmp_path / "provider_job_results.jsonl"
    _write_jsonl(shard, [{"job_id": "job_a"}, {"job_id": "job_b"}])
    if write_results:
        _write_jsonl(results, [_result("job_a"), _result("job_b")])
    expected_hash = "0" * 64 if tamper_hash else _sha(shard)
    path = tmp_path / "stage163.json"
    _write_json(
        path,
        {
            "decision": "FIRST_PROVIDER_PRERUN_LOCK_READY_AWAITING_APPROVAL",
            "first_unlock_provider": "ibm_runtime",
            "aggregate_job_shard_lock_sha256": expected_hash,
            "window_locks": [
                {
                    "provider": "ibm_runtime",
                    "window_id": "window_0",
                    "job_count": 2,
                    "job_shard_path": str(shard.as_posix()),
                    "job_shard_sha256": expected_hash,
                    "provider_results_path": str(results.as_posix()),
                }
            ],
        },
    )
    return path


def test_stage164_verifies_complete_results_against_lock(tmp_path) -> None:
    stage163 = _stage163(tmp_path, write_results=True)

    result = run_stage164_result_lock_verifier(stage163_results_path=stage163)

    assert result["decision"] == "FIRST_PROVIDER_RESULT_LOCK_VERIFIED_READY_FOR_STAGE115"
    assert result["hash_match_count"] == 1
    assert result["provider_result_record_count"] == 2
    assert result["missing_result_record_count"] == 0


def test_stage164_blocks_until_results_exist(tmp_path) -> None:
    stage163 = _stage163(tmp_path, write_results=False)

    result = run_stage164_result_lock_verifier(stage163_results_path=stage163)

    assert result["decision"] == "FIRST_PROVIDER_RESULT_LOCK_VERIFICATION_BLOCKED_RESULTS_MISSING"
    assert result["missing_result_record_count"] == 2
    assert "window_result_lock_verification_blockers_present" in result["blockers"]
    assert "provider_results_missing" in result["window_verifications"][0]["blockers"]


def test_stage164_blocks_on_hash_mismatch(tmp_path) -> None:
    stage163 = _stage163(tmp_path, write_results=True, tamper_hash=True)

    result = run_stage164_result_lock_verifier(stage163_results_path=stage163)

    assert result["decision"] == "FIRST_PROVIDER_RESULT_LOCK_VERIFICATION_BLOCKED"
    assert "job_shard_hash_mismatch" in result["window_verifications"][0]["blockers"]


def test_stage164_outputs_do_not_record_secrets_or_live_commands(tmp_path) -> None:
    stage163 = _stage163(tmp_path, write_results=False)
    result = run_stage164_result_lock_verifier(stage163_results_path=stage163)

    paths = write_stage164_outputs(result, tmp_path / "out")
    written = (tmp_path / "out" / "results.json").read_text(encoding="utf-8")
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert "--allow-live-submit" not in written
    assert "--allow-live-submit" not in summary
    assert "IBM_QUANTUM_TOKEN" not in written
    assert "crn:v1" not in written
