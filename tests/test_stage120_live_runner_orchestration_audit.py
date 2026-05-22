from __future__ import annotations

import json
import sys
from pathlib import Path

from qrope.stage120_live_runner_orchestration_audit import run_stage120_audit, write_stage120_outputs


RUNNER_DIR = Path(__file__).resolve().parents[1] / "scripts" / "provider_runners"
sys.path.insert(0, str(RUNNER_DIR))

from runner_guard import run_guarded_provider_runner  # noqa: E402


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _write_jsonl(path, records) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(record, sort_keys=True) + "\n" for record in records), encoding="utf-8")


def _runner_fixture(tmp_path):
    job_shard = tmp_path / "jobs.jsonl"
    payloads = tmp_path / "payloads.jsonl"
    results = tmp_path / "results.jsonl"
    stage111 = tmp_path / "stage111.json"
    stage118 = tmp_path / "stage118.json"
    stage129 = tmp_path / "stage129.json"
    jobs = [
        {
            "job_id": "job_0",
            "job_kind": "known_state_calibration",
            "openqasm3": "OPENQASM 3.0;\n",
            "provider": "ibm_runtime",
            "shots": 1000,
            "window_id": "window_0",
        }
    ]
    _write_jsonl(job_shard, jobs)
    _write_jsonl(
        payloads,
        [
            {
                "job_id": "job_0",
                "provider": "ibm_runtime",
                "shots": 1000,
                "window_id": "window_0",
            }
        ],
    )
    _write_json(
        stage111,
        {
            "provider_records": [
                {
                    "provider": "ibm_runtime",
                    "status": "ready",
                    "blockers": [],
                }
            ]
        },
    )
    _write_json(
        stage118,
        {
            "payload_records": [
                {
                    "provider": "ibm_runtime",
                    "window_id": "window_0",
                    "payload_output_path": str(payloads.as_posix()),
                    "compiled_payload_count": 1,
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
    return job_shard, results, stage111, stage118, stage129


def test_runner_guard_writes_results_with_injected_submitter(tmp_path) -> None:
    job_shard, results, stage111, stage118, stage129 = _runner_fixture(tmp_path)

    def submitter(*, provider, jobs, payloads):
        assert provider == "ibm_runtime"
        assert len(jobs) == 1
        assert len(payloads) == 1
        return [
            {
                "job_id": "job_0",
                "job_or_task_id": "task_0",
                "backend_metadata": {"provider": provider},
                "submitted_at_utc": "2026-01-01T00:00:00Z",
                "completed_at_utc": "2026-01-01T00:00:01Z",
                "counts": {"00": 1000},
            }
        ]

    code = run_guarded_provider_runner(
        "ibm_runtime",
        [
            "--job-shard",
            str(job_shard),
            "--provider-results",
            str(results),
            "--stage111-results",
            str(stage111),
            "--stage118-results",
            str(stage118),
            "--stage129-results",
            str(stage129),
            "--allow-live-submit",
        ],
        submitter=submitter,
    )

    assert code == 0
    assert results.exists()
    assert json.loads(results.read_text(encoding="utf-8").strip())["job_id"] == "job_0"


def test_runner_guard_rejects_invalid_submitter_results(tmp_path) -> None:
    job_shard, results, stage111, stage118, stage129 = _runner_fixture(tmp_path)

    code = run_guarded_provider_runner(
        "ibm_runtime",
        [
            "--job-shard",
            str(job_shard),
            "--provider-results",
            str(results),
            "--stage111-results",
            str(stage111),
            "--stage118-results",
            str(stage118),
            "--stage129-results",
            str(stage129),
            "--allow-live-submit",
        ],
        submitter=lambda **_: [{"job_id": "unknown", "counts": {}}],
    )

    assert code == 5
    assert not results.exists()


def test_runner_guard_requires_stage129_cutover_authorization(tmp_path) -> None:
    job_shard, results, stage111, stage118, stage129 = _runner_fixture(tmp_path)
    _write_json(stage129, {"provider_records": [{"provider": "ibm_runtime", "cutover_authorized": False, "blockers": ["stage106:not_ready"]}]})

    code = run_guarded_provider_runner(
        "ibm_runtime",
        [
            "--job-shard",
            str(job_shard),
            "--provider-results",
            str(results),
            "--stage111-results",
            str(stage111),
            "--stage118-results",
            str(stage118),
            "--stage129-results",
            str(stage129),
            "--allow-live-submit",
        ],
        submitter=lambda **_: [],
    )

    assert code == 4
    assert not results.exists()


def test_stage120_reports_runner_orchestration_ready(tmp_path) -> None:
    _write_json(
        tmp_path / "stage116.json",
        {
            "decision": "PROVIDER_RUNNER_PLAN_PREPARED_EXECUTION_BLOCKED",
            "runner_records": [
                {
                    "provider": "ibm_runtime",
                    "window_id": "window_0",
                    "status": "blocked",
                    "job_count": 1,
                    "runner_command": "python scripts/provider_runners/run_ibm_runtime_stage112_jobs.py --job-shard jobs.jsonl --provider-results results.jsonl",
                }
            ],
        },
    )
    _write_json(tmp_path / "stage118.json", {"decision": "PROVIDER_PAYLOAD_DRY_RUN_COMPILED_EXECUTION_BLOCKED"})
    _write_json(tmp_path / "stage119.json", {"decision": "PROVIDER_RESULT_REHEARSAL_READY_EXECUTION_BLOCKED"})

    result = run_stage120_audit(
        stage116_results_path=tmp_path / "stage116.json",
        stage118_results_path=tmp_path / "stage118.json",
        stage119_results_path=tmp_path / "stage119.json",
    )

    assert result["decision"] == "LIVE_RUNNER_ORCHESTRATION_READY_ADAPTER_REQUIRED"
    assert result["ready_runner_count"] == 1
    assert result["runner_records"][0]["accepts_stage129_results"] is True


def test_stage120_outputs_are_written(tmp_path) -> None:
    _write_json(
        tmp_path / "stage116.json",
        {
            "runner_records": [
                {
                    "provider": "ibm_runtime",
                    "window_id": "window_0",
                    "status": "blocked",
                    "job_count": 1,
                    "runner_command": "python scripts/provider_runners/run_ibm_runtime_stage112_jobs.py --job-shard jobs.jsonl --provider-results results.jsonl",
                }
            ]
        },
    )
    _write_json(tmp_path / "stage118.json", {})
    _write_json(tmp_path / "stage119.json", {})
    result = run_stage120_audit(
        stage116_results_path=tmp_path / "stage116.json",
        stage118_results_path=tmp_path / "stage118.json",
        stage119_results_path=tmp_path / "stage119.json",
    )

    paths = write_stage120_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert manifest["runner_count"] == 1
    assert "window_0" in summary
