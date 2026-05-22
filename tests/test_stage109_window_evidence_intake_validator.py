from __future__ import annotations

import json

from qrope.stage109_window_evidence_intake_validator import run_stage109_intake_validator, write_stage109_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _window_plan(tmp_path, packet_id: str = "packet_alpha") -> dict[str, object]:
    window_dir = tmp_path / "windows" / "provider__window_00"
    template_path = tmp_path / "templates" / f"{packet_id}.json"
    _write_json(
        template_path,
        {
            "packet_id": packet_id,
            "raw_counts_by_row": [
                {"row_id": "hwrow-000", "counts": {}},
                {"row_id": "hwrow-001", "counts": {}},
            ],
        },
    )
    return {
        "window_id": "provider__window_00",
        "provider": "ibm_runtime",
        "window_index": 0,
        "steps": [
            {
                "step_id": "known_state_calibration_execution",
                "output_path": str((window_dir / "calibration" / "ibm_runtime_known_state_execution.json").as_posix()),
            },
            {
                "step_id": "matched_packet_execution",
                "output_dir": str((window_dir / "packet_executions").as_posix()),
                "packet_template_count": 1,
                "packet_templates": [
                    {
                        "packet_id": packet_id,
                        "provider": "ibm_runtime",
                        "encoding_family": "phasewrap",
                        "source_lane_id": "source_alpha",
                        "circuit_template": "two_ry_product_state_z_readout_v1",
                        "row_count": 2,
                        "template_path": str(template_path.as_posix()),
                    }
                ],
            },
        ],
    }


def test_stage109_reports_missing_window_plans(tmp_path) -> None:
    result = run_stage109_intake_validator(stage107_window_plans_path=tmp_path / "missing.json")

    assert result["status"] == "incomplete"
    assert result["decision"] == "WINDOW_EVIDENCE_INTAKE_BLOCKED_EVIDENCE_MISSING"
    assert result["missing_source_artifacts"]


def test_stage109_blocks_current_like_plan_with_missing_evidence(tmp_path) -> None:
    plan = _window_plan(tmp_path)
    _write_json(tmp_path / "window_execution_plans.json", [plan])

    result = run_stage109_intake_validator(stage107_window_plans_path=tmp_path / "window_execution_plans.json")

    assert result["status"] == "completed"
    assert result["ready_window_count"] == 0
    assert result["window_records"][0]["status"] == "missing_evidence"
    assert "calibration_execution_json" in result["window_records"][0]["missing_evidence"]
    assert "packet_execution_json" in result["window_records"][0]["missing_evidence"]


def test_stage109_accepts_synthetic_complete_window_evidence(tmp_path) -> None:
    plan = _window_plan(tmp_path)
    _write_json(tmp_path / "window_execution_plans.json", [plan])
    window_dir = tmp_path / "windows" / "provider__window_00"
    _write_json(window_dir / "calibration" / "ibm_runtime_known_state_execution.json", {"job_or_task_ids": ["job-1"]})
    _write_json(
        window_dir / "calibration" / "stage101" / "results.json",
        {
            "decision": "KNOWN_STATE_CALIBRATION_VERIFIED_READY_FOR_MATCHED_HARDWARE_EXECUTION",
            "known_state_calibration_pass": True,
        },
    )
    _write_json(
        window_dir / "packet_executions" / "packet_alpha.json",
        {
            "job_or_task_ids": ["job-2"],
            "backend_metadata": {"backend": "backend_a"},
            "submitted_at_utc": "2026-05-21T00:00:00Z",
            "completed_at_utc": "2026-05-21T00:10:00Z",
            "raw_counts_by_row": [
                {"row_id": "hwrow-000", "counts": {"00": 900, "01": 100}},
                {"row_id": "hwrow-001", "counts": {"10": 875, "11": 125}},
            ],
        },
    )
    _write_json(window_dir / "stage103" / "results.json", {"ready_to_interpret_hardware_metrics": True})

    result = run_stage109_intake_validator(stage107_window_plans_path=tmp_path / "window_execution_plans.json")

    assert result["decision"] == "WINDOW_EVIDENCE_INTAKE_READY_FOR_STAGE105_AGGREGATION"
    assert result["ready_window_count"] == 1
    assert result["window_records"][0]["ready_packet_count"] == 1


def test_stage109_outputs_are_written(tmp_path) -> None:
    plan = _window_plan(tmp_path)
    _write_json(tmp_path / "window_execution_plans.json", [plan])
    result = run_stage109_intake_validator(stage107_window_plans_path=tmp_path / "window_execution_plans.json")

    paths = write_stage109_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert manifest["window_count"] == 1
    assert "provider__window_00" in summary
