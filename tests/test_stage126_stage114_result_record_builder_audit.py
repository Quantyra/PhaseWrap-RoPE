from __future__ import annotations

import json

import pytest

from qrope.provider_adapters.common import ProviderAdapterBlocked, build_stage114_result_record
from qrope.stage126_stage114_result_record_builder_audit import run_stage126_audit, write_stage126_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _write_jsonl(path, records) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(record, sort_keys=True) + "\n" for record in records), encoding="utf-8")


def _plan(provider: str = "ibm_runtime") -> dict:
    return {
        "job_id": "job_0",
        "openqasm3_sha256": "abc",
        "provider": provider,
        "provider_submission_kind": "ibm_runtime_openqasm3_sampler",
        "target_counts_key": "00",
        "window_id": "window_0",
    }


def test_build_stage114_result_record_has_required_fields() -> None:
    record = build_stage114_result_record(
        plan=_plan(),
        job_or_task_id="task_0",
        backend_metadata={"backend": "backend_0"},
        submitted_at_utc="2026-01-01T00:00:00Z",
        completed_at_utc="2026-01-01T00:00:01Z",
        counts={"0b00": 10},
    )

    assert record["job_id"] == "job_0"
    assert record["job_or_task_id"] == "task_0"
    assert record["counts"] == {"00": 10}
    assert record["backend_metadata"]["openqasm3_sha256"] == "abc"


def test_build_stage114_result_record_rejects_bad_timestamp() -> None:
    with pytest.raises(ProviderAdapterBlocked):
        build_stage114_result_record(
            plan=_plan(),
            job_or_task_id="task_0",
            backend_metadata={"backend": "backend_0"},
            submitted_at_utc="not-a-date",
            completed_at_utc="2026-01-01T00:00:01Z",
            counts={"00": 10},
        )


def _fixture(tmp_path):
    schema = tmp_path / "schema.json"
    stage123 = tmp_path / "stage123" / "results.json"
    stage125 = tmp_path / "stage125.json"
    plan_path = tmp_path / "stage123" / "submission_plans" / "ibm_runtime" / "window_0" / "submission_plans.jsonl"
    _write_json(
        schema,
        {
            "required_fields": [
                "job_id",
                "job_or_task_id",
                "backend_metadata",
                "submitted_at_utc",
                "completed_at_utc",
                "counts",
            ]
        },
    )
    _write_json(stage123, {"decision": "PROVIDER_SUBMISSION_PLANS_READY_EXECUTION_BLOCKED"})
    _write_json(stage125, {"decision": "PROVIDER_RESULT_NORMALIZATION_READY_EXECUTION_BLOCKED"})
    _write_jsonl(plan_path, [_plan()])
    return schema, stage123, stage125


def test_stage126_builds_stage114_records_from_plans(tmp_path) -> None:
    schema, stage123, stage125 = _fixture(tmp_path)

    result = run_stage126_audit(stage114_schema_path=schema, stage123_results_path=stage123, stage125_results_path=stage125)

    assert result["decision"] == "STAGE114_RESULT_RECORD_BUILDER_READY_EXECUTION_BLOCKED"
    assert result["ready_provider_window_count"] == 1
    record = next(iter(result["built_records"].values()))
    assert record["job_id"] == "job_0"
    assert record["counts"]


def test_stage126_outputs_are_written(tmp_path) -> None:
    schema, stage123, stage125 = _fixture(tmp_path)
    result = run_stage126_audit(stage114_schema_path=schema, stage123_results_path=stage123, stage125_results_path=stage125)

    paths = write_stage126_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")
    built = tmp_path / "out" / "built_result_records" / "ibm_runtime" / "window_0" / "provider_job_result.record_builder_sample.json"

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert manifest["ready_provider_window_count"] == 1
    assert "window_0" in summary
    assert built.exists()
