from __future__ import annotations

import json

import pytest

from qrope.provider_adapters.amazon_braket import build_submission_plan as build_braket_plan
from qrope.provider_adapters.common import ProviderAdapterBlocked
from qrope.provider_adapters.ibm_runtime import build_submission_plan as build_ibm_plan
from qrope.stage123_provider_submission_plan_audit import run_stage123_audit, write_stage123_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _write_jsonl(path, records) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(record, sort_keys=True) + "\n" for record in records), encoding="utf-8")


def _job_and_payload(provider: str):
    job = {
        "job_id": "job_0",
        "job_kind": "known_state_calibration",
        "provider": provider,
        "shots": 1000,
        "window_id": "window_0",
    }
    payload = {
        "job_id": "job_0",
        "openqasm3": "OPENQASM 3.0;\n",
        "openqasm3_sha256": "abc",
        "provider": provider,
        "shots": 1000,
        "target_counts_key": "00",
        "window_id": "window_0",
    }
    return job, payload


def test_provider_submission_plan_builders_preserve_contract_fields() -> None:
    ibm_job, ibm_payload = _job_and_payload("ibm_runtime")
    braket_job, braket_payload = _job_and_payload("amazon_braket")

    ibm_plan = build_ibm_plan(jobs=[ibm_job], payloads=[ibm_payload])[0]
    braket_plan = build_braket_plan(jobs=[braket_job], payloads=[braket_payload])[0]

    assert ibm_plan["provider_submission_kind"] == "ibm_runtime_openqasm3_sampler"
    assert braket_plan["provider_submission_kind"] == "amazon_braket_openqasm3_task"
    assert ibm_plan["openqasm3_sha256"] == "abc"
    assert braket_plan["openqasm3_sha256"] == "abc"
    assert ibm_plan["no_hardware_submission"] is True
    assert braket_plan["no_hardware_submission"] is True
    assert "counts" in ibm_plan["expected_result_fields"]
    assert "counts" in braket_plan["expected_result_fields"]


def test_provider_submission_plan_builders_reject_id_mismatch() -> None:
    job, payload = _job_and_payload("ibm_runtime")
    payload["job_id"] = "other"

    with pytest.raises(ProviderAdapterBlocked):
        build_ibm_plan(jobs=[job], payloads=[payload])


def _fixture(tmp_path):
    payload_path = (
        tmp_path
        / "logs"
        / "automated_stage_gates"
        / "stage118_provider_payload_dry_run_audit"
        / "dry_run_payloads"
        / "ibm_runtime"
        / "window_0"
        / "submission_payloads.jsonl"
    )
    job_path = (
        tmp_path
        / "logs"
        / "automated_stage_gates"
        / "stage114_provider_result_capture_contract"
        / "job_shards"
        / "ibm_runtime"
        / "window_0"
        / "jobs.jsonl"
    )
    job, payload = _job_and_payload("ibm_runtime")
    _write_jsonl(job_path, [job])
    _write_jsonl(payload_path, [payload])
    _write_json(
        tmp_path / "stage118.json",
        {
            "decision": "PROVIDER_PAYLOAD_DRY_RUN_COMPILED_EXECUTION_BLOCKED",
            "payload_records": [
                {
                    "provider": "ibm_runtime",
                    "window_id": "window_0",
                    "payload_output_path": str(payload_path.as_posix()),
                    "compiled_payload_count": 1,
                }
            ],
        },
    )
    _write_json(tmp_path / "stage122.json", {"decision": "PROVIDER_ADAPTER_SKELETONS_READY_EXECUTION_BLOCKED"})
    return tmp_path / "stage118.json", tmp_path / "stage122.json"


def test_stage123_builds_submission_plans_from_stage118_payloads(tmp_path) -> None:
    stage118, stage122 = _fixture(tmp_path)

    result = run_stage123_audit(stage118_results_path=stage118, stage122_results_path=stage122)

    assert result["decision"] == "PROVIDER_SUBMISSION_PLANS_READY_EXECUTION_BLOCKED"
    assert result["submission_plan_count"] == 1
    assert result["ready_plan_record_count"] == 1
    plans = next(iter(result["plans_by_window"].values()))
    assert plans[0]["job_id"] == "job_0"


def test_stage123_outputs_are_written(tmp_path) -> None:
    stage118, stage122 = _fixture(tmp_path)
    result = run_stage123_audit(stage118_results_path=stage118, stage122_results_path=stage122)

    paths = write_stage123_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")
    plan_file = tmp_path / "out" / "submission_plans" / "ibm_runtime" / "window_0" / "submission_plans.jsonl"

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert manifest["submission_plan_count"] == 1
    assert "window_0" in summary
    assert plan_file.exists()
