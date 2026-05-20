from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from .automated_stage_gates import AttentionRow, generate_transformer_phase_wrap_attention_bundle
from .stage5_attention_baselines import (
    context_metrics,
    mean_absolute_error,
    mod24_key,
    rank_correlation,
    ridge_feature_matrix,
    rope_attention_predictions,
    sinusoidal_attention_predictions,
)


STAGE6_SCHEMA_VERSION = "qrope_stage6_downstream_attention_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage6_downstream_attention"
TOKEN_ORDER = ("A", "B", "C", "D")
MODEL_NAMES = (
    "phasewrap_rope_attention",
    "rope_attention",
    "alibi_attention",
    "sinusoidal_attention",
    "no_position_attention",
    "lookup_mod24_baseline",
    "classical_m8_m12_product_baseline",
)


@dataclass(frozen=True)
class DownstreamRow:
    context_id: str
    split: str
    slot: int
    query_token: str
    candidate_token: str
    reference_delta: int
    candidate_delta: int
    m8: float
    m12: float
    phase_product: float
    phase_label: float
    content_score: float
    target: float


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def token_pair_features(row: DownstreamRow) -> list[float]:
    return [1.0 if row.query_token == q and row.candidate_token == c else 0.0 for q in TOKEN_ORDER for c in TOKEN_ORDER]


def content_score(query_token: str, candidate_token: str) -> float:
    query_index = TOKEN_ORDER.index(query_token)
    candidate_index = TOKEN_ORDER.index(candidate_token)
    if query_index == candidate_index:
        return 1.0
    if (candidate_index - query_index) % len(TOKEN_ORDER) == 1:
        return 0.72
    if (query_index - candidate_index) % len(TOKEN_ORDER) == 1:
        return 0.28
    return 0.48


def make_downstream_row(row: AttentionRow) -> DownstreamRow:
    phase_label = float(row.label)
    content = content_score(row.query_token, row.candidate_token)
    target = _clamp01(0.10 + 0.50 * content + 0.30 * phase_label + 0.10 * content * phase_label)
    return DownstreamRow(
        context_id=row.context_id,
        split=row.split,
        slot=row.slot,
        query_token=row.query_token,
        candidate_token=row.candidate_token,
        reference_delta=row.reference_delta,
        candidate_delta=row.candidate_delta,
        m8=row.m8,
        m12=row.m12,
        phase_product=row.m8 * row.m12,
        phase_label=phase_label,
        content_score=content,
        target=round(target, 12),
    )


def make_downstream_splits(seed: int = 42) -> dict[str, list[DownstreamRow]]:
    bundle = generate_transformer_phase_wrap_attention_bundle(seed)
    return {
        "train": [make_downstream_row(row) for row in bundle.train],
        "validation": [make_downstream_row(row) for row in bundle.validation],
        "test": [make_downstream_row(row) for row in bundle.test],
    }


def _targets(rows: list[DownstreamRow]) -> list[float]:
    return [row.target for row in rows]


def _fit_ridge(x: np.ndarray, y: np.ndarray, alpha: float) -> np.ndarray:
    penalty = np.eye(x.shape[1], dtype=float) * alpha
    penalty[0, 0] = 0.0
    return np.linalg.solve(x.T @ x + penalty, x.T @ y)


def _predict_ridge(weights: np.ndarray, x: np.ndarray) -> list[float]:
    return [_clamp01(value) for value in (x @ weights).tolist()]


def _select_and_fit_ridge(
    train: list[DownstreamRow],
    validation: list[DownstreamRow],
    feature_fn: Any,
) -> dict[str, Any]:
    alphas = (0.0, 1e-8, 1e-6, 1e-4, 1e-2, 0.1, 1.0, 10.0)
    train_x = np.array([feature_fn(row) for row in train], dtype=float)
    train_y = np.array(_targets(train), dtype=float)
    validation_x = np.array([feature_fn(row) for row in validation], dtype=float)
    validation_y = _targets(validation)
    candidates: list[tuple[float, float]] = []
    for alpha in alphas:
        weights = _fit_ridge(train_x, train_y, alpha)
        predictions = _predict_ridge(weights, validation_x)
        candidates.append((mean_absolute_error(validation_y, predictions), alpha))
    _, selected_alpha = min(candidates, key=lambda item: (item[0], item[1]))
    combined = train + validation
    weights = _fit_ridge(
        np.array([feature_fn(row) for row in combined], dtype=float),
        np.array(_targets(combined), dtype=float),
        selected_alpha,
    )
    return {"ridge_alpha": selected_alpha, "weights": [float(value) for value in weights.tolist()]}


def _predict_model(model: dict[str, Any], rows: list[DownstreamRow], feature_fn: Any) -> list[float]:
    return _predict_ridge(np.array(model["weights"], dtype=float), np.array([feature_fn(row) for row in rows], dtype=float))


def _content_features(row: DownstreamRow) -> list[float]:
    return [1.0] + token_pair_features(row)


def _phasewrap_features(row: DownstreamRow) -> list[float]:
    return _content_features(row) + [row.m8, row.m12, row.phase_product, row.phase_label]


def _rope_features(row: DownstreamRow) -> list[float]:
    proxy = AttentionRow(
        context_id=row.context_id,
        split=row.split,
        seed=0,
        slot=row.slot,
        query_pos=0,
        reference_key_pos=0,
        candidate_key_pos=0,
        reference_delta=row.reference_delta,
        candidate_delta=row.candidate_delta,
        query_token=row.query_token,
        reference_token="A",
        candidate_token=row.candidate_token,
        label=0.0,
        score=0.0,
        m8=row.m8,
        m12=row.m12,
        quadrant="",
        text="",
    )
    return _content_features(row) + [rope_attention_predictions([proxy])[0]]


def _sinusoidal_features(row: DownstreamRow) -> list[float]:
    proxy = AttentionRow(
        context_id=row.context_id,
        split=row.split,
        seed=0,
        slot=row.slot,
        query_pos=0,
        reference_key_pos=0,
        candidate_key_pos=0,
        reference_delta=row.reference_delta,
        candidate_delta=row.candidate_delta,
        query_token=row.query_token,
        reference_token="A",
        candidate_token=row.candidate_token,
        label=0.0,
        score=0.0,
        m8=row.m8,
        m12=row.m12,
        quadrant="",
        text="",
    )
    return _content_features(row) + [sinusoidal_attention_predictions([proxy])[0]]


def _alibi_features(row: DownstreamRow) -> list[float]:
    return _content_features(row) + [float(abs(row.reference_delta - row.candidate_delta))]


def _phase_only_features(row: DownstreamRow) -> list[float]:
    return [1.0, row.m8, row.m12, row.phase_product, row.phase_label]


def _attention_proxy(row: DownstreamRow) -> AttentionRow:
    return AttentionRow(
        context_id=row.context_id,
        split=row.split,
        seed=0,
        slot=row.slot,
        query_pos=0,
        reference_key_pos=0,
        candidate_key_pos=0,
        reference_delta=row.reference_delta,
        candidate_delta=row.candidate_delta,
        query_token=row.query_token,
        reference_token="A",
        candidate_token=row.candidate_token,
        label=row.target,
        score=0.0,
        m8=row.m8,
        m12=row.m12,
        quadrant="",
        text="",
    )


def evaluate_downstream_predictions(rows: list[DownstreamRow], predictions: list[float]) -> dict[str, float]:
    labels = _targets(rows)
    proxies = [_attention_proxy(row) for row in rows]
    metrics = {
        "row_count": len(rows),
        "mae": mean_absolute_error(labels, predictions),
        "rank_correlation": rank_correlation(labels, predictions),
    }
    metrics.update(context_metrics(proxies, predictions))
    return metrics


def _train_lookup_mod24(rows: list[DownstreamRow]) -> dict[str, Any]:
    buckets: dict[int, list[float]] = {}
    for row in rows:
        key = (row.reference_delta - row.candidate_delta) % 24
        buckets.setdefault(key, []).append(row.target)
    return {
        "global_mean": float(np.mean(_targets(rows))),
        "bucket_means": {str(key): float(np.mean(values)) for key, values in sorted(buckets.items())},
    }


def _predict_lookup_mod24(model: dict[str, Any], rows: list[DownstreamRow]) -> list[float]:
    return [_clamp01(model["bucket_means"].get(str((row.reference_delta - row.candidate_delta) % 24), model["global_mean"])) for row in rows]


def leakage_diagnostics(rows: list[DownstreamRow]) -> dict[str, Any]:
    targets = _targets(rows)
    mod_model = _train_lookup_mod24(rows)
    mod_predictions = _predict_lookup_mod24(mod_model, rows)
    phase_model = _select_and_fit_ridge(rows, rows, _phase_only_features)
    phase_predictions = _predict_model(phase_model, rows, _phase_only_features)
    token_targets: dict[str, set[float]] = {}
    for row in rows:
        token_targets.setdefault(row.query_token + row.candidate_token, set()).add(row.target)
    return {
        "mod24_self_mae": mean_absolute_error(targets, mod_predictions),
        "phase_feature_self_mae": mean_absolute_error(targets, phase_predictions),
        "mod24_not_exact_pass": mean_absolute_error(targets, mod_predictions) > 0.01,
        "phase_features_not_exact_pass": mean_absolute_error(targets, phase_predictions) > 0.01,
        "token_pair_variation_present": any(len(values) > 1 for values in token_targets.values()),
    }


def _score_model(name: str, rows: list[DownstreamRow], predictions: list[float], model: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"name": name, "metrics": evaluate_downstream_predictions(rows, predictions), "model": model or {}}


def run_downstream_attention(seed: int = 42) -> dict[str, Any]:
    splits = make_downstream_splits(seed)
    train = splits["train"]
    validation = splits["validation"]
    test = splits["test"]
    models = {
        "phasewrap_rope_attention": _select_and_fit_ridge(train, validation, _phasewrap_features),
        "rope_attention": _select_and_fit_ridge(train, validation, _rope_features),
        "alibi_attention": _select_and_fit_ridge(train, validation, _alibi_features),
        "sinusoidal_attention": _select_and_fit_ridge(train, validation, _sinusoidal_features),
        "no_position_attention": _select_and_fit_ridge(train, validation, _content_features),
        "classical_m8_m12_product_baseline": _select_and_fit_ridge(train, validation, _phase_only_features),
    }
    lookup_model = _train_lookup_mod24(train + validation)
    results = [
        _score_model(
            "phasewrap_rope_attention",
            test,
            _predict_model(models["phasewrap_rope_attention"], test, _phasewrap_features),
            models["phasewrap_rope_attention"],
        ),
        _score_model("rope_attention", test, _predict_model(models["rope_attention"], test, _rope_features), models["rope_attention"]),
        _score_model("alibi_attention", test, _predict_model(models["alibi_attention"], test, _alibi_features), models["alibi_attention"]),
        _score_model(
            "sinusoidal_attention",
            test,
            _predict_model(models["sinusoidal_attention"], test, _sinusoidal_features),
            models["sinusoidal_attention"],
        ),
        _score_model(
            "no_position_attention",
            test,
            _predict_model(models["no_position_attention"], test, _content_features),
            models["no_position_attention"],
        ),
        _score_model("lookup_mod24_baseline", test, _predict_lookup_mod24(lookup_model, test), lookup_model),
        _score_model(
            "classical_m8_m12_product_baseline",
            test,
            _predict_model(models["classical_m8_m12_product_baseline"], test, _phase_only_features),
            models["classical_m8_m12_product_baseline"],
        ),
    ]
    table = [
        {
            "method": result["name"],
            "rows": result["metrics"]["row_count"],
            "contexts": result["metrics"]["context_count"],
            "mae": result["metrics"]["mae"],
            "rank_correlation": result["metrics"]["rank_correlation"],
            "top1_accuracy": result["metrics"]["top1_accuracy"],
            "mrr": result["metrics"]["mrr"],
            "ndcg_at_4": result["metrics"]["ndcg_at_4"],
        }
        for result in results
    ]
    best = min(table, key=lambda row: (row["mae"], -row["top1_accuracy"], row["method"]))
    return {
        "schema_version": STAGE6_SCHEMA_VERSION,
        "stage": "stage6_downstream_attention",
        "seed": seed,
        "dataset": "synthetic_downstream_attention_content_phase_mix_v1",
        "task": {
            "target": "0.10 + 0.50*content_score + 0.30*phase_label + 0.10*content_score*phase_label",
            "content_source": "query/candidate token compatibility",
            "position_source": "existing phase-wrap attention rows",
        },
        "claim_boundary": {
            "supported": [
                "Toy downstream attention evidence on a deterministic synthetic task that mixes content and positional signal.",
                "Comparison against RoPE, ALiBI, sinusoidal, no-position, mod-24 lookup, and exposed phase-feature baselines.",
            ],
            "excluded": [
                "production transformer superiority",
                "full transformer-scale validation",
                "broad quantum advantage",
            ],
        },
        "leakage_diagnostics": leakage_diagnostics(train + validation + test),
        "splits": {
            name: {
                "row_count": len(rows),
                "context_count": len({row.context_id for row in rows}),
            }
            for name, rows in splits.items()
        },
        "results": results,
        "table": table,
        "best_method": best["method"],
    }


def write_stage6_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "seed": result["seed"],
        "dataset": result["dataset"],
        "model_names": list(MODEL_NAMES),
        "result_path": str((output_dir / "results.json").as_posix()),
        "summary_csv_path": str((output_dir / "summary.csv").as_posix()),
        "claim_boundary": result["claim_boundary"],
    }
    paths = {
        "manifest": str(output_dir / "manifest.json"),
        "results": str(output_dir / "results.json"),
        "summary_csv": str(output_dir / "summary.csv"),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(result["table"][0].keys()))
        writer.writeheader()
        writer.writerows(result["table"])
    return paths


def print_stage6_table(result: dict[str, Any]) -> None:
    columns = ("method", "rows", "contexts", "mae", "rank_correlation", "top1_accuracy", "mrr", "ndcg_at_4")
    print(" | ".join(columns))
    print(" | ".join("---" for _ in columns))
    for row in result["table"]:
        print(" | ".join(str(row[column]) for column in columns))
