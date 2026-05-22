from __future__ import annotations

import json

from qrope.stage210_reduced_scope_objective_conclusion import run_stage210_reduced_scope_objective_conclusion, write_stage210_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _stage198(path) -> None:
    _write_json(
        path,
        {
            "interpretation_boundary": {
                "hardware_scope_label": "reduced_precision_all_lanes_2048_shots_v1",
                "shots_per_row": 2048,
                "pass_fail_policy": {
                    "minimum_scaled_best_positional_margin_shot_quanta": 2.0,
                    "minimum_scaled_matched_null_margin_shot_quanta": 2.0,
                    "minimum_stable_seed_pairs": 2,
                    "minimum_stable_templates_per_seed_pair": 2,
                },
            }
        },
    )


def _stage208(path) -> None:
    _write_json(path, {"decision": "REDUCED_SCOPE_CALIBRATION_VALIDATED_READY_FOR_METRICS", "inferred_bitstring_order": "q1q0"})


def _stage209(path, *, positive: bool = True) -> None:
    decision = "REDUCED_SCOPE_HARDWARE_POSITIVE_PHASEWRAP_ADVANTAGE" if positive else "REDUCED_SCOPE_HARDWARE_DOES_NOT_SUPPORT_PHASEWRAP_ADVANTAGE"
    _write_json(
        path,
        {
            "decision": decision,
            "blockers": [],
            "hardware_scope_label": "reduced_precision_all_lanes_2048_shots_v1",
            "bitstring_order": "q1q0",
            "packet_template_count": 20,
            "candidate_records": [
                {
                    "seed_pair": "ibm:314",
                    "stable_template_count": 2,
                    "stable_templates": ["two_ry_cx_parity_z_readout_v1", "two_ry_product_state_z_readout_v1"],
                    "min_positional_margin_shot_quanta": 11.0,
                    "min_matched_null_margin_shot_quanta": 15.0,
                    "reduced_scope_hardware_positive": positive,
                },
                {
                    "seed_pair": "ibm:577",
                    "stable_template_count": 2,
                    "stable_templates": ["two_ry_cx_parity_z_readout_v1", "two_ry_product_state_z_readout_v1"],
                    "min_positional_margin_shot_quanta": 23.0,
                    "min_matched_null_margin_shot_quanta": 37.0,
                    "reduced_scope_hardware_positive": positive,
                },
            ],
            "comparison_summary": [
                {"all_families_present": True, "source_lane_id": "a"},
                {"all_families_present": True, "source_lane_id": "b"},
                {"all_families_present": True, "source_lane_id": "c"},
                {"all_families_present": True, "source_lane_id": "d"},
            ],
        },
    )


def test_stage210_supports_reduced_scope_objective_by_robustness(tmp_path) -> None:
    stage198 = tmp_path / "stage198.json"
    stage208 = tmp_path / "stage208.json"
    stage209 = tmp_path / "stage209.json"
    _stage198(stage198)
    _stage208(stage208)
    _stage209(stage209)

    result = run_stage210_reduced_scope_objective_conclusion(
        stage198_results_path=stage198,
        stage208_results_path=stage208,
        stage209_results_path=stage209,
    )

    assert result["decision"] == "REDUCED_SCOPE_OBJECTIVE_SUPPORTED_BY_HARDWARE_ROBUSTNESS"
    assert result["objective_supported"] is True
    assert result["support_mode"] == "robustness"
    assert result["auditability_advantage_separately_supported"] is False
    assert result["stable_seed_pair_count"] == 2
    assert result["weakest_positional_margin_shot_quanta"] == 11.0


def test_stage210_blocks_when_stage209_is_not_positive(tmp_path) -> None:
    stage198 = tmp_path / "stage198.json"
    stage208 = tmp_path / "stage208.json"
    stage209 = tmp_path / "stage209.json"
    _stage198(stage198)
    _stage208(stage208)
    _stage209(stage209, positive=False)

    result = run_stage210_reduced_scope_objective_conclusion(
        stage198_results_path=stage198,
        stage208_results_path=stage208,
        stage209_results_path=stage209,
    )

    assert result["decision"] == "REDUCED_SCOPE_OBJECTIVE_CONCLUSION_BLOCKED_OR_NOT_SUPPORTED"
    assert result["objective_supported"] is False
    assert "stage209_reduced_scope_positive_missing" in result["blockers"]


def test_stage210_blocks_when_family_coverage_is_incomplete(tmp_path) -> None:
    stage198 = tmp_path / "stage198.json"
    stage208 = tmp_path / "stage208.json"
    stage209 = tmp_path / "stage209.json"
    _stage198(stage198)
    _stage208(stage208)
    _stage209(stage209)
    payload = json.loads(stage209.read_text(encoding="utf-8"))
    payload["comparison_summary"][0]["all_families_present"] = False
    _write_json(stage209, payload)

    result = run_stage210_reduced_scope_objective_conclusion(
        stage198_results_path=stage198,
        stage208_results_path=stage208,
        stage209_results_path=stage209,
    )

    assert result["objective_supported"] is False
    assert "comparison_family_coverage_incomplete" in result["blockers"]


def test_stage210_outputs_do_not_record_secrets_or_live_submit(tmp_path) -> None:
    stage198 = tmp_path / "stage198.json"
    stage208 = tmp_path / "stage208.json"
    stage209 = tmp_path / "stage209.json"
    _stage198(stage198)
    _stage208(stage208)
    _stage209(stage209)
    result = run_stage210_reduced_scope_objective_conclusion(
        stage198_results_path=stage198,
        stage208_results_path=stage208,
        stage209_results_path=stage209,
    )

    write_stage210_outputs(result, tmp_path / "out")
    written = (tmp_path / "out" / "results.json").read_text(encoding="utf-8")
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert "IBM_QUANTUM_TOKEN" not in written
    assert "QISKIT_IBM_TOKEN" not in written
    assert "crn:v1" not in written
    assert "--allow-live-submit" not in written
    assert "--allow-live-submit" not in summary
