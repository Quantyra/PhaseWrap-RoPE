from __future__ import annotations

import json

from qrope.stage203_reduced_scope_execution_package import run_stage203_reduced_scope_execution_package, write_stage203_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _template(lane: str, family: str) -> dict:
    template = "two_ry_cx_parity_z_readout_v1" if "_cx_" in lane else "two_ry_product_state_z_readout_v1"
    return {
        "schema_version": "qrope_stage190_replacement_execution_package_v1",
        "template_type": "replacement_packet_execution_counts",
        "packet_id": f"{lane}__sem__{family}",
        "packet_hash": f"hash-{lane}-{family}",
        "semantics_id": "matched_nonzero_null_noise_sensitivity_v1",
        "source_lane_id": lane,
        "provider": "ibm_runtime",
        "backend": "PREREGISTERED_IBM_BACKEND_TO_BE_SELECTED",
        "encoding_family": family,
        "circuit_template": template,
        "status": "template_counts_required",
        "no_hardware_submission": True,
        "job_or_task_ids": [],
        "backend_metadata": {"backend": "", "provider": "ibm_runtime", "calibration_timestamp_utc": "", "stage190_result_path": "", "additional_metadata": {}},
        "submitted_at_utc": "",
        "completed_at_utc": "",
        "shot_count": 4096,
        "raw_counts_by_row": [
            {"row_id": "r0", "ideal_score": 1.0, "component_exposure": 0.5, "counts": {}, "openqasm3": "OPENQASM 3.0;"},
            {"row_id": "r1", "ideal_score": 0.5, "component_exposure": 0.25, "counts": {}, "openqasm3": "OPENQASM 3.0;"},
        ],
        "required_execution_fields": ["job_or_task_ids", "backend_metadata", "submitted_at_utc", "completed_at_utc", "raw_counts_by_row"],
    }


def _sources(tmp_path):
    stage202 = tmp_path / "stage202.json"
    stage198 = tmp_path / "stage198.json"
    stage190 = tmp_path / "stage190.json"
    lanes = [
        "ibm_product_seed314_rows16_shots4096",
        "ibm_product_seed577_rows16_shots4096",
        "ibm_cx_seed314_rows16_shots4096",
        "ibm_cx_seed577_rows16_shots4096",
    ]
    families = ("phasewrap", "rope_like", "sinusoidal_like", "alibi_like", "matched_nonzero_null_control")
    templates = [_template(lane, family) for lane in lanes for family in families]
    _write_json(
        stage202,
        {
            "decision": "REDUCED_SCOPE_LIVE_RUNNER_PREPARATION_REVIEW_READY_TO_BUILD_PACKAGE_NOT_LIVE",
            "exact_approval_ready": True,
            "budget_cap_usd": 100.0,
            "backend_metadata": {"backend": "ibm_fez", "operational": True},
        },
    )
    _write_json(
        stage198,
        {
            "decision": "REDUCED_SCOPE_PREREGISTERED_READY_FOR_COST_ATTESTATION_REVIEW",
            "selected_scope": {
                "scope_id": "all_lanes_half_shots_2048",
                "estimated_total_job_count": 44,
                "estimated_total_shots": 81920 + 4000,
                "shots_per_row": 2048,
                "packet_row_job_count": 40,
            },
            "interpretation_boundary": {
                "hardware_scope_label": "reduced_precision_all_lanes_2048_shots_v1",
                "shots_per_row": 2048,
                "calibration_shots_per_state": 1000,
            },
        },
    )
    _write_json(
        stage190,
        {
            "decision": "REPLACEMENT_EXECUTION_PACKAGE_PREPARED_COUNTS_AND_CALIBRATION_REQUIRED",
            "execution_templates": templates,
            "calibration_template": {
                "template_type": "replacement_known_state_calibration_counts",
                "provider": "ibm_runtime",
                "status": "template_counts_required",
                "no_hardware_submission": True,
                "job_or_task_ids": [],
                "backend_metadata": {"backend": "", "provider": "ibm_runtime", "calibration_timestamp_utc": "", "additional_metadata": {}},
                "submitted_at_utc": "",
                "completed_at_utc": "",
                "shots_per_state": 1000,
                "raw_counts_by_state": [{"state": state, "expected_dominant_key": state, "counts": {}, "openqasm3": "OPENQASM 3.0;"} for state in ("00", "01", "10", "11")],
            },
        },
    )
    return stage202, stage198, stage190


def test_stage203_builds_reduced_scope_execution_package(tmp_path) -> None:
    stage202, stage198, stage190 = _sources(tmp_path)

    result = run_stage203_reduced_scope_execution_package(
        stage202_results_path=stage202,
        stage198_results_path=stage198,
        stage190_results_path=stage190,
    )

    assert result["decision"] == "REDUCED_SCOPE_EXECUTION_PACKAGE_PREPARED_COUNTS_AND_CALIBRATION_REQUIRED_NOT_LIVE"
    assert result["packet_template_count"] == 20
    assert result["estimated_packet_row_job_count"] == 40
    assert result["estimated_total_job_count"] == 44
    assert result["estimated_total_shots"] == 85920
    assert result["execution_templates"][0]["shot_count"] == 2048
    assert "shots2048" in result["execution_templates"][0]["packet_id"]
    assert result["live_submit_command_created"] is False


def test_stage203_blocks_without_stage202_approval(tmp_path) -> None:
    stage202, stage198, stage190 = _sources(tmp_path)
    _write_json(stage202, {"decision": "REDUCED_SCOPE_LIVE_RUNNER_PREPARATION_REVIEW_BLOCKED_APPROVAL_OR_PACKAGE_REQUIRED", "exact_approval_ready": False})

    result = run_stage203_reduced_scope_execution_package(
        stage202_results_path=stage202,
        stage198_results_path=stage198,
        stage190_results_path=stage190,
    )

    assert result["decision"] == "REDUCED_SCOPE_EXECUTION_PACKAGE_INCOMPLETE"
    assert "stage202_live_runner_preparation_not_ready" in result["blockers"]


def test_stage203_outputs_do_not_record_secrets_or_live_submit(tmp_path) -> None:
    stage202, stage198, stage190 = _sources(tmp_path)
    result = run_stage203_reduced_scope_execution_package(
        stage202_results_path=stage202,
        stage198_results_path=stage198,
        stage190_results_path=stage190,
    )

    paths = write_stage203_outputs(result, tmp_path / "out")
    written = (tmp_path / "out" / "results.json").read_text(encoding="utf-8")
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv", "template_dir"}
    assert "IBM_QUANTUM_TOKEN" not in written
    assert "QISKIT_IBM_TOKEN" not in written
    assert "crn:v1" not in written
    assert "--allow-live-submit" not in written
    assert "--allow-live-submit" not in summary
