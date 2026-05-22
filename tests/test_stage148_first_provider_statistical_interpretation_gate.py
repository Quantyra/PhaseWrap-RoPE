from __future__ import annotations

import json

from qrope.stage148_first_provider_statistical_interpretation_gate import run_stage148_gate, write_stage148_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _fixture(tmp_path, *, ready: bool) -> tuple[object, object, object]:
    root = tmp_path / "window"
    calibration_path = root / "calibration" / "ibm_runtime_known_state_execution.json"
    stage101_path = root / "calibration" / "stage101" / "results.json"
    stage103_path = root / "stage103" / "results.json"
    packet_dir = root / "packet_executions"
    plans = tmp_path / "plans.json"
    stage146 = tmp_path / "stage146.json"
    stage147 = tmp_path / "stage147.json"
    _write_json(
        plans,
        [
            {
                "provider": "ibm_runtime",
                "window_id": "window_0",
                "steps": [
                    {"step_id": "known_state_calibration_execution", "output_path": str(calibration_path.as_posix())},
                    {"step_id": "matched_packet_execution", "output_dir": str(packet_dir.as_posix())},
                ],
            }
        ],
    )
    _write_json(
        stage147,
        {
            "provider_scope": "ibm_runtime",
            "state_records": [
                {"state": "00", "expected_dominant_key": "00", "minimum_wilson95_dominant_count": 825},
                {"state": "01", "expected_dominant_key": "10", "minimum_wilson95_dominant_count": 825},
            ],
        },
    )
    _write_json(
        stage146,
        {
            "lane_summaries": [
                {
                    "provider": "ibm_runtime",
                    "window_id": "window_0",
                    "source_lane_id": "lane_a",
                    "circuit_template": "two_ry_product_state_z_readout_v1",
                    "minimum_phasewrap_mae_margin_for_95pct_shot_noise_separation": 0.01,
                }
            ]
        },
    )
    if ready:
        _write_json(
            calibration_path,
            {
                "status": "assembled_from_stage113_results",
                "no_hardware_submission": False,
                "raw_counts_by_state": [
                    {"state": "00", "counts": {"00": 900, "01": 100}},
                    {"state": "01", "counts": {"10": 900, "00": 100}},
                ]
            },
        )
        _write_json(
            stage101_path,
            {
                "decision": "KNOWN_STATE_CALIBRATION_VERIFIED_READY_FOR_MATCHED_HARDWARE_EXECUTION",
                "known_state_calibration_pass": True,
            },
        )
        _write_json(
            stage103_path,
            {
                "decision": "ROBUSTNESS_METRICS_READY_FOR_INTERPRETATION",
                "comparison_summary": [
                    {
                        "source_lane_id": "lane_a",
                        "circuit_template": "two_ry_product_state_z_readout_v1",
                        "phasewrap_mean_absolute_score_error": 0.02,
                        "best_comparator_mean_absolute_score_error": 0.05,
                        "phasewrap_lower_error_than": ["rope_like", "sinusoidal_like", "alibi_like", "no_position_control"],
                        "all_families_present": True,
                    }
                ]
            },
        )
    return plans, stage146, stage147


def test_stage148_blocks_when_observed_provider_evidence_is_missing(tmp_path) -> None:
    plans, stage146, stage147 = _fixture(tmp_path, ready=False)

    result = run_stage148_gate(stage107_window_plans_path=plans, stage146_results_path=stage146, stage147_results_path=stage147)

    assert result["decision"] == "FIRST_PROVIDER_STATISTICAL_INTERPRETATION_BLOCKED_EVIDENCE_REQUIRED"
    assert result["ready_calibration_record_count"] == 0
    assert result["shot_noise_separated_lane_count"] == 0


def test_stage148_reports_ready_when_calibration_and_margins_pass(tmp_path) -> None:
    plans, stage146, stage147 = _fixture(tmp_path, ready=True)

    result = run_stage148_gate(stage107_window_plans_path=plans, stage146_results_path=stage146, stage147_results_path=stage147)

    assert result["decision"] == "FIRST_PROVIDER_STATISTICAL_INTERPRETATION_READY_FOR_CLAIM_GATES"
    assert result["ready_calibration_record_count"] == 1
    assert result["shot_noise_separated_lane_count"] == 1
    assert result["lane_records"][0]["phasewrap_mae_margin"] == 0.03


def test_stage148_blocks_complete_calibration_counts_without_stage113_status(tmp_path) -> None:
    plans, stage146, stage147 = _fixture(tmp_path, ready=True)
    calibration_path = tmp_path / "window" / "calibration" / "ibm_runtime_known_state_execution.json"
    calibration = json.loads(calibration_path.read_text(encoding="utf-8"))
    calibration.pop("status")
    _write_json(calibration_path, calibration)

    result = run_stage148_gate(stage107_window_plans_path=plans, stage146_results_path=stage146, stage147_results_path=stage147)

    assert result["decision"] == "FIRST_PROVIDER_STATISTICAL_INTERPRETATION_BLOCKED_EVIDENCE_REQUIRED"
    assert result["ready_calibration_record_count"] == 0
    assert "stage113_assembled_calibration_status" in result["calibration_records"][0]["missing_evidence"]


def test_stage148_blocks_summary_shaped_stage103_without_ready_decision(tmp_path) -> None:
    plans, stage146, stage147 = _fixture(tmp_path, ready=True)
    stage103_path = tmp_path / "window" / "stage103" / "results.json"
    stage103 = json.loads(stage103_path.read_text(encoding="utf-8"))
    stage103.pop("decision")
    _write_json(stage103_path, stage103)

    result = run_stage148_gate(stage107_window_plans_path=plans, stage146_results_path=stage146, stage147_results_path=stage147)

    assert result["decision"] == "FIRST_PROVIDER_STATISTICAL_INTERPRETATION_BLOCKED_EVIDENCE_REQUIRED"
    assert result["stage103_lower_mae_lane_count"] == 0
    assert result["lane_records"][0]["stage103_ready_for_interpretation"] is False


def test_stage148_outputs_are_written(tmp_path) -> None:
    plans, stage146, stage147 = _fixture(tmp_path, ready=False)
    result = run_stage148_gate(stage107_window_plans_path=plans, stage146_results_path=stage146, stage147_results_path=stage147)

    written = write_stage148_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(written) == {"manifest", "result", "summary_csv"}
    assert manifest["decision"] == "FIRST_PROVIDER_STATISTICAL_INTERPRETATION_BLOCKED_EVIDENCE_REQUIRED"
    assert "minimum_shot_noise_separation_margin" in summary
