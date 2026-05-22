from __future__ import annotations

import json

from qrope.stage165_simulated_noise_margin_stability_audit import (
    run_stage165_margin_stability_audit,
    write_stage165_outputs,
)


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _stage153_payload() -> dict:
    metric_records = []
    for source_lane_id, template in (
        ("ibm_cx_seed314_rows16_shots4096", "two_ry_cx_parity_z_readout_v1"),
        ("ibm_product_seed314_rows16_shots4096", "two_ry_product_state_z_readout_v1"),
        ("braket_cx_seed2718_rows8_shots1000", "two_ry_cx_parity_z_readout_v1"),
    ):
        metric_records.append(
            {
                "noise_model_id": "ry_offset_0p02rad",
                "provider": "ibm_runtime" if source_lane_id.startswith("ibm") else "amazon_braket",
                "source_lane_id": source_lane_id,
                "circuit_template": template,
                "encoding_family": "phasewrap",
                "shot_counts": [4096 if source_lane_id.startswith("ibm") else 1000],
            }
        )
    return {
        "decision": "SIMULATED_NOISE_PHASEWRAP_STRICT_ADVANTAGE_OBSERVED",
        "noise_models": [{"noise_model_id": "ry_offset_0p02rad", "noise_family": "coherent_ry_angle_offset"}],
        "metric_records": metric_records,
    }


def _target(provider, lane, template, phasewrap, comparator, control) -> dict:
    return {
        "noise_model_id": "ry_offset_0p02rad",
        "provider": provider,
        "source_lane_id": lane,
        "circuit_template": template,
        "phasewrap_mean_absolute_score_error": phasewrap,
        "best_positional_comparator_mean_absolute_score_error": comparator,
        "no_position_control_mean_absolute_score_error": control,
    }


def test_stage165_recommends_provider_only_when_two_templates_clear_shot_margin(tmp_path) -> None:
    stage153 = tmp_path / "stage153.json"
    stage154 = tmp_path / "stage154.json"
    _write_json(stage153, _stage153_payload())
    _write_json(
        stage154,
        {
            "decision": "SIMULATED_NOISE_TARGETED_HARDWARE_FOLLOWUP_RECOMMENDED",
            "recommended_targets": [
                _target(
                    "ibm_runtime",
                    "ibm_cx_seed314_rows16_shots4096",
                    "two_ry_cx_parity_z_readout_v1",
                    0.0039,
                    0.0046,
                    0.0100,
                ),
                _target(
                    "ibm_runtime",
                    "ibm_product_seed314_rows16_shots4096",
                    "two_ry_product_state_z_readout_v1",
                    0.0039,
                    0.0046,
                    0.0100,
                ),
                _target(
                    "amazon_braket",
                    "braket_cx_seed2718_rows8_shots1000",
                    "two_ry_cx_parity_z_readout_v1",
                    0.0024,
                    0.0029,
                    0.0100,
                ),
            ],
        },
    )

    result = run_stage165_margin_stability_audit(stage153_results_path=stage153, stage154_results_path=stage154)
    providers = {record["provider"]: record for record in result["provider_records"]}

    assert result["decision"] == "SIMULATED_NOISE_STABLE_TARGETED_HARDWARE_PROBE_RECOMMENDED"
    assert result["stable_target_count"] == 2
    assert result["recommended_hardware_probe_providers"] == ["ibm_runtime"]
    assert providers["ibm_runtime"]["hardware_probe_recommended"] is True
    assert providers["amazon_braket"]["hardware_probe_recommended"] is False
    assert providers["amazon_braket"]["stable_target_count"] == 0


def test_stage165_blocks_subshot_targets(tmp_path) -> None:
    stage153 = tmp_path / "stage153.json"
    stage154 = tmp_path / "stage154.json"
    _write_json(stage153, _stage153_payload())
    _write_json(
        stage154,
        {
            "decision": "SIMULATED_NOISE_TARGETED_HARDWARE_FOLLOWUP_RECOMMENDED",
            "recommended_targets": [
                _target(
                    "ibm_runtime",
                    "ibm_cx_seed314_rows16_shots4096",
                    "two_ry_cx_parity_z_readout_v1",
                    0.0040,
                    0.0041,
                    0.0100,
                )
            ],
        },
    )

    result = run_stage165_margin_stability_audit(stage153_results_path=stage153, stage154_results_path=stage154)

    assert result["decision"] == "SIMULATED_NOISE_STABLE_HARDWARE_PROBE_NOT_RECOMMENDED_YET"
    assert result["stable_target_count"] == 0
    assert "positional_margin_below_two_shot_quanta" in result["target_records"][0]["stability_blockers"]


def test_stage165_outputs_are_written(tmp_path) -> None:
    stage153 = tmp_path / "stage153.json"
    stage154 = tmp_path / "stage154.json"
    _write_json(stage153, _stage153_payload())
    _write_json(
        stage154,
        {
            "decision": "SIMULATED_NOISE_TARGETED_HARDWARE_FOLLOWUP_RECOMMENDED",
            "recommended_targets": [
                _target(
                    "ibm_runtime",
                    "ibm_cx_seed314_rows16_shots4096",
                    "two_ry_cx_parity_z_readout_v1",
                    0.0039,
                    0.0046,
                    0.0100,
                )
            ],
        },
    )
    result = run_stage165_margin_stability_audit(stage153_results_path=stage153, stage154_results_path=stage154)

    paths = write_stage165_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert manifest["recommended_target_count"] == 1
    assert "ibm_runtime" in summary
