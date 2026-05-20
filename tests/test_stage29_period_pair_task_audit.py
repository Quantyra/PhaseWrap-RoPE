from __future__ import annotations

import json

from qrope.stage12_ruler_retrieval import make_stage12_examples
from qrope.stage29_period_pair_task_audit import evaluate_period_pair, run_stage29_audit, write_stage29_outputs


def test_stage29_period_pair_evaluation_reports_alias_metrics() -> None:
    rows = make_stage12_examples(seeds=(401,), context_lengths=(128,), examples_per_task_length=1)
    result = evaluate_period_pair(rows, (8, 12))
    assert result["period_pair"] == "8/12"
    assert result["fundamental_period"] == 24
    assert result["row_count"] == 3
    assert 0.0 <= result["top1_accuracy"] <= 1.0
    assert 0.0 <= result["target_top_tie_rate"] <= 1.0
    assert result["mean_top_score_tie_count"] >= 1.0
    assert result["mean_target_score_tie_count"] >= 1.0


def test_stage29_audit_compares_period_pairs() -> None:
    result = run_stage29_audit(
        seeds=(401,),
        local_context_lengths=(128, 256),
        long_context_lengths=(512,),
        examples_per_task_length=1,
        period_pairs=((8, 12), (10, 16)),
    )
    assert result["stage"] == "stage29_period_pair_task_audit"
    assert result["local_row_count"] == 6
    assert result["long_row_count"] == 3
    assert len(result["local_table"]) == 2
    assert len(result["long_table"]) == 2
    assert len(result["task_table"]) == 6
    assert len(result["length_table"]) == 2
    assert result["best_local_period_pair"] in {"8/12", "10/16"}
    assert "a proof that any period pair is globally optimal" in result["claim_boundary"]["excluded"]


def test_stage29_outputs_are_written(tmp_path) -> None:
    result = run_stage29_audit(
        seeds=(401,),
        local_context_lengths=(128,),
        long_context_lengths=(512,),
        examples_per_task_length=1,
        period_pairs=((8, 12),),
    )
    paths = write_stage29_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    assert set(paths) == {"manifest", "results", "local_summary_csv", "long_summary_csv", "task_summary_csv", "length_summary_csv"}
    assert manifest["stage"] == "stage29_period_pair_task_audit"
    assert saved["default_pair_summary"] == result["default_pair_summary"]
