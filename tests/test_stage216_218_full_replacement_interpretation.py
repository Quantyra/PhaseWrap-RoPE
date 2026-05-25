from __future__ import annotations

from qrope.stage216_full_replacement_merged_result_counts import run_stage216_full_replacement_merged_result_counts
from qrope.stage217_full_replacement_calibration_validation import run_stage217_full_replacement_calibration_validation
from qrope.stage218_full_replacement_hardware_metric_interpreter import run_stage218_full_replacement_hardware_metric_interpreter


def test_stage216_merges_original_and_allocated_instance_counts() -> None:
    result = run_stage216_full_replacement_merged_result_counts()

    assert result["decision"] == "FULL_REPLACEMENT_ALL_RESULT_COUNTS_MERGED_READY_FOR_CALIBRATION"
    assert result["blockers"] == []
    assert result["merged_template_count"] == 21
    assert result["expected_template_count"] == 21
    assert result["secret_values_recorded"] is False


def test_stage217_validates_unique_ibm_bitstring_order() -> None:
    result = run_stage217_full_replacement_calibration_validation()

    assert result["decision"] == "FULL_REPLACEMENT_CALIBRATION_VALIDATED_READY_FOR_METRICS"
    assert result["blockers"] == []
    assert result["inferred_bitstring_order"] == "q1q0"
    assert len(result["state_records"]) == 8
    q1q0_rows = [row for row in result["state_records"] if row["order"] == "q1q0"]
    assert len(q1q0_rows) == 4
    assert all(row["pass"] is True for row in q1q0_rows)


def test_stage218_reports_full_replacement_phasewrap_advantage() -> None:
    result = run_stage218_full_replacement_hardware_metric_interpreter()

    assert result["decision"] == "FULL_REPLACEMENT_HARDWARE_POSITIVE_PHASEWRAP_ADVANTAGE"
    assert result["blockers"] == []
    assert result["bitstring_order"] == "q1q0"
    assert result["packet_template_count"] == 20
    assert result["comparison_group_count"] == 4
    assert result["full_replacement_positive_seed_pair_count"] == 2
    assert all(row["stable_full_replacement_hardware_target"] is True for row in result["comparison_summary"])

    by_lane = {row["source_lane_id"]: row for row in result["comparison_summary"]}
    assert set(by_lane) == {
        "ibm_cx_seed314_rows16_shots4096",
        "ibm_cx_seed577_rows16_shots4096",
        "ibm_product_seed314_rows16_shots4096",
        "ibm_product_seed577_rows16_shots4096",
    }
    assert by_lane["ibm_cx_seed314_rows16_shots4096"]["phasewrap_normalized_noise_sensitivity_delta"] == 0.056685851326
    assert by_lane["ibm_cx_seed577_rows16_shots4096"]["phasewrap_normalized_noise_sensitivity_delta"] == 0.058017065101
    assert by_lane["ibm_product_seed314_rows16_shots4096"]["phasewrap_normalized_noise_sensitivity_delta"] == 0.027709086969
    assert by_lane["ibm_product_seed577_rows16_shots4096"]["phasewrap_normalized_noise_sensitivity_delta"] == 0.037817399951
