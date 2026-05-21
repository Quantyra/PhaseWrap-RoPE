from __future__ import annotations

import json

from qrope.stage72_phase_cued_bias_tie_support_audit import run_stage72_audit, write_stage72_outputs


def test_stage72_smoke_reports_tie_support_decision() -> None:
    result = run_stage72_audit(
        seeds=(307,),
        examples_per_length=1,
        method_names=("no_position", "rope_relative", "phasewrap_bias"),
    )
    assert result["stage"] == "stage72_phase_cued_bias_tie_support_audit"
    assert result["status"] == "completed"
    assert result["tasks"] == ["phase_cued_retrieval"]
    assert result["failed_runs"] == []
    assert result["decision"]["decision"] in {
        "PHASE_CUED_TIE_SUPPORT_SOLVES_REVIEW_REQUIRED",
        "PHASE_CUED_PHASEWRAP_TIE_SUPPORT_WITH_AMBIGUITY",
        "PHASE_CUED_TARGET_NOT_IN_PHASEWRAP_MAX_BIAS_SUPPORT",
    }


def test_stage72_preserves_phasewrap_max_tie_miss_and_no_position_ambiguity() -> None:
    result = run_stage72_audit(
        seeds=(307,),
        examples_per_length=1,
        method_names=("no_position", "phasewrap_bias"),
    )
    rows = {row["method"]: row for row in result["aggregate_table"]}
    assert rows["no_position"]["test_target_in_max_tie_rate_mean"] == 1.0
    assert rows["no_position"]["test_mean_max_tie_count_mean"] > 10.0
    assert rows["phasewrap_bias"]["test_target_in_max_tie_rate_mean"] == 0.0
    assert rows["phasewrap_bias"]["test_top1_accuracy_mean"] < 0.5


def test_stage72_outputs_are_written(tmp_path) -> None:
    result = run_stage72_audit(
        seeds=(307,),
        examples_per_length=1,
        method_names=("no_position",),
    )
    paths = write_stage72_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    assert set(paths) == {"manifest", "result", "summary_csv", "per_run_csv", "per_example_csv", "failed_runs"}
    assert manifest["stage"] == "stage72_phase_cued_bias_tie_support_audit"
    assert saved["method_names"] == ["no_position"]
    assert (tmp_path / "per_example_results.csv").exists()
