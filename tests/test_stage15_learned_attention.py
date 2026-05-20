from __future__ import annotations

import json

import numpy as np

from qrope.stage14_attention_readout import make_stage14_examples, split_examples
from qrope.stage15_learned_attention import (
    METHOD_NAMES,
    evaluate_learned_attention,
    run_stage15_benchmark,
    train_learned_attention,
    write_stage15_outputs,
)


def test_train_and_evaluate_learned_attention_smoke() -> None:
    rows = make_stage14_examples(seeds=(401,), context_lengths=(128, 256, 512, 1024), examples_per_task_length=1)
    splits = split_examples(rows)
    training = train_learned_attention(splits["train"], "phasewrap_distance_adapter", epochs=4)
    params = {key: np.array(value, dtype=float) for key, value in training["params"].items()}
    metrics = evaluate_learned_attention(splits["test"], "phasewrap_distance_adapter", params)
    assert len(training["training_history"]) == 4
    assert metrics["row_count"] == 3
    assert 0.0 <= metrics["top1_accuracy"] <= 1.0
    assert metrics["mrr_ci_low"] <= metrics["mrr"] <= metrics["mrr_ci_high"]


def test_run_stage15_benchmark_is_complete() -> None:
    result = run_stage15_benchmark(seeds=(401,), context_lengths=(128, 256, 512, 1024), examples_per_task_length=1, epochs=4)
    assert result["stage"] == "stage15_learned_attention"
    assert result["no_hardware_submission"] is True
    assert [row["method"] for row in result["table"]] == list(METHOD_NAMES)
    assert result["best_method_by_top1_mrr"] in METHOD_NAMES
    assert result["test_row_count"] == 3
    assert result["model"]["type"] == "one_hidden_layer_attention_scorer_over_positional_features"
    assert "a claim that PhaseWrap-RoPE is a validated RoPE replacement" in result["claim_boundary"]["excluded"]


def test_stage15_outputs_are_written(tmp_path) -> None:
    result = run_stage15_benchmark(seeds=(401,), context_lengths=(128, 256, 512, 1024), examples_per_task_length=1, epochs=4)
    paths = write_stage15_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    assert set(paths) == {"manifest", "results", "summary_csv", "task_summary_csv"}
    assert manifest["stage"] == "stage15_learned_attention"
    assert saved["table"] == result["table"]
    assert (tmp_path / "summary.csv").exists()
    assert (tmp_path / "task_summary.csv").exists()
