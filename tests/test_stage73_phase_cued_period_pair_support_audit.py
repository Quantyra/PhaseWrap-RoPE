from __future__ import annotations

import json

from qrope.stage73_phase_cued_period_pair_support_audit import run_stage73_audit, write_stage73_outputs


def test_stage73_smoke_reports_period_pair_decision() -> None:
    result = run_stage73_audit(
        seeds=(307,),
        examples_per_length=1,
        period_pairs=((8, 12), (8, 24)),
    )
    assert result["stage"] == "stage73_phase_cued_period_pair_support_audit"
    assert result["status"] == "completed"
    assert result["tasks"] == ["phase_cued_retrieval"]
    assert result["failed_runs"] == []
    assert result["decision"]["decision"] in {
        "PHASE_CUED_PERIOD_PAIR_SOLVES_REVIEW_REQUIRED",
        "PHASE_CUED_PERIOD_PAIR_SUPPORT_WITH_AMBIGUITY",
        "PHASE_CUED_PERIOD_PAIR_SWEEP_DOES_NOT_REPAIR_SUPPORT",
    }


def test_stage73_default_pair_preserves_phase_cued_support_miss() -> None:
    result = run_stage73_audit(
        seeds=(307,),
        examples_per_length=1,
        period_pairs=((8, 12),),
    )
    row = result["aggregate_table"][0]
    assert row["period_pair"] == "8/12"
    assert row["test_target_in_max_support_rate_mean"] == 0.0
    assert result["decision"]["default_8_12_support_rate"] == 0.0


def test_stage73_outputs_are_written(tmp_path) -> None:
    result = run_stage73_audit(
        seeds=(307,),
        examples_per_length=1,
        period_pairs=((8, 12),),
    )
    paths = write_stage73_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    assert set(paths) == {"manifest", "result", "summary_csv", "per_run_csv", "per_example_csv", "failed_runs"}
    assert manifest["stage"] == "stage73_phase_cued_period_pair_support_audit"
    assert saved["period_pairs"] == [[8, 12]]
    assert (tmp_path / "per_example_results.csv").exists()
