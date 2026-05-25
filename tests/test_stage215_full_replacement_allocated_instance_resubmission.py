from __future__ import annotations

import json

from qrope.stage215_full_replacement_allocated_instance_resubmission import (
    run_stage215_full_replacement_allocated_instance_resubmission,
    write_stage215_outputs,
)


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _template(index: int) -> dict:
    return {
        "template_type": "replacement_packet_execution_counts",
        "packet_id": f"p{index}",
        "source_lane_id": "lane",
        "encoding_family": "phasewrap",
        "circuit_template": "two_ry_product_state_z_readout_v1",
        "shot_count": 4096,
        "raw_counts_by_row": [{"row_id": "r0", "openqasm3": "OPENQASM 3.0;\nqubit[2] q;\nbit[2] c;\n"}],
    }


def _sources(tmp_path):
    stage190 = tmp_path / "stage190.json"
    stage212 = tmp_path / "stage212.json"
    stage213 = tmp_path / "stage213.json"
    templates = [_template(index) for index in range(20)]
    calibration = {
        "template_type": "replacement_known_state_calibration_counts",
        "shots_per_state": 1000,
        "raw_counts_by_state": [{"state": state, "openqasm3": "OPENQASM 3.0;\nqubit[2] q;\nbit[2] c;\n"} for state in ("00", "01")],
    }
    records = [
        {
            "template_type": "replacement_packet_execution_counts",
            "packet_id": f"p{index}",
            "runtime_job_id": f"old-{index}",
            "submitted_at_utc": "t0",
            "backend_metadata": {"backend": "ibm_fez"},
            "status": "submitted_awaiting_results",
        }
        for index in range(20)
    ]
    records.append(
        {
            "template_type": "replacement_known_state_calibration_counts",
            "packet_id": "",
            "runtime_job_id": "old-cal",
            "submitted_at_utc": "t0",
            "backend_metadata": {"backend": "ibm_fez"},
            "status": "submitted_awaiting_results",
        }
    )
    poll_records = [
        {
            "template_type": record["template_type"],
            "packet_id": record["packet_id"],
            "runtime_job_id": record["runtime_job_id"],
            "status": "DONE" if index < 13 else "QUEUED",
        }
        for index, record in enumerate(records)
    ]
    _write_json(stage190, {"estimated_total_job_count": 324, "estimated_total_shots": 1314720, "execution_templates": templates, "calibration_template": calibration})
    _write_json(stage212, {"decision": "FULL_REPLACEMENT_HARDWARE_SUBMITTED_AWAITING_RESULTS", "backend": "ibm_fez", "budget_cap_usd": 250.0, "submission_records": records})
    _write_json(stage213, {"poll_records": poll_records})
    return stage190, stage212, stage213


def test_stage215_resubmits_only_pending_and_preserves_done_records(tmp_path) -> None:
    stage190, stage212, stage213 = _sources(tmp_path)

    def fake_submit(*, template, backend_name):
        key = template.get("packet_id") or "calibration"
        return {"runtime_job_id": f"new-{key}", "submitted_at_utc": "t1", "backend_metadata": {"backend": backend_name, "provider": "ibm_runtime"}}

    result = run_stage215_full_replacement_allocated_instance_resubmission(
        stage212_results_path=stage212,
        stage213_results_path=stage213,
        stage190_results_path=stage190,
        allow_live_submit=True,
        submit_template=fake_submit,
    )

    assert result["decision"] == "FULL_REPLACEMENT_HARDWARE_SUBMITTED_AWAITING_RESULTS"
    assert result["submitted_replacement_runtime_job_count"] == 8
    assert result["submission_records"][0]["runtime_job_id"] == "old-0"
    assert result["submission_records"][13]["runtime_job_id"] == "new-p13"
    assert result["replacement_records"][0]["superseded_runtime_job_id"] == "old-13"
    assert result["secret_values_recorded"] is False


def test_stage215_blocks_without_live_flag(tmp_path) -> None:
    stage190, stage212, stage213 = _sources(tmp_path)

    result = run_stage215_full_replacement_allocated_instance_resubmission(
        stage212_results_path=stage212,
        stage213_results_path=stage213,
        stage190_results_path=stage190,
    )

    assert result["replacement_decision"] == "FULL_REPLACEMENT_ALLOCATED_INSTANCE_RESUBMISSION_BLOCKED_OR_PARTIAL"
    assert "allow_live_submit_flag_required" in result["blockers"]


def test_stage215_outputs_do_not_record_secrets_or_live_command(tmp_path) -> None:
    stage190, stage212, stage213 = _sources(tmp_path)
    result = run_stage215_full_replacement_allocated_instance_resubmission(
        stage212_results_path=stage212,
        stage213_results_path=stage213,
        stage190_results_path=stage190,
    )
    write_stage215_outputs(result, tmp_path / "out")
    written = "\n".join(
        [
            (tmp_path / "out" / "results.json").read_text(encoding="utf-8"),
            (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8"),
        ]
    )

    assert "IBM_QUANTUM_TOKEN" not in written
    assert "QISKIT_IBM_TOKEN" not in written
    assert "crn:v1" not in written
    assert "--allow-live-submit" not in written
