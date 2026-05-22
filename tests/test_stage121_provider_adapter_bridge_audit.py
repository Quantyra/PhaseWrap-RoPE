from __future__ import annotations

import json
import sys
from pathlib import Path

from qrope.stage121_provider_adapter_bridge_audit import run_stage121_audit, write_stage121_outputs


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
    _write_jsonl(
        job_shard,
        [{"job_id": "job_0", "job_kind": "known_state_calibration", "provider": "ibm_runtime", "shots": 1000, "window_id": "window_0"}],
    )
    _write_jsonl(payloads, [{"job_id": "job_0", "provider": "ibm_runtime", "shots": 1000, "window_id": "window_0"}])
    _write_json(stage111, {"provider_records": [{"provider": "ibm_runtime", "status": "ready", "blockers": []}]})
    _write_json(
        stage118,
        {"payload_records": [{"provider": "ibm_runtime", "window_id": "window_0", "payload_output_path": str(payloads.as_posix()), "compiled_payload_count": 1}]},
    )
    _write_json(stage129, {"provider_records": [{"provider": "ibm_runtime", "cutover_authorized": True, "blockers": []}]})
    return job_shard, results, stage111, stage118, stage129


def test_runner_guard_loads_submitter_import_path(tmp_path, monkeypatch) -> None:
    module_path = tmp_path / "fake_adapter.py"
    module_path.write_text(
        "\n".join(
            [
                "def submit(*, provider, jobs, payloads):",
                "    return [{'job_id': jobs[0]['job_id'], 'job_or_task_id': 'task_0', 'backend_metadata': {'provider': provider}, 'submitted_at_utc': '2026-01-01T00:00:00Z', 'completed_at_utc': '2026-01-01T00:00:01Z', 'counts': {'00': 1000}}]",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_path))
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
            "--submitter",
            "fake_adapter:submit",
        ],
    )

    assert code == 0
    assert json.loads(results.read_text(encoding="utf-8").strip())["job_or_task_id"] == "task_0"


def test_runner_guard_rejects_missing_submitter_import_path(tmp_path) -> None:
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
            "--submitter",
            "missing_adapter:submit",
        ],
    )

    assert code == 4
    assert not results.exists()


def test_stage121_reports_adapter_bridge_ready(tmp_path) -> None:
    _write_json(
        tmp_path / "stage120.json",
        {
            "decision": "LIVE_RUNNER_ORCHESTRATION_READY_ADAPTER_REQUIRED",
            "runner_records": [
                {
                    "provider": "ibm_runtime",
                    "window_id": "window_0",
                    "runner_script": "scripts/provider_runners/run_ibm_runtime_stage112_jobs.py",
                }
            ],
        },
    )

    result = run_stage121_audit(stage120_results_path=tmp_path / "stage120.json")

    assert result["decision"] == "PROVIDER_ADAPTER_BRIDGE_READY_PROVIDER_ADAPTERS_REQUIRED"
    assert result["ready_runner_count"] == 1
    assert result["runner_records"][0]["accepts_stage129_results"] is True
    assert result["runner_records"][0]["accepts_submitter_import_path"] is True


def test_stage121_outputs_are_written(tmp_path) -> None:
    _write_json(
        tmp_path / "stage120.json",
        {
            "runner_records": [
                {
                    "provider": "ibm_runtime",
                    "window_id": "window_0",
                    "runner_script": "scripts/provider_runners/run_ibm_runtime_stage112_jobs.py",
                }
            ]
        },
    )
    result = run_stage121_audit(stage120_results_path=tmp_path / "stage120.json")

    paths = write_stage121_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert manifest["runner_count"] == 1
    assert "window_0" in summary
