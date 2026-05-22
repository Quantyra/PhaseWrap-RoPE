from __future__ import annotations

import json
from pathlib import Path

from qrope.stage119_provider_result_rehearsal_audit import run_stage119_audit, write_stage119_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _write_jsonl(path, records) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(record, sort_keys=True) + "\n" for record in records), encoding="utf-8")


def _fixture(tmp_path):
    payload_path = tmp_path / "payloads" / "submission_payloads.jsonl"
    _write_jsonl(
        payload_path,
        [
            {
                "dry_run_only": True,
                "job_id": "job_cal",
                "job_kind": "known_state_calibration",
                "openqasm3_sha256": "abc",
                "provider": "ibm_runtime",
                "provider_submission_kind": "ibm_runtime_openqasm3_sampler",
                "shots": 1000,
                "target_counts_key": "01",
                "window_id": "window_0",
            },
            {
                "dry_run_only": True,
                "job_id": "job_packet",
                "job_kind": "matched_packet_row",
                "openqasm3_sha256": "def",
                "provider": "ibm_runtime",
                "provider_submission_kind": "ibm_runtime_openqasm3_sampler",
                "shots": 4096,
                "target_counts_key": "hwrow-000",
                "window_id": "window_0",
            },
        ],
    )
    _write_json(
        tmp_path / "stage118.json",
        {
            "decision": "PROVIDER_PAYLOAD_DRY_RUN_COMPILED_EXECUTION_BLOCKED",
            "payload_records": [
                {
                    "provider": "ibm_runtime",
                    "window_id": "window_0",
                    "compiled_payload_count": 2,
                    "payload_output_path": str(payload_path.as_posix()),
                }
            ],
        },
    )
    _write_json(
        tmp_path / "schema.json",
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
    return tmp_path / "stage118.json", tmp_path / "schema.json"


def test_stage119_reports_missing_sources() -> None:
    result = run_stage119_audit(stage118_results_path=Path("missing118.json"), stage114_schema_path=Path("missing_schema.json"))

    assert result["status"] == "incomplete"
    assert result["decision"] == "PROVIDER_RESULT_REHEARSAL_INCOMPLETE"
    assert result["rehearsal_record_count"] == 0


def test_stage119_rehearses_stage114_result_shape(tmp_path) -> None:
    stage118, schema = _fixture(tmp_path)

    result = run_stage119_audit(stage118_results_path=stage118, stage114_schema_path=schema, output_dir=tmp_path / "out")

    assert result["decision"] == "PROVIDER_RESULT_REHEARSAL_READY_EXECUTION_BLOCKED"
    assert result["rehearsal_record_count"] == 2
    assert result["invalid_rehearsal_record_count"] == 0
    records = next(iter(result["rehearsals_by_path"].values()))
    assert records[0]["dry_run_only"] is True
    assert records[0]["not_hardware_evidence"] is True
    assert records[0]["counts"] == {"01": 1000}
    assert records[1]["counts"] == {"00": 4096}


def test_stage119_outputs_are_written(tmp_path) -> None:
    stage118, schema = _fixture(tmp_path)
    result = run_stage119_audit(stage118_results_path=stage118, stage114_schema_path=schema, output_dir=tmp_path / "out")

    paths = write_stage119_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")
    rehearsal_file = tmp_path / "out" / "rehearsal_results" / "ibm_runtime" / "window_0" / "provider_job_results.rehearsal.jsonl"

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert manifest["rehearsal_record_count"] == 2
    assert "window_0" in summary
    assert rehearsal_file.exists()
    assert len(rehearsal_file.read_text(encoding="utf-8").splitlines()) == 2
