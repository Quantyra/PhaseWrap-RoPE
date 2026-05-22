from __future__ import annotations

import json

from qrope.stage184_error_orthogonalized_components_candidate_screen import (
    DESIGN_FAMILY_ID,
    run_stage184_error_orthogonalized_components_candidate_screen,
    write_stage184_outputs,
)


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _stage177(path) -> None:
    _write_json(
        path,
        {
            "noise_models": [
                {
                    "noise_model_id": "ibm_backend_median_stochastic",
                    "noise_family": "ibm_backend_properties_stochastic",
                    "readout_bitflip_probability": 0.01,
                    "depolarizing_observable_shrink": 0.002,
                    "ry_angle_scale_error": 0.0,
                    "ry_angle_offset_radians": 0.0,
                    "observable_bias_component_a": 0.0,
                    "observable_bias_component_b": 0.0,
                },
                {
                    "noise_model_id": "ibm_backend_p75_stochastic",
                    "noise_family": "ibm_backend_properties_stochastic",
                    "readout_bitflip_probability": 0.03,
                    "depolarizing_observable_shrink": 0.004,
                    "ry_angle_scale_error": 0.0,
                    "ry_angle_offset_radians": 0.0,
                    "observable_bias_component_a": 0.0,
                    "observable_bias_component_b": 0.0,
                },
            ]
        },
    )


def _stage181(path, *, ready: bool = True) -> None:
    _write_json(
        path,
        {
            "decision": "FIXED_WIDTH_TARGET_REDESIGN_PLAN_READY" if ready else "FIXED_WIDTH_TARGET_REDESIGN_PLAN_INCOMPLETE",
            "design_families": [{"family_id": DESIGN_FAMILY_ID}],
        },
    )


def _source_packet(path, lane_id: str, provider: str, shots: int = 1000) -> None:
    rows = [
        {
            "row_id": f"{lane_id}_row0",
            "row_hash": f"{lane_id}_hash0",
            "source": {"reference_delta": -4, "candidate_delta": 0},
        },
        {
            "row_id": f"{lane_id}_row1",
            "row_hash": f"{lane_id}_hash1",
            "source": {"reference_delta": 0, "candidate_delta": 0},
        },
        {
            "row_id": f"{lane_id}_row2",
            "row_hash": f"{lane_id}_hash2",
            "source": {"reference_delta": 4, "candidate_delta": 0},
        },
    ]
    _write_json(
        path,
        {
            "provider": provider,
            "backend": "fixture_backend",
            "config": {"shot_count": shots},
            "preregistration": {"lane_id": lane_id, "row_set_hash": f"{lane_id}_row_set"},
            "rows": rows,
        },
    )


def _source_dir(tmp_path):
    source_dir = tmp_path / "stage4"
    product_files = ("fixture_product_seed1_rows3_shots1000.json",)
    cx_files = ("fixture_cx_seed1_rows3_shots1000.json",)
    _source_packet(source_dir / product_files[0], "fixture_product_seed1_rows3_shots1000", "fixture")
    _source_packet(source_dir / cx_files[0], "fixture_cx_seed1_rows3_shots1000", "fixture")
    return source_dir, product_files, cx_files


def test_stage184_runs_error_orthogonalized_candidate_screen_without_hardware(tmp_path) -> None:
    stage177 = tmp_path / "stage177.json"
    stage181 = tmp_path / "stage181.json"
    _stage177(stage177)
    _stage181(stage181)
    source_dir, product_files, cx_files = _source_dir(tmp_path)

    result = run_stage184_error_orthogonalized_components_candidate_screen(
        stage177_results_path=stage177,
        stage181_results_path=stage181,
        source_packet_dir=source_dir,
        product_source_packet_files=product_files,
        cx_source_packet_files=cx_files,
    )

    assert result["status"] == "completed"
    assert result["decision"] == "ERROR_ORTHOGONALIZED_COMPONENTS_CANDIDATE_DOES_NOT_SUPPORT_HARDWARE_REOPEN"
    assert result["packet_count"] == 10
    assert result["comparison_group_count"] == 4
    assert result["no_hardware_submission"] is True
    assert result["provider_credentials_required"] is False


def test_stage184_blocks_when_redesign_plan_not_ready(tmp_path) -> None:
    stage177 = tmp_path / "stage177.json"
    stage181 = tmp_path / "stage181.json"
    _stage177(stage177)
    _stage181(stage181, ready=False)
    source_dir, product_files, cx_files = _source_dir(tmp_path)

    result = run_stage184_error_orthogonalized_components_candidate_screen(
        stage177_results_path=stage177,
        stage181_results_path=stage181,
        source_packet_dir=source_dir,
        product_source_packet_files=product_files,
        cx_source_packet_files=cx_files,
    )

    assert result["decision"] == "ERROR_ORTHOGONALIZED_COMPONENTS_CANDIDATE_SCREEN_INCOMPLETE"
    assert "stage181_redesign_plan_not_ready" in result["blockers"]


def test_stage184_outputs_do_not_record_secrets_or_live_submit(tmp_path) -> None:
    stage177 = tmp_path / "stage177.json"
    stage181 = tmp_path / "stage181.json"
    _stage177(stage177)
    _stage181(stage181)
    source_dir, product_files, cx_files = _source_dir(tmp_path)
    result = run_stage184_error_orthogonalized_components_candidate_screen(
        stage177_results_path=stage177,
        stage181_results_path=stage181,
        source_packet_dir=source_dir,
        product_source_packet_files=product_files,
        cx_source_packet_files=cx_files,
    )

    paths = write_stage184_outputs(result, tmp_path / "out")
    written = (tmp_path / "out" / "results.json").read_text(encoding="utf-8")
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv", "packet_dir"}
    assert "IBM_QUANTUM_TOKEN" not in written
    assert "crn:v1" not in written
    assert "--allow-live-submit" not in written
    assert "--allow-live-submit" not in summary
