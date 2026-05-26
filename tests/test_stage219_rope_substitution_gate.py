from __future__ import annotations

from qrope.stage219_rope_substitution_gate import run_stage219_rope_substitution_gate


def test_stage219_supports_bounded_ranking_parity_claim() -> None:
    result = run_stage219_rope_substitution_gate()

    assert result["decision"] == "BOUNDED_PHASEWRAP_RANKING_PARITY_WITH_MEASURED_CALIBRATION_DEGRADATION"
    assert result["legacy_decision_aliases"] == [
        "BOUNDED_PHASEWRAP_ROPE_SUBSTITUTION_SUPPORTED_WITH_MEASURED_CALIBRATION_DEGRADATION"
    ]
    assert result["blockers"] == []
    assert "ranking parity" in result["supported_claim"]
    assert "substitution adequacy" in result["claim_boundary"]["does_not_support"]
    assert "adequacy_criteria" not in result

    primary = result["primary_benchmark"]
    assert primary["stage"] == "stage30_matched_retrieval_bridge"
    assert primary["phasewrap_method"] == "phasewrap_distance_adapter"
    assert primary["phasewrap_metrics"]["top1_accuracy_mean"] == 1.0
    assert primary["phasewrap_metrics"]["mrr_mean"] == 1.0
    assert primary["degradation_vs_rope"]["top1_accuracy"] == 0.0
    assert primary["degradation_vs_rope"]["mrr"] == 0.0
    assert primary["degradation_vs_rope"]["mean_target_probability"] > 0.0
    assert primary["degradation_vs_rope"]["expected_calibration_error"] > 0.0
    assert "rope_probability_advantage_recorded" not in primary["ranking_criteria"]
    assert "rope_calibration_advantage_recorded" not in primary["ranking_criteria"]
    assert primary["degradation_observed"]["target_probability"] is True
    assert primary["degradation_observed"]["expected_calibration_error"] is True
    assert primary["ranking_parity_pass"] is True

    secondary = result["secondary_benchmark"]
    assert secondary["stage"] == "stage32_full_context_feature_bridge"
    assert secondary["phasewrap_method"] == "phasewrap_multiscale_adapter"
    assert secondary["phasewrap_metrics"]["top1_accuracy_mean"] == 1.0
    assert secondary["phasewrap_metrics"]["mrr_mean"] == 1.0
    assert secondary["ranking_parity_pass"] is True
