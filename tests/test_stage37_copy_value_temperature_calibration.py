from __future__ import annotations

import json

import numpy as np

from qrope.stage14_attention_readout import make_stage14_examples, split_examples
from qrope.stage36_copy_value_bridge import train_copy_value_bridge
from qrope.stage37_copy_value_temperature_calibration import (
    evaluate_copy_value_with_temperature,
    run_stage37_benchmark,
    select_copy_value_temperature,
    write_stage37_outputs,
)


def test_stage37_temperature_selection_uses_grid() -> None:
    splits = split_examples(make_stage14_examples(seeds=(401,), context_lengths=(128, 256, 512, 1024), examples_per_task_length=1))
    training = train_copy_value_bridge(splits["train"], "rope_relative", model_seed=3707, epochs=3)
    params = {key: np.array(value, dtype=float) for key, value in training["params"].items()}
    calibration = select_copy_value_temperature(splits["validation"], "rope_relative", params, grid=(0.5, 1.0, 2.0))
    assert calibration["selected_temperature"] in {0.5, 1.0, 2.0}
    assert [row["temperature"] for row in calibration["validation_table"]] == [0.5, 1.0, 2.0]
    assert calibration["selection_metric"] == "validation_loss_then_ece"


def test_stage37_evaluation_reports_temperature_metrics() -> None:
    splits = split_examples(make_stage14_examples(seeds=(401,), context_lengths=(128, 256, 512, 1024), examples_per_task_length=1))
    training = train_copy_value_bridge(splits["train"], "phasewrap_multiscale_adapter", model_seed=3707, epochs=3)
    metrics = evaluate_copy_value_with_temperature(
        splits["test"],
        "phasewrap_multiscale_adapter",
        {key: np.array(value, dtype=float) for key, value in training["params"].items()},
        0.5,
    )
    assert metrics["row_count"] == 3
    assert metrics["temperature"] == 0.5
    assert 0.0 <= metrics["top1_accuracy"] <= 1.0
    assert 0.0 < metrics["mrr"] <= 1.0
    assert 0.0 < metrics["mean_target_value_probability"] <= 1.0
    assert 0.0 < metrics["mean_target_attention_probability"] <= 1.0


def test_stage37_benchmark_and_outputs(tmp_path) -> None:
    result = run_stage37_benchmark(
        data_seeds=(401,),
        model_seeds=(3707, 3719),
        context_lengths=(128, 256, 512, 1024),
        examples_per_task_length=1,
        epochs=3,
        method_names=("rope_relative", "phasewrap_multiscale_adapter"),
        temperature_grid=(0.5, 1.0, 2.0),
    )
    assert result["stage"] == "stage37_copy_value_temperature_calibration"
    assert result["train_row_count"] == 6
    assert result["test_row_count"] == 3
    assert len(result["run_table"]) == 4
    assert len(result["task_table"]) == 12
    assert "delta_target_value_probability_mean" in result["table"][0]
    assert "temperature_grid" in result["model"]
    assert "a claim that PhaseWrap-RoPE is a validated RoPE replacement" in result["claim_boundary"]["excluded"]

    paths = write_stage37_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    assert set(paths) == {"manifest", "results", "summary_csv", "per_run_csv", "task_summary_csv", "weak_runs"}
    assert manifest["stage"] == "stage37_copy_value_temperature_calibration"
    assert saved["selection_table"] == result["selection_table"]
