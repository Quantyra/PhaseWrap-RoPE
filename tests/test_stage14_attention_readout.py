from __future__ import annotations

import json

import numpy as np

from qrope.stage14_attention_readout import (
    METHOD_NAMES,
    VALUE_VOCAB_SIZE,
    evaluate_readout,
    make_stage14_examples,
    run_stage14_benchmark,
    split_examples,
    train_readout,
    write_stage14_outputs,
)


def test_stage14_examples_are_deterministic_key_value_rows() -> None:
    first = make_stage14_examples(seeds=(401,), context_lengths=(128,), examples_per_task_length=1)
    second = make_stage14_examples(seeds=(401,), context_lengths=(128,), examples_per_task_length=1)
    assert first == second
    assert len(first) == 3
    for row in first:
        assert len(row.key_positions) == len(row.candidate_values)
        assert set(row.target_positions).issubset(set(row.key_positions))
        assert set(row.target_values).issubset(set(row.candidate_values))
        assert all(0 < value < VALUE_VOCAB_SIZE for value in row.candidate_values)


def test_split_examples_uses_train_validation_test_lengths() -> None:
    rows = make_stage14_examples(seeds=(401,), context_lengths=(128, 256, 512, 1024), examples_per_task_length=1)
    splits = split_examples(rows)
    assert {row.sequence_length for row in splits["train"]} == {128, 256}
    assert {row.sequence_length for row in splits["validation"]} == {512}
    assert {row.sequence_length for row in splits["test"]} == {1024}


def test_train_and_evaluate_readout_smoke() -> None:
    rows = make_stage14_examples(seeds=(401,), context_lengths=(128, 256, 512, 1024), examples_per_task_length=1)
    splits = split_examples(rows)
    training = train_readout(splits["train"], "phasewrap_distance_adapter", epochs=4)
    metrics = evaluate_readout(splits["test"], "phasewrap_distance_adapter", np.array(training["weights"], dtype=float))
    assert len(training["training_history"]) == 4
    assert metrics["row_count"] == 3
    assert 0.0 <= metrics["top1_accuracy"] <= 1.0
    assert metrics["mrr_ci_low"] <= metrics["mrr"] <= metrics["mrr_ci_high"]


def test_run_stage14_benchmark_is_complete() -> None:
    result = run_stage14_benchmark(seeds=(401,), context_lengths=(128, 256, 512, 1024), examples_per_task_length=1, epochs=4)
    assert result["stage"] == "stage14_attention_readout"
    assert result["no_hardware_submission"] is True
    assert [row["method"] for row in result["table"]] == list(METHOD_NAMES)
    assert result["best_method_by_top1_mrr"] in METHOD_NAMES
    assert result["test_row_count"] == 3
    assert "a claim that PhaseWrap-RoPE is a validated RoPE replacement" in result["claim_boundary"]["excluded"]


def test_stage14_outputs_are_written(tmp_path) -> None:
    result = run_stage14_benchmark(seeds=(401,), context_lengths=(128, 256, 512, 1024), examples_per_task_length=1, epochs=4)
    paths = write_stage14_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    assert set(paths) == {"manifest", "results", "summary_csv", "task_summary_csv"}
    assert manifest["stage"] == "stage14_attention_readout"
    assert saved["table"] == result["table"]
    assert (tmp_path / "summary.csv").exists()
    assert (tmp_path / "task_summary.csv").exists()
