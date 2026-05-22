from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from qrope.provider_adapters.amazon_braket import adapter_status as braket_status
from qrope.provider_adapters.amazon_braket import submit as braket_submit
from qrope.provider_adapters.common import ProviderAdapterBlocked
from qrope.provider_adapters.ibm_runtime import adapter_status as ibm_status
from qrope.provider_adapters.ibm_runtime import submit as ibm_submit
from qrope.stage122_provider_adapter_skeleton_audit import run_stage122_audit, write_stage122_outputs


RUNNER_DIR = Path(__file__).resolve().parents[1] / "scripts" / "provider_runners"
sys.path.insert(0, str(RUNNER_DIR))

from runner_guard import run_guarded_provider_runner  # noqa: E402


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _write_jsonl(path, records) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(record, sort_keys=True) + "\n" for record in records), encoding="utf-8")


def test_provider_adapter_statuses_are_non_secret_and_blocked() -> None:
    ibm = ibm_status()
    braket = braket_status()

    assert ibm["provider"] == "ibm_runtime"
    assert braket["provider"] == "amazon_braket"
    assert ibm["submitter_import_path"] == "qrope.provider_adapters.ibm_runtime:submit"
    assert braket["submitter_import_path"] == "qrope.provider_adapters.amazon_braket:submit"
    assert ibm["live_submission_implemented"] is True
    assert braket["live_submission_implemented"] is True
    assert ibm["no_hardware_submission"] is False
    assert braket["no_hardware_submission"] is False
    assert ibm["ready"] is False
    assert braket["ready"] is False


def test_provider_adapter_submitters_fail_closed() -> None:
    with pytest.raises(ProviderAdapterBlocked):
        ibm_submit(provider="ibm_runtime", jobs=[{"job_id": "job_0"}], payloads=[{"job_id": "job_0"}])
    with pytest.raises(ProviderAdapterBlocked):
        braket_submit(provider="amazon_braket", jobs=[{"job_id": "job_0"}], payloads=[{"job_id": "job_0"}])


def test_runner_guard_catches_blocked_provider_adapter_without_writing(tmp_path) -> None:
    job_shard = tmp_path / "jobs.jsonl"
    payloads = tmp_path / "payloads.jsonl"
    results = tmp_path / "results.jsonl"
    stage111 = tmp_path / "stage111.json"
    stage118 = tmp_path / "stage118.json"
    stage129 = tmp_path / "stage129.json"
    _write_jsonl(job_shard, [{"job_id": "job_0", "provider": "ibm_runtime", "window_id": "window_0", "shots": 1000}])
    _write_jsonl(payloads, [{"job_id": "job_0", "provider": "ibm_runtime", "window_id": "window_0", "shots": 1000}])
    _write_json(stage111, {"provider_records": [{"provider": "ibm_runtime", "status": "ready", "blockers": []}]})
    _write_json(stage118, {"payload_records": [{"provider": "ibm_runtime", "window_id": "window_0", "payload_output_path": str(payloads.as_posix())}]})
    _write_json(stage129, {"provider_records": [{"provider": "ibm_runtime", "cutover_authorized": True, "blockers": []}]})

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
            "qrope.provider_adapters.ibm_runtime:submit",
        ],
    )

    assert code == 5
    assert not results.exists()


def test_stage122_reports_adapter_skeletons_ready(tmp_path) -> None:
    _write_json(tmp_path / "stage121.json", {"decision": "PROVIDER_ADAPTER_BRIDGE_READY_PROVIDER_ADAPTERS_REQUIRED"})

    result = run_stage122_audit(stage121_results_path=tmp_path / "stage121.json")

    assert result["decision"] == "PROVIDER_ADAPTER_SKELETONS_READY_EXECUTION_BLOCKED"
    assert result["ready_adapter_count"] == 2
    assert {record["provider"] for record in result["adapter_records"]} == {"amazon_braket", "ibm_runtime"}


def test_stage122_outputs_are_written(tmp_path) -> None:
    _write_json(tmp_path / "stage121.json", {})
    result = run_stage122_audit(stage121_results_path=tmp_path / "stage121.json")

    paths = write_stage122_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert manifest["adapter_count"] == 2
    assert "ibm_runtime" in summary
