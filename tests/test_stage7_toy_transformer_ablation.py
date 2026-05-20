from __future__ import annotations

import json

import numpy as np

from qrope.stage7_toy_transformer_ablation import (
    LAYER_COUNT,
    MODEL_NAMES,
    evaluate_toy_transformer_model,
    four_layer_attention_distribution,
    make_toy_transformer_splits,
    run_toy_transformer_ablation,
    write_stage7_outputs,
)


def test_toy_transformer_splits_are_deterministic() -> None:
    first = make_toy_transformer_splits(42)
    second = make_toy_transformer_splits(42)
    assert first == second
    assert {row.sequence_length for row in first["train"]} == {16, 24}
    assert {row.sequence_length for row in first["test"]} == {48, 64}


def test_four_layer_attention_distribution_is_probability_vector() -> None:
    row = make_toy_transformer_splits(42)["test"][0]
    distribution = four_layer_attention_distribution(row, "phasewrap_rope_4layer", 2.0)
    assert distribution.shape == (row.query_pos,)
    assert np.isclose(float(np.sum(distribution)), 1.0)
    assert np.all(distribution >= 0.0)


def test_evaluate_toy_transformer_model_reports_expected_fields() -> None:
    rows = make_toy_transformer_splits(42)["validation"]
    metrics = evaluate_toy_transformer_model(rows, "phasewrap_rope_4layer", 2.0)
    assert metrics["row_count"] == len(rows)
    assert metrics["sequence_length_min"] == 32
    assert 0.0 <= metrics["top1_accuracy"] <= 1.0


def test_run_toy_transformer_ablation_is_deterministic_and_complete() -> None:
    first = run_toy_transformer_ablation(42)
    second = run_toy_transformer_ablation(42)
    assert first["table"] == second["table"]
    assert [row["method"] for row in first["table"]] == list(MODEL_NAMES)
    assert first["best_method"] in MODEL_NAMES
    assert all(row["layers"] == LAYER_COUNT for row in first["table"])


def test_stage7_outputs_are_written(tmp_path) -> None:
    result = run_toy_transformer_ablation(42)
    paths = write_stage7_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    assert set(paths) == {"manifest", "results", "summary_csv"}
    assert manifest["stage"] == "stage7_toy_transformer_ablation"
    assert saved["table"] == result["table"]
    assert (tmp_path / "summary.csv").exists()
