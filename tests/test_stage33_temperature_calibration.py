from __future__ import annotations

import json

import numpy as np

from qrope.stage12_ruler_retrieval import make_stage12_examples
from qrope.stage13_positional_adapter import split_examples
from qrope.stage32_full_context_feature_bridge import train_full_context_bridge
from qrope.stage33_temperature_calibration import (
    evaluate_with_temperature,
    run_stage33_benchmark,
    select_temperature,
    write_stage33_outputs,
)


def test_stage33_temperature_selection_uses_grid() -> None:
    splits = split_examples(make_stage12_examples(seeds=(401,), context_lengths=(128, 256, 512, 1024), examples_per_task_length=1))
    training = train_full_context_bridge(splits["train"], "rope_relative", model_seed=3203, epochs=3)
    params = {key: np.array(value, dtype=float) for key, value in training["params"].items()}
    selected = select_temperature(splits["validation"], "rope_relative", params, grid=(0.5, 1.0, 2.0))
    assert selected["selected_temperature"] in {0.5, 1.0, 2.0}
    assert len(selected["validation_table"]) == 3


def test_stage33_evaluation_reports_required_metrics() -> None:
    splits = split_examples(make_stage12_examples(seeds=(401,), context_lengths=(128, 256, 512, 1024), examples_per_task_length=1))
    training = train_full_context_bridge(splits["train"], "phasewrap_multiscale_adapter", model_seed=3203, epochs=3)
    metrics = evaluate_with_temperature(
        splits["test"],
        "phasewrap_multiscale_adapter",
        {key: np.array(value, dtype=float) for key, value in training["params"].items()},
        1.0,
    )
    assert metrics["row_count"] == 3
    assert 0.0 <= metrics["top1_accuracy"] <= 1.0
    assert 0.0 < metrics["mrr"] <= 1.0
    assert 0.0 < metrics["mean_target_probability"] <= 1.0
    assert 0.0 <= metrics["expected_calibration_error"] <= 1.0


def test_stage33_benchmark_and_outputs(tmp_path) -> None:
    result = run_stage33_benchmark(
        data_seeds=(401,),
        model_seeds=(3203, 3217),
        context_lengths=(128, 256, 512, 1024),
        examples_per_task_length=1,
        epochs=3,
        method_names=("rope_relative", "phasewrap_multiscale_adapter"),
    )
    assert result["stage"] == "stage33_temperature_calibration"
    assert result["train_row_count"] == 6
    assert result["validation_row_count"] == 3
    assert result["test_row_count"] == 3
    assert len(result["run_table"]) == 4
    assert len(result["calibration_records"]) == 4
    assert "selected_temperature_mean" in result["table"][0]
    assert "delta_target_probability_mean" in result["table"][0]
    assert "uncalibrated_mean_target_probability" in result["run_table"][0]
    assert "a claim that PhaseWrap-RoPE is a validated RoPE replacement" in result["claim_boundary"]["excluded"]

    paths = write_stage33_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    assert set(paths) == {"manifest", "results", "summary_csv", "per_run_csv", "weak_runs"}
    assert manifest["stage"] == "stage33_temperature_calibration"
    assert saved["selection_table"] == result["selection_table"]
