from __future__ import annotations

from qrope.stage219_rope_substitution_gate import run_stage219_rope_substitution_gate


def test_stage219_supports_bounded_rope_substitution_claim() -> None:
    result = run_stage219_rope_substitution_gate()

    assert result["decision"] == "BOUNDED_PHASEWRAP_ROPE_SUBSTITUTION_SUPPORTED_WITH_MEASURED_CALIBRATION_DEGRADATION"
    assert result["blockers"] == []

    primary = result["primary_benchmark"]
    assert primary["stage"] == "stage30_matched_retrieval_bridge"
    assert primary["phasewrap_method"] == "phasewrap_distance_adapter"
    assert primary["phasewrap_metrics"]["top1_accuracy_mean"] == 1.0
    assert primary["phasewrap_metrics"]["mrr_mean"] == 1.0
    assert primary["degradation_vs_rope"]["top1_accuracy"] == 0.0
    assert primary["degradation_vs_rope"]["mrr"] == 0.0
    assert primary["degradation_vs_rope"]["mean_target_probability"] > 0.0
    assert primary["degradation_vs_rope"]["expected_calibration_error"] > 0.0
    assert primary["all_criteria_pass"] is True

    secondary = result["secondary_benchmark"]
    assert secondary["stage"] == "stage32_full_context_feature_bridge"
    assert secondary["phasewrap_method"] == "phasewrap_multiscale_adapter"
    assert secondary["phasewrap_metrics"]["top1_accuracy_mean"] == 1.0
    assert secondary["phasewrap_metrics"]["mrr_mean"] == 1.0
    assert secondary["all_criteria_pass"] is True
