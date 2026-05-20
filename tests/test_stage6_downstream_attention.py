from __future__ import annotations

import json

from qrope.stage6_downstream_attention import (
    MODEL_NAMES,
    content_score,
    evaluate_downstream_predictions,
    leakage_diagnostics,
    make_downstream_splits,
    run_downstream_attention,
    token_pair_features,
    write_stage6_outputs,
)


def test_content_score_is_deterministic_and_bounded() -> None:
    assert content_score("A", "A") == 1.0
    assert content_score("A", "B") == 0.72
    assert 0.0 <= content_score("C", "A") <= 1.0


def test_downstream_splits_are_deterministic() -> None:
    first = make_downstream_splits(42)
    second = make_downstream_splits(42)
    assert first == second
    assert len(first["train"]) == 448
    assert len(first["test"]) == 152


def test_token_pair_features_have_fixed_width() -> None:
    row = make_downstream_splits(42)["train"][0]
    features = token_pair_features(row)
    assert len(features) == 16
    assert sum(features) == 1.0


def test_leakage_diagnostics_show_delta_only_baselines_are_not_exact() -> None:
    rows = make_downstream_splits(42)["train"] + make_downstream_splits(42)["validation"] + make_downstream_splits(42)["test"]
    diagnostics = leakage_diagnostics(rows)
    assert diagnostics["mod24_not_exact_pass"] is True
    assert diagnostics["phase_features_not_exact_pass"] is True
    assert diagnostics["token_pair_variation_present"] is True


def test_evaluate_downstream_predictions_perfect_scores() -> None:
    rows = make_downstream_splits(42)["test"][:8]
    predictions = [row.target for row in rows]
    metrics = evaluate_downstream_predictions(rows, predictions)
    assert metrics["mae"] == 0.0
    assert metrics["top1_accuracy"] == 1.0


def test_run_downstream_attention_is_deterministic_and_complete() -> None:
    first = run_downstream_attention(42)
    second = run_downstream_attention(42)
    assert first["table"] == second["table"]
    assert [result["name"] for result in first["results"]] == list(MODEL_NAMES)
    assert first["best_method"] == "phasewrap_rope_attention"


def test_stage6_outputs_are_written(tmp_path) -> None:
    result = run_downstream_attention(42)
    paths = write_stage6_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    assert set(paths) == {"manifest", "results", "summary_csv"}
    assert manifest["stage"] == "stage6_downstream_attention"
    assert saved["table"] == result["table"]
    assert (tmp_path / "summary.csv").exists()
