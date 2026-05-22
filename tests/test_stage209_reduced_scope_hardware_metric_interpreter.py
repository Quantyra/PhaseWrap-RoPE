from __future__ import annotations

import json

from qrope.stage209_reduced_scope_hardware_metric_interpreter import (
    CX_TEMPLATE,
    PRODUCT_TEMPLATE,
    _observed_score,
    run_stage209_reduced_scope_hardware_metric_interpreter,
    write_stage209_outputs,
)


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _stage198(path) -> None:
    _write_json(
        path,
        {
            "interpretation_boundary": {
                "hardware_scope_label": "reduced_precision_all_lanes_2048_shots_v1",
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
    _write_json(
        path,
        {
            "decision": "REDUCED_SCOPE_CALIBRATION_VALIDATED_READY_FOR_METRICS",
            "inferred_bitstring_order": "q1q0",
        },
    )


def _row(ideal: float, observed: float, exposure: float = 1.0) -> dict:
    zeros = int(round(2048 * observed))
    ones = 2048 - zeros
    return {"row_id": "hwrow-000", "ideal_score": ideal, "component_exposure": exposure, "counts": {"00": zeros, "11": ones}}


def _template(lane: str, family: str, template: str, ideal: float, observed: float) -> dict:
    return {
        "template_type": "reduced_scope_packet_execution_counts",
        "packet_id": f"{lane}__{family}",
        "source_lane_id": lane,
        "encoding_family": family,
        "circuit_template": template,
        "shot_count": 2048,
        "raw_counts_by_row": [_row(ideal, observed)],
    }


def _stage207(path) -> None:
    templates = []
    for seed in ("314", "577"):
        for kind, circuit_template in (("product", PRODUCT_TEMPLATE), ("cx", CX_TEMPLATE)):
            lane = f"ibm_{kind}_seed{seed}_rows16_shots2048"
            templates.extend(
                [
                    _template(lane, "phasewrap", circuit_template, 1.0, 1.0),
                    _template(lane, "rope_like", circuit_template, 1.0, 0.9),
                    _template(lane, "sinusoidal_like", circuit_template, 1.0, 0.9),
                    _template(lane, "alibi_like", circuit_template, 1.0, 0.9),
                    _template(lane, "matched_nonzero_null_control", circuit_template, 1.0, 0.9),
                ]
            )
    _write_json(
        path,
        {
            "decision": "REDUCED_SCOPE_RESULT_COUNTS_COLLECTED_READY_FOR_CALIBRATION",
            "collected_templates": templates,
        },
    )


def test_observed_score_applies_reversed_q1q0_order_for_product() -> None:
    observed, logical = _observed_score(PRODUCT_TEMPLATE, {"10": 2048}, "q1q0")

    assert logical["01"] == 2048
    assert observed == 0.5


def test_stage209_detects_reduced_scope_positive(tmp_path) -> None:
    stage198 = tmp_path / "stage198.json"
    stage207 = tmp_path / "stage207.json"
    stage208 = tmp_path / "stage208.json"
    _stage198(stage198)
    _stage207(stage207)
    _stage208(stage208)

    result = run_stage209_reduced_scope_hardware_metric_interpreter(
        stage198_results_path=stage198,
        stage207_results_path=stage207,
        stage208_results_path=stage208,
    )

    assert result["decision"] == "REDUCED_SCOPE_HARDWARE_POSITIVE_PHASEWRAP_ADVANTAGE"
    assert result["reduced_scope_positive_seed_pair_count"] == 2
    assert result["blockers"] == []


def test_stage209_outputs_do_not_record_secrets_or_live_submit(tmp_path) -> None:
    stage198 = tmp_path / "stage198.json"
    stage207 = tmp_path / "stage207.json"
    stage208 = tmp_path / "stage208.json"
    _stage198(stage198)
    _stage207(stage207)
    _stage208(stage208)
    result = run_stage209_reduced_scope_hardware_metric_interpreter(
        stage198_results_path=stage198,
        stage207_results_path=stage207,
        stage208_results_path=stage208,
    )

    write_stage209_outputs(result, tmp_path / "out")
    written = (tmp_path / "out" / "results.json").read_text(encoding="utf-8")
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert "IBM_QUANTUM_TOKEN" not in written
    assert "QISKIT_IBM_TOKEN" not in written
    assert "crn:v1" not in written
    assert "--allow-live-submit" not in written
    assert "--allow-live-submit" not in summary
