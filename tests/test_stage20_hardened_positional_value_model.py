from __future__ import annotations

import json

import numpy as np

from qrope.stage14_attention_readout import make_stage14_examples, split_examples
from qrope.stage20_hardened_positional_value_model import (
    evaluate_hardened_positional_value_model,
    run_stage20_benchmark,
    train_hardened_positional_value_model,
    write_stage20_outputs,
)


def test_train_hardened_positional_value_model_smoke() -> None:
    rows = make_stage14_examples(seeds=(401,), context_lengths=(128, 256, 512, 1024), examples_per_task_length=1)
    splits = split_examples(rows)
    training = train_hardened_positional_value_model(splits["train"], "phasewrap_distance_adapter", epochs=4, embed_dim=8)
    params = {key: np.array(value, dtype=float) for key, value in training["params"].items()}
    metrics = evaluate_hardened_positional_value_model(splits["test"], "phasewrap_distance_adapter", params, split_name="test")
    assert training["optimizer"] == "full_batch_adam"
    assert len(training["training_history"]) == 4
    assert metrics["row_count"] == 3
    assert 0.0 <= metrics["top1_accuracy"] <= 1.0


def test_run_stage20_benchmark_is_complete() -> None:
    result = run_stage20_benchmark(
        seeds=(401,),
        context_lengths=(128, 256, 512, 1024),
        examples_per_task_length=1,
        epochs=4,
        method_names=("no_position", "phasewrap_distance_adapter"),
    )
    assert result["stage"] == "stage20_hardened_positional_value_model"
    assert result["no_hardware_submission"] is True
    assert set(result["method_names"]) == {"no_position", "phasewrap_distance_adapter"}
    assert {row["split"] for row in result["table"]} == {"train", "validation", "test"}
    assert result["best_method_by_test_top1_mrr"] in {"no_position", "phasewrap_distance_adapter"}
    assert "a claim that PhaseWrap-RoPE is a validated RoPE replacement" in result["claim_boundary"]["excluded"]


def test_stage20_outputs_are_written_without_params(tmp_path) -> None:
    result = run_stage20_benchmark(
        seeds=(401,),
        context_lengths=(128, 256, 512, 1024),
        examples_per_task_length=1,
        epochs=4,
        method_names=("no_position", "phasewrap_distance_adapter"),
    )
    paths = write_stage20_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    assert set(paths) == {"manifest", "results", "summary_csv", "task_summary_csv"}
    assert manifest["stage"] == "stage20_hardened_positional_value_model"
    assert saved["table"] == result["table"]
    assert "params" not in saved["training_records"][0]
