from __future__ import annotations

import json

import numpy as np

from qrope.stage12_ruler_retrieval import make_stage12_examples
from qrope.stage13_positional_adapter import split_examples
from qrope.stage28_ruler_attention_bridge import (
    evaluate_attention_bridge,
    run_stage28_benchmark,
    train_attention_bridge,
    write_stage28_outputs,
)


def test_stage28_training_is_deterministic() -> None:
    rows = split_examples(make_stage12_examples(seeds=(401,), context_lengths=(128, 256, 512, 1024), examples_per_task_length=1))["train"]
    first = train_attention_bridge(rows, "alibi", model_seed=2801, epochs=3)
    second = train_attention_bridge(rows, "alibi", model_seed=2801, epochs=3)
    assert first["training_history"] == second["training_history"]
    assert first["param_sha256"] == second["param_sha256"]
    assert first["params"] == second["params"]


def test_stage28_evaluation_reports_required_metrics() -> None:
    splits = split_examples(make_stage12_examples(seeds=(401,), context_lengths=(128, 256, 512, 1024), examples_per_task_length=1))
    training = train_attention_bridge(splits["train"], "phasewrap_distance_adapter", model_seed=2801, epochs=3)
    metrics = evaluate_attention_bridge(
        splits["test"],
        "phasewrap_distance_adapter",
        {key: np.array(value, dtype=float) for key, value in training["params"].items()},
    )
    assert metrics["row_count"] == 3
    assert 0.0 <= metrics["top1_accuracy"] <= 1.0
    assert 0.0 < metrics["mrr"] <= 1.0
    assert 0.0 < metrics["mean_target_probability"] <= 1.0
    assert 0.0 <= metrics["expected_calibration_error"] <= 1.0
    assert 0.0 <= metrics["mean_top1_confidence"] <= 1.0
    assert metrics["target_probability_mae"] == round(1.0 - metrics["mean_target_probability"], 6)


def test_stage28_benchmark_and_outputs(tmp_path) -> None:
    result = run_stage28_benchmark(
        data_seeds=(401,),
        model_seeds=(2801, 2819),
        context_lengths=(128, 256, 512, 1024),
        examples_per_task_length=1,
        epochs=3,
        method_names=("alibi", "phasewrap_distance_adapter"),
    )
    assert result["stage"] == "stage28_ruler_attention_bridge"
    assert result["train_row_count"] == 6
    assert result["test_row_count"] == 3
    assert len(result["run_table"]) == 4
    assert len(result["task_table"]) == 12
    assert len(result["table"]) == 2
    assert "expected_calibration_error_mean" in result["table"][0]
    assert "target_probability_mae_mean" in result["table"][0]
    assert result["best_method_by_test_top1_mrr"] in {"alibi", "phasewrap_distance_adapter"}
    assert "a claim that PhaseWrap-RoPE is a validated RoPE replacement" in result["claim_boundary"]["excluded"]

    paths = write_stage28_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    assert set(paths) == {"manifest", "results", "summary_csv", "per_run_csv", "task_summary_csv", "weak_runs"}
    assert manifest["stage"] == "stage28_ruler_attention_bridge"
    assert saved["selection_table"] == result["selection_table"]
