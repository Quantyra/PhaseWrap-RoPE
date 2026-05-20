from __future__ import annotations

import json

from qrope.automated_stage_gates import generate_transformer_phase_wrap_attention_bundle
from qrope.stage5_attention_baselines import (
    BASELINE_NAMES,
    context_metrics,
    delta_feature_matrix,
    evaluate_predictions,
    mod24_key,
    phase_wrap_predictions,
    ridge_feature_matrix,
    rope_attention_predictions,
    run_attention_baselines,
    sinusoidal_attention_predictions,
    train_lookup_mod24,
    write_stage5_outputs,
)


def test_mod24_key_uses_reference_minus_candidate_delta() -> None:
    row = generate_transformer_phase_wrap_attention_bundle(42).test[0]
    assert mod24_key(row) == (row.reference_delta - row.candidate_delta) % 24


def test_ridge_feature_matrix_order() -> None:
    row = generate_transformer_phase_wrap_attention_bundle(42).test[0]
    matrix = ridge_feature_matrix([row])
    assert matrix.shape == (1, 4)
    assert matrix[0].tolist() == [1.0, row.m8, row.m12, row.m8 * row.m12]


def test_delta_feature_matrix_is_deterministic() -> None:
    row = generate_transformer_phase_wrap_attention_bundle(42).test[0]
    first = delta_feature_matrix([row])
    second = delta_feature_matrix([row])
    assert first.tolist() == second.tolist()
    assert first.shape == (1, 7)


def test_rope_and_sinusoidal_predictions_are_bounded_and_deterministic() -> None:
    rows = generate_transformer_phase_wrap_attention_bundle(42).test[:8]
    assert rope_attention_predictions(rows) == rope_attention_predictions(rows)
    assert sinusoidal_attention_predictions(rows) == sinusoidal_attention_predictions(rows)
    assert all(0.0 <= value <= 1.0 for value in rope_attention_predictions(rows))
    assert all(0.0 <= value <= 1.0 for value in sinusoidal_attention_predictions(rows))


def test_context_metrics_identify_perfect_top1() -> None:
    rows = generate_transformer_phase_wrap_attention_bundle(42).test[:8]
    predictions = [row.label for row in rows]
    metrics = context_metrics(rows, predictions)
    assert metrics["top1_accuracy"] == 1.0
    assert metrics["mrr"] == 1.0
    assert metrics["ndcg_at_4"] == 1.0


def test_evaluate_predictions_reports_core_metrics() -> None:
    rows = generate_transformer_phase_wrap_attention_bundle(42).test[:8]
    metrics = evaluate_predictions(rows, phase_wrap_predictions(rows))
    assert metrics["row_count"] == 8
    assert metrics["mae"] == 0.0
    assert metrics["rank_correlation"] == 1.0


def test_lookup_mod24_model_contains_bucket_means() -> None:
    rows = generate_transformer_phase_wrap_attention_bundle(42).train
    model = train_lookup_mod24(rows)
    assert "global_mean" in model
    assert len(model["bucket_means"]) <= 24


def test_run_attention_baselines_is_deterministic() -> None:
    first = run_attention_baselines(seed=42)
    second = run_attention_baselines(seed=42)
    assert first["table"] == second["table"]
    assert [item["name"] for item in first["baselines"]] == list(BASELINE_NAMES)


def test_stage5_output_files_are_written(tmp_path) -> None:
    result = run_attention_baselines(seed=42)
    paths = write_stage5_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    assert set(paths) == {"manifest", "results", "summary_csv"}
    assert manifest["stage"] == "stage5_attention_baselines"
    assert saved["table"] == result["table"]
    assert (tmp_path / "summary.csv").exists()
