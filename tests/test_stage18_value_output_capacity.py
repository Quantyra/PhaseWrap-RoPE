from __future__ import annotations

import json

import numpy as np

from qrope.stage14_attention_readout import make_stage14_examples, split_examples
from qrope.stage18_value_output_capacity import (
    evaluate_capacity_model,
    run_stage18_benchmark,
    train_capacity_model,
    write_stage18_outputs,
)


def test_train_capacity_model_smoke() -> None:
    rows = make_stage14_examples(seeds=(401,), context_lengths=(128, 256, 512, 1024), examples_per_task_length=1)
    splits = split_examples(rows)
    training = train_capacity_model(splits["train"], "teacher_forced_attention", epochs=4)
    params = {key: np.array(value, dtype=float) for key, value in training["params"].items()}
    metrics = evaluate_capacity_model(splits["test"], "teacher_forced_attention", params)
    assert len(training["training_history"]) == 4
    assert metrics["row_count"] == 3
    assert 0.0 <= metrics["top1_accuracy"] <= 1.0


def test_run_stage18_benchmark_is_complete() -> None:
    result = run_stage18_benchmark(seeds=(401,), context_lengths=(128, 256, 512, 1024), examples_per_task_length=1, epochs=4)
    assert result["stage"] == "stage18_value_output_capacity"
    assert result["no_hardware_submission"] is True
    assert {row["mode"] for row in result["table"]} == {"uniform_attention", "teacher_forced_attention"}
    assert {row["split"] for row in result["table"]} == {"train", "validation", "test"}
    assert "a claim that PhaseWrap-RoPE is a validated RoPE replacement" in result["claim_boundary"]["excluded"]


def test_stage18_outputs_are_written(tmp_path) -> None:
    result = run_stage18_benchmark(seeds=(401,), context_lengths=(128, 256, 512, 1024), examples_per_task_length=1, epochs=4)
    paths = write_stage18_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    assert set(paths) == {"manifest", "results", "summary_csv"}
    assert manifest["stage"] == "stage18_value_output_capacity"
    assert saved["table"] == result["table"]
    assert "params" not in saved["training_records"][0]
