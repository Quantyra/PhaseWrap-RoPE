from __future__ import annotations

import json

import numpy as np

from qrope.stage13_positional_adapter import (
    METHOD_NAMES,
    evaluate_adapter,
    positional_features,
    run_stage13_benchmark,
    split_examples,
    train_adapter,
    write_stage13_outputs,
)
from qrope.stage12_ruler_retrieval import make_stage12_examples


def test_positional_features_are_deterministic_and_sized() -> None:
    example = make_stage12_examples(seeds=(401,), context_lengths=(128,), examples_per_task_length=1)[0]
    for method_name in METHOD_NAMES:
        first = positional_features(example, method_name)
        second = positional_features(example, method_name)
        assert np.array_equal(first, second)
        assert first.shape[0] == len(example.key_positions)
        assert first.shape[1] >= 1


def test_split_examples_uses_declared_lengths() -> None:
    examples = make_stage12_examples(seeds=(401,), context_lengths=(128, 256, 512, 1024), examples_per_task_length=1)
    splits = split_examples(examples)
    assert {example.sequence_length for example in splits["train"]} == {128, 256}
    assert {example.sequence_length for example in splits["validation"]} == {512}
    assert {example.sequence_length for example in splits["test"]} == {1024}


def test_train_and_evaluate_adapter_smoke() -> None:
    examples = make_stage12_examples(seeds=(401,), context_lengths=(128, 256, 512, 1024), examples_per_task_length=1)
    splits = split_examples(examples)
    training = train_adapter(splits["train"], "phasewrap_distance_adapter", epochs=4)
    metrics = evaluate_adapter(splits["test"], "phasewrap_distance_adapter", np.array(training["weights"], dtype=float))
    assert len(training["training_history"]) == 4
    assert metrics["row_count"] == 3
    assert 0.0 <= metrics["top1_accuracy"] <= 1.0
    assert metrics["mrr_ci_low"] <= metrics["mrr"] <= metrics["mrr_ci_high"]


def test_run_stage13_benchmark_is_complete() -> None:
    result = run_stage13_benchmark(seeds=(401,), context_lengths=(128, 256, 512, 1024), examples_per_task_length=1, epochs=4)
    assert result["stage"] == "stage13_positional_adapter"
    assert result["no_hardware_submission"] is True
    assert [row["method"] for row in result["table"]] == list(METHOD_NAMES)
    assert result["best_method_by_top1_mrr"] in METHOD_NAMES
    assert result["test_row_count"] == 3
    assert "a claim that PhaseWrap-RoPE is a validated RoPE replacement" in result["claim_boundary"]["excluded"]


def test_stage13_outputs_are_written(tmp_path) -> None:
    result = run_stage13_benchmark(seeds=(401,), context_lengths=(128, 256, 512, 1024), examples_per_task_length=1, epochs=4)
    paths = write_stage13_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    assert set(paths) == {"manifest", "results", "summary_csv", "task_summary_csv"}
    assert manifest["stage"] == "stage13_positional_adapter"
    assert saved["table"] == result["table"]
    assert (tmp_path / "summary.csv").exists()
    assert (tmp_path / "task_summary.csv").exists()
