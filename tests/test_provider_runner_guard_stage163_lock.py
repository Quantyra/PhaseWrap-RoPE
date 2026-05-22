from __future__ import annotations

import hashlib
import json

from scripts.provider_runners.runner_guard import run_guarded_provider_runner


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _write_jsonl(path, records) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(record, sort_keys=True) + "\n" for record in records), encoding="utf-8")


def _sha256(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fixture(tmp_path):
    window_id = "ibm_runtime__independent_window_00"
    job_shard = tmp_path / "jobs.jsonl"
    provider_results = tmp_path / "provider_job_results.jsonl"
    payloads = tmp_path / "payloads.jsonl"
    jobs = [
        {"job_id": "job_0", "window_id": window_id, "job_kind": "experiment"},
        {"job_id": "job_1", "window_id": window_id, "job_kind": "calibration"},
    ]
    _write_jsonl(job_shard, jobs)
    _write_jsonl(payloads, [{"job_id": "job_0"}, {"job_id": "job_1"}])
    stage111 = tmp_path / "stage111.json"
    stage118 = tmp_path / "stage118.json"
    stage129 = tmp_path / "stage129.json"
    stage163 = tmp_path / "stage163.json"
    _write_json(stage111, {"provider_records": [{"provider": "ibm_runtime", "status": "ready", "blockers": []}]})
    _write_json(
        stage118,
        {
            "payload_records": [
                {
                    "provider": "ibm_runtime",
                    "window_id": window_id,
                    "payload_output_path": payloads.as_posix(),
                }
            ]
        },
    )
    _write_json(
        stage129,
        {
            "provider_records": [
                {
                    "provider": "ibm_runtime",
                    "cutover_authorized": True,
                    "blockers": [],
                }
            ]
        },
    )
    _write_json(
        stage163,
        {
            "decision": "FIRST_PROVIDER_PRERUN_LOCK_READY_AWAITING_APPROVAL",
            "first_unlock_provider": "ibm_runtime",
            "window_locks": [
                {
                    "provider": "ibm_runtime",
                    "window_id": window_id,
                    "ready": True,
                    "job_shard_path": job_shard.as_posix(),
                    "provider_results_path": provider_results.as_posix(),
                    "job_shard_sha256": _sha256(job_shard),
                    "job_count": len(jobs),
                }
            ],
        },
    )
    return {
        "jobs": jobs,
        "job_shard": job_shard,
        "provider_results": provider_results,
        "stage111": stage111,
        "stage118": stage118,
        "stage129": stage129,
        "stage163": stage163,
    }


def _argv(fixture, *extra):
    return [
        "--job-shard",
        fixture["job_shard"].as_posix(),
        "--provider-results",
        fixture["provider_results"].as_posix(),
        "--stage111-results",
        fixture["stage111"].as_posix(),
        "--stage118-results",
        fixture["stage118"].as_posix(),
        "--stage129-results",
        fixture["stage129"].as_posix(),
        "--stage163-results",
        fixture["stage163"].as_posix(),
        *extra,
    ]


def test_ibm_runner_validates_stage163_lock_before_live_flag(tmp_path, capsys) -> None:
    fixture = _fixture(tmp_path)

    rc = run_guarded_provider_runner("ibm_runtime", _argv(fixture))

    assert rc == 3
    assert "decision: PROVIDER_RUNNER_READY_LIVE_SUBMIT_FLAG_REQUIRED" in capsys.readouterr().out
    assert not fixture["provider_results"].exists()


def test_ibm_runner_blocks_live_submit_when_stage163_hash_mismatches(tmp_path, capsys) -> None:
    fixture = _fixture(tmp_path)
    _write_jsonl(fixture["job_shard"], fixture["jobs"] + [{"job_id": "job_2", "window_id": "ibm_runtime__independent_window_00", "job_kind": "experiment"}])

    rc = run_guarded_provider_runner("ibm_runtime", _argv(fixture, "--allow-live-submit"), submitter=lambda **_: [])

    output = capsys.readouterr().out
    assert rc == 4
    assert "decision: PROVIDER_RUNNER_BLOCKED_STAGE163_PRERUN_LOCK_MISMATCH" in output
    assert "stage163_job_shard_hash_mismatch" in output
    assert not fixture["provider_results"].exists()


def test_ibm_runner_writes_results_after_valid_stage163_lock(tmp_path, capsys) -> None:
    fixture = _fixture(tmp_path)

    def submitter(*, provider, jobs, payloads, cutover_authorized):
        assert provider == "ibm_runtime"
        assert len(payloads) == len(jobs)
        assert cutover_authorized is True
        return [
            {
                "job_id": job["job_id"],
                "job_or_task_id": f"provider_{job['job_id']}",
                "backend_metadata": {
                    "provider": provider,
                    "backend": "ibm_fez",
                    "window_id": job["window_id"],
                    "job_kind": job["job_kind"],
                },
                "submitted_at_utc": "2026-05-22T00:00:00Z",
                "completed_at_utc": "2026-05-22T00:01:00Z",
                "counts": {"0": 1},
            }
            for job in jobs
        ]

    rc = run_guarded_provider_runner("ibm_runtime", _argv(fixture, "--allow-live-submit"), submitter=submitter)

    assert rc == 0
    assert "decision: PROVIDER_RUNNER_RESULTS_WRITTEN" in capsys.readouterr().out
    assert len(fixture["provider_results"].read_text(encoding="utf-8").splitlines()) == 2
