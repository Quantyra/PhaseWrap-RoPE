from __future__ import annotations

import json

from qrope.stage190_replacement_execution_package import run_stage190_replacement_execution_package, write_stage190_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _packet(lane: str, family: str) -> dict:
    template = "two_ry_cx_parity_z_readout_v1" if "_cx_" in lane else "two_ry_product_state_z_readout_v1"
    return {
        "packet_id": f"{lane}__sem__{family}",
        "packet_hash": f"hash-{lane}-{family}",
        "semantics_id": "matched_nonzero_null_noise_sensitivity_v1",
        "provider": "ibm_runtime",
        "backend": "fixture_backend",
        "source_lane_id": lane,
        "encoding_family": family,
        "row_count": 2,
        "shot_count": 1000,
        "fixed_width": {"circuit_template": template},
        "rows": [
            {
                "row_id": "r0",
                "component_exposure": 0.25,
                "circuit_parameters": {"ry_q0": 0.0, "ry_q1": 0.0},
                "ideal_predictions": {"score": 1.0},
            },
            {
                "row_id": "r1",
                "component_exposure": 0.25,
                "circuit_parameters": {"ry_q0": 1.0, "ry_q1": 1.0},
                "ideal_predictions": {"score": 0.5},
            },
        ],
    }


def _sources(tmp_path):
    stage188 = tmp_path / "stage188.json"
    stage189 = tmp_path / "stage189.json"
    lanes = ["ibm_product_seed314_rows16_shots4096", "ibm_cx_seed314_rows16_shots4096"]
    families = ("phasewrap", "rope_like", "sinusoidal_like", "alibi_like", "matched_nonzero_null_control")
    packets = [_packet(lane, family) for lane in lanes for family in families]
    _write_json(stage188, {"semantics_id": "matched_nonzero_null_noise_sensitivity_v1", "packets": packets})
    _write_json(
        stage189,
        {
            "decision": "REPLACEMENT_HARDWARE_REVIEW_REOPENED_BUT_NOT_READY_FOR_LIVE_RUN",
            "selected_lanes": lanes,
        },
    )
    return stage188, stage189


def test_stage190_builds_replacement_execution_package(tmp_path) -> None:
    stage188, stage189 = _sources(tmp_path)

    result = run_stage190_replacement_execution_package(stage188_results_path=stage188, stage189_results_path=stage189)

    assert result["decision"] == "REPLACEMENT_EXECUTION_PACKAGE_PREPARED_COUNTS_AND_CALIBRATION_REQUIRED"
    assert result["packet_template_count"] == 10
    assert result["calibration_template_count"] == 1
    assert result["estimated_packet_row_job_count"] == 20
    assert result["estimated_calibration_job_count"] == 4
    assert result["no_hardware_submission"] is True


def test_stage190_blocks_when_review_not_reopened(tmp_path) -> None:
    stage188, stage189 = _sources(tmp_path)
    _write_json(stage189, {"decision": "NOPE", "selected_lanes": ["ibm_product_seed314_rows16_shots4096"]})

    result = run_stage190_replacement_execution_package(stage188_results_path=stage188, stage189_results_path=stage189)

    assert result["decision"] == "REPLACEMENT_EXECUTION_PACKAGE_INCOMPLETE"
    assert "stage189_hardware_review_not_reopened" in result["blockers"]


def test_stage190_outputs_do_not_record_secrets_or_live_submit(tmp_path) -> None:
    stage188, stage189 = _sources(tmp_path)
    result = run_stage190_replacement_execution_package(stage188_results_path=stage188, stage189_results_path=stage189)

    paths = write_stage190_outputs(result, tmp_path / "out")
    written = (tmp_path / "out" / "results.json").read_text(encoding="utf-8")
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv", "template_dir"}
    assert "IBM_QUANTUM_TOKEN" not in written
    assert "crn:v1" not in written
    assert "--allow-live-submit" not in written
    assert "--allow-live-submit" not in summary
