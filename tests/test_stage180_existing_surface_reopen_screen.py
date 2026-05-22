from __future__ import annotations

import json

from qrope.stage180_existing_surface_reopen_screen import run_stage180_existing_surface_reopen_screen, write_stage180_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _sources(tmp_path):
    stage177 = tmp_path / "stage177.json"
    stage179 = tmp_path / "stage179.json"
    _write_json(
        stage177,
        {
            "decision": "IBM_BACKEND_INFORMED_SIM_DOES_NOT_SUPPORT_TARGETED_HARDWARE_RUN_YET",
            "noise_models": [
                {
                    "noise_model_id": "ibm_backend_median_stochastic",
                    "noise_family": "ibm_backend_properties_stochastic",
                    "readout_bitflip_probability": 0.0,
                    "depolarizing_observable_shrink": 0.0,
                    "ry_angle_scale_error": 0.0,
                    "ry_angle_offset_radians": 0.02,
                    "observable_bias_component_a": 0.0,
                    "observable_bias_component_b": 0.0,
                }
            ],
        },
    )
    _write_json(stage179, {"decision": "CURRENT_IBM_HARDWARE_PATH_ARCHIVE_RECOMMENDED"})
    return stage177, stage179


def _packet(path, lane_id: str, family: str, circuit_template: str, component_a: float, component_b: float) -> None:
    score = 0.5 + 0.25 * (component_a + component_b)
    _write_json(
        path,
        {
            "packet_id": f"{lane_id}__{family}",
            "provider": "ibm_runtime",
            "source_lane_id": lane_id,
            "encoding_family": family,
            "shot_count": 4096,
            "fixed_width": {"circuit_template": circuit_template},
            "rows": [
                {
                    "row_id": "row_0",
                    "components": {"component_a": component_a, "component_b": component_b},
                    "ideal_predictions": {"score": score},
                }
            ],
        },
    )


def _manifests(tmp_path, *, candidate=True):
    packet_dir = tmp_path / "packets"
    packet_paths = []
    specs = (
        {
            "phasewrap": (1.0, 1.0),
            "rope_like": (0.0, 0.0),
            "sinusoidal_like": (0.1, 0.1),
            "alibi_like": (0.2, 0.2),
            "no_position_control": (0.0, 0.0),
        }
        if candidate
        else {
            "phasewrap": (0.0, 0.0),
            "rope_like": (1.0, 1.0),
            "sinusoidal_like": (0.8, 0.8),
            "alibi_like": (0.6, 0.6),
            "no_position_control": (0.2, 0.2),
        }
    )
    lanes = {
        "ibm_product_seed999_rows16_shots4096": "two_ry_product_state_z_readout_v1",
        "ibm_cx_seed999_rows16_shots4096": "two_ry_cx_parity_z_readout_v1",
    }
    for lane_id, template in lanes.items():
        for family, components in specs.items():
            path = packet_dir / f"{lane_id}__{family}.json"
            _packet(path, lane_id, family, template, *components)
            packet_paths.append(str(path.as_posix()))
    stage99 = tmp_path / "stage99.json"
    stage100 = tmp_path / "stage100.json"
    _write_json(stage99, {"packet_paths": packet_paths[:5]})
    _write_json(stage100, {"packet_paths": packet_paths[5:]})
    return stage99, stage100


def test_stage180_finds_existing_surface_reopen_candidate(tmp_path) -> None:
    stage177, stage179 = _sources(tmp_path)
    stage99, stage100 = _manifests(tmp_path, candidate=True)

    result = run_stage180_existing_surface_reopen_screen(
        stage177_results_path=stage177,
        stage179_results_path=stage179,
        stage99_manifest_path=stage99,
        stage100_manifest_path=stage100,
    )

    assert result["decision"] == "EXISTING_SURFACE_REOPEN_CANDIDATES_FOUND"
    assert result["reopen_candidate_count"] == 1
    assert result["reopen_candidates"][0]["stable_template_count"] == 2


def test_stage180_reports_no_existing_surface_candidate(tmp_path) -> None:
    stage177, stage179 = _sources(tmp_path)
    stage99, stage100 = _manifests(tmp_path, candidate=False)

    result = run_stage180_existing_surface_reopen_screen(
        stage177_results_path=stage177,
        stage179_results_path=stage179,
        stage99_manifest_path=stage99,
        stage100_manifest_path=stage100,
    )

    assert result["decision"] == "EXISTING_SURFACE_HAS_NO_IBM_INFORMED_REOPEN_CANDIDATE"
    assert result["reopen_candidate_count"] == 0


def test_stage180_outputs_do_not_record_secrets_or_live_submit(tmp_path) -> None:
    stage177, stage179 = _sources(tmp_path)
    stage99, stage100 = _manifests(tmp_path)
    result = run_stage180_existing_surface_reopen_screen(
        stage177_results_path=stage177,
        stage179_results_path=stage179,
        stage99_manifest_path=stage99,
        stage100_manifest_path=stage100,
    )

    paths = write_stage180_outputs(result, tmp_path / "out")
    written = (tmp_path / "out" / "results.json").read_text(encoding="utf-8")
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert "IBM_QUANTUM_TOKEN" not in written
    assert "crn:v1" not in written
    assert "--allow-live-submit" not in written
    assert "--allow-live-submit" not in summary
