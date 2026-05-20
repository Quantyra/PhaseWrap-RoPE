from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import numpy as np

from .automated_stage_gates import (
    AttentionRow,
    generate_transformer_phase_wrap_attention_bundle,
    spearman,
)


STAGE5_SCHEMA_VERSION = "qrope_stage5_attention_baselines_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage5_attention_baselines"
BASELINE_NAMES = (
    "phase_wrap_formula",
    "lookup_mod24",
    "classical_m8_m12_product",
    "delta_regression_tree",
    "rope_attention",
    "sinusoidal_attention",
    "alibi_attention",
)


@dataclass(frozen=True)
class TreeNode:
    value: float
    feature_index: int | None = None
    threshold: float | None = None
    left: "TreeNode | None" = None
    right: "TreeNode | None" = None

    def predict_one(self, features: np.ndarray) -> float:
        if self.feature_index is None or self.threshold is None or self.left is None or self.right is None:
            return self.value
        if features[self.feature_index] <= self.threshold:
            return self.left.predict_one(features)
        return self.right.predict_one(features)


def mod24_key(row: AttentionRow) -> int:
    return (row.reference_delta - row.candidate_delta) % 24


def ridge_feature_matrix(rows: list[AttentionRow]) -> np.ndarray:
    return np.array([[1.0, row.m8, row.m12, row.m8 * row.m12] for row in rows], dtype=float)


def delta_feature_matrix(rows: list[AttentionRow]) -> np.ndarray:
    return np.array(
        [
            [
                float(row.reference_delta),
                float(row.candidate_delta),
                float(row.reference_delta - row.candidate_delta),
                float(abs(row.reference_delta - row.candidate_delta)),
                float((row.reference_delta - row.candidate_delta) % 24),
                float(row.reference_delta % 24),
                float(row.candidate_delta % 24),
            ]
            for row in rows
        ],
        dtype=float,
    )


def mean_absolute_error(labels: list[float], predictions: list[float]) -> float:
    if len(labels) != len(predictions) or not labels:
        raise ValueError("labels and predictions must be non-empty and equal length")
    return round(float(np.mean(np.abs(np.array(labels) - np.array(predictions)))), 6)


def rank_correlation(labels: list[float], predictions: list[float]) -> float:
    if len(labels) != len(predictions) or not labels:
        raise ValueError("labels and predictions must be non-empty and equal length")
    return round(float(spearman(predictions, labels)), 6)


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _labels(rows: list[AttentionRow]) -> list[float]:
    return [float(row.label) for row in rows]


def _group_by_context(rows: list[AttentionRow]) -> dict[str, list[int]]:
    grouped: dict[str, list[int]] = {}
    for index, row in enumerate(rows):
        grouped.setdefault(row.context_id, []).append(index)
    return grouped


def _average_rank(sorted_indices: list[int], true_best: set[int]) -> float:
    ranks = [rank + 1 for rank, index in enumerate(sorted_indices) if index in true_best]
    return float(sum(ranks) / len(ranks))


def context_metrics(rows: list[AttentionRow], predictions: list[float]) -> dict[str, float]:
    grouped = _group_by_context(rows)
    top1_hits = 0
    reciprocal_ranks: list[float] = []
    ndcg_values: list[float] = []
    for indices in grouped.values():
        labels = [float(rows[index].label) for index in indices]
        scores = [float(predictions[index]) for index in indices]
        max_label = max(labels)
        true_best = {indices[pos] for pos, label in enumerate(labels) if label == max_label}
        sorted_indices = sorted(indices, key=lambda index: (-predictions[index], rows[index].slot, rows[index].candidate_delta))
        if sorted_indices[0] in true_best:
            top1_hits += 1
        reciprocal_ranks.append(1.0 / _average_rank(sorted_indices, true_best))
        gains = [float(rows[index].label) for index in sorted_indices]
        ideal = sorted(labels, reverse=True)
        dcg = sum((2.0**gain - 1.0) / math.log2(rank + 2.0) for rank, gain in enumerate(gains))
        ideal_dcg = sum((2.0**gain - 1.0) / math.log2(rank + 2.0) for rank, gain in enumerate(ideal))
        ndcg_values.append(dcg / ideal_dcg if ideal_dcg else 0.0)
    count = len(grouped)
    return {
        "context_count": count,
        "top1_accuracy": round(top1_hits / count, 6) if count else 0.0,
        "mrr": round(float(np.mean(reciprocal_ranks)), 6) if reciprocal_ranks else 0.0,
        "ndcg_at_4": round(float(np.mean(ndcg_values)), 6) if ndcg_values else 0.0,
    }


def evaluate_predictions(rows: list[AttentionRow], predictions: list[float]) -> dict[str, float]:
    labels = _labels(rows)
    metrics = {
        "row_count": len(rows),
        "mae": mean_absolute_error(labels, predictions),
        "rank_correlation": rank_correlation(labels, predictions),
    }
    metrics.update(context_metrics(rows, predictions))
    return metrics


def phase_wrap_predictions(rows: list[AttentionRow]) -> list[float]:
    return [float(row.label) for row in rows]


def train_lookup_mod24(rows: list[AttentionRow]) -> dict[str, Any]:
    buckets: dict[int, list[float]] = {}
    for row in rows:
        buckets.setdefault(mod24_key(row), []).append(float(row.label))
    global_mean = float(np.mean(_labels(rows)))
    return {
        "global_mean": global_mean,
        "bucket_means": {str(key): float(np.mean(values)) for key, values in sorted(buckets.items())},
    }


def predict_lookup_mod24(model: dict[str, Any], rows: list[AttentionRow]) -> list[float]:
    buckets = model["bucket_means"]
    return [_clamp01(buckets.get(str(mod24_key(row)), model["global_mean"])) for row in rows]


def _fit_ridge(rows: list[AttentionRow], ridge_alpha: float) -> np.ndarray:
    x = ridge_feature_matrix(rows)
    y = np.array(_labels(rows), dtype=float)
    penalty = np.eye(x.shape[1], dtype=float) * ridge_alpha
    penalty[0, 0] = 0.0
    return np.linalg.solve(x.T @ x + penalty, x.T @ y)


def _predict_ridge(weights: np.ndarray, rows: list[AttentionRow]) -> list[float]:
    return [_clamp01(value) for value in (ridge_feature_matrix(rows) @ weights).tolist()]


def train_ridge_product(train: list[AttentionRow], validation: list[AttentionRow]) -> dict[str, Any]:
    alphas = (0.0, 1e-8, 1e-6, 1e-4, 1e-2, 0.1, 1.0, 10.0)
    candidates = []
    for alpha in alphas:
        weights = _fit_ridge(train, alpha)
        predictions = _predict_ridge(weights, validation)
        candidates.append((mean_absolute_error(_labels(validation), predictions), alpha))
    _, selected_alpha = min(candidates, key=lambda item: (item[0], item[1]))
    weights = _fit_ridge(train + validation, selected_alpha)
    return {
        "ridge_alpha": selected_alpha,
        "feature_order": ["bias", "m8", "m12", "m8*m12"],
        "weights": [float(value) for value in weights.tolist()],
    }


def predict_ridge_product(model: dict[str, Any], rows: list[AttentionRow]) -> list[float]:
    return _predict_ridge(np.array(model["weights"], dtype=float), rows)


def _leaf_value(y: np.ndarray) -> float:
    return _clamp01(float(np.mean(y))) if len(y) else 0.5


def _fit_tree_node(x: np.ndarray, y: np.ndarray, *, depth: int, max_depth: int, min_leaf: int) -> TreeNode:
    value = _leaf_value(y)
    if depth >= max_depth or len(y) < 2 * min_leaf or float(np.var(y)) <= 1e-12:
        return TreeNode(value=value)
    best: tuple[float, int, float] | None = None
    for feature_index in range(x.shape[1]):
        values = sorted(set(float(value) for value in x[:, feature_index].tolist()))
        thresholds = [(left + right) / 2.0 for left, right in zip(values, values[1:])]
        for threshold in thresholds:
            mask = x[:, feature_index] <= threshold
            left_count = int(np.sum(mask))
            right_count = len(y) - left_count
            if left_count < min_leaf or right_count < min_leaf:
                continue
            left_y = y[mask]
            right_y = y[~mask]
            loss = float(np.sum((left_y - np.mean(left_y)) ** 2) + np.sum((right_y - np.mean(right_y)) ** 2))
            candidate = (loss, feature_index, threshold)
            if best is None or candidate < best:
                best = candidate
    if best is None:
        return TreeNode(value=value)
    _, feature_index, threshold = best
    mask = x[:, feature_index] <= threshold
    return TreeNode(
        value=value,
        feature_index=feature_index,
        threshold=threshold,
        left=_fit_tree_node(x[mask], y[mask], depth=depth + 1, max_depth=max_depth, min_leaf=min_leaf),
        right=_fit_tree_node(x[~mask], y[~mask], depth=depth + 1, max_depth=max_depth, min_leaf=min_leaf),
    )


def _tree_to_dict(node: TreeNode) -> dict[str, Any]:
    payload: dict[str, Any] = {"value": round(node.value, 12)}
    if node.feature_index is not None:
        payload.update(
            {
                "feature_index": node.feature_index,
                "threshold": round(float(node.threshold), 12),
                "left": _tree_to_dict(node.left),  # type: ignore[arg-type]
                "right": _tree_to_dict(node.right),  # type: ignore[arg-type]
            }
        )
    return payload


def _tree_from_dict(payload: dict[str, Any]) -> TreeNode:
    if "feature_index" not in payload:
        return TreeNode(value=float(payload["value"]))
    return TreeNode(
        value=float(payload["value"]),
        feature_index=int(payload["feature_index"]),
        threshold=float(payload["threshold"]),
        left=_tree_from_dict(payload["left"]),
        right=_tree_from_dict(payload["right"]),
    )


def _fit_tree(rows: list[AttentionRow], max_depth: int, min_leaf: int) -> TreeNode:
    return _fit_tree_node(
        delta_feature_matrix(rows),
        np.array(_labels(rows), dtype=float),
        depth=0,
        max_depth=max_depth,
        min_leaf=min_leaf,
    )


def _predict_tree(root: TreeNode, rows: list[AttentionRow]) -> list[float]:
    return [_clamp01(root.predict_one(features)) for features in delta_feature_matrix(rows)]


def train_regression_tree(train: list[AttentionRow], validation: list[AttentionRow]) -> dict[str, Any]:
    candidates: list[tuple[float, int, int]] = []
    for max_depth in (1, 2, 3, 4):
        for min_leaf in (4, 8, 16):
            root = _fit_tree(train, max_depth=max_depth, min_leaf=min_leaf)
            predictions = _predict_tree(root, validation)
            candidates.append((mean_absolute_error(_labels(validation), predictions), max_depth, min_leaf))
    _, selected_depth, selected_min_leaf = min(candidates)
    root = _fit_tree(train + validation, max_depth=selected_depth, min_leaf=selected_min_leaf)
    return {
        "feature_order": [
            "reference_delta",
            "candidate_delta",
            "delta_diff",
            "abs_delta_diff",
            "delta_diff_mod24",
            "reference_delta_mod24",
            "candidate_delta_mod24",
        ],
        "max_depth": selected_depth,
        "min_leaf": selected_min_leaf,
        "tree": _tree_to_dict(root),
    }


def predict_regression_tree(model: dict[str, Any], rows: list[AttentionRow]) -> list[float]:
    return _predict_tree(_tree_from_dict(model["tree"]), rows)


def _period_similarity(row: AttentionRow, periods: tuple[float, ...]) -> float:
    delta = float(row.reference_delta - row.candidate_delta)
    return float(np.mean([math.cos(2.0 * math.pi * delta / period) for period in periods]))


def _score_from_similarity(value: float) -> float:
    return _clamp01(0.5 + 0.5 * value)


def rope_attention_predictions(rows: list[AttentionRow]) -> list[float]:
    return [_score_from_similarity(_period_similarity(row, (8.0, 12.0, 24.0, 48.0))) for row in rows]


def sinusoidal_attention_predictions(rows: list[AttentionRow]) -> list[float]:
    return [_score_from_similarity(_period_similarity(row, (4.0, 8.0, 16.0, 32.0))) for row in rows]


def train_alibi(train: list[AttentionRow], validation: list[AttentionRow]) -> dict[str, float]:
    scales = (0.02, 0.05, 0.1, 0.2)
    slopes = tuple(float(value) for value in np.linspace(0.0, 0.05, 26))
    candidates: list[tuple[float, float, float]] = []
    for scale in scales:
        for slope in slopes:
            predictions = [_clamp01(1.0 - slope * abs(row.reference_delta - row.candidate_delta) * scale) for row in validation]
            candidates.append((mean_absolute_error(_labels(validation), predictions), slope, scale))
    _, selected_slope, selected_scale = min(candidates)
    return {"slope": selected_slope, "scale": selected_scale}


def predict_alibi(model: dict[str, float], rows: list[AttentionRow]) -> list[float]:
    return [
        _clamp01(1.0 - model["slope"] * abs(row.reference_delta - row.candidate_delta) * model["scale"])
        for row in rows
    ]


def _score_baseline(
    name: str,
    rows: list[AttentionRow],
    predictions: list[float],
    model: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "name": name,
        "metrics": evaluate_predictions(rows, predictions),
        "model": model or {},
    }


def run_attention_baselines(seed: int = 42) -> dict[str, Any]:
    bundle = generate_transformer_phase_wrap_attention_bundle(seed)
    train = bundle.train
    validation = bundle.validation
    test = bundle.test
    lookup_model = train_lookup_mod24(train)
    ridge_model = train_ridge_product(train, validation)
    tree_model = train_regression_tree(train, validation)
    alibi_model = train_alibi(train, validation)
    baselines = [
        _score_baseline("phase_wrap_formula", test, phase_wrap_predictions(test)),
        _score_baseline("lookup_mod24", test, predict_lookup_mod24(lookup_model, test), lookup_model),
        _score_baseline("classical_m8_m12_product", test, predict_ridge_product(ridge_model, test), ridge_model),
        _score_baseline("delta_regression_tree", test, predict_regression_tree(tree_model, test), tree_model),
        _score_baseline("rope_attention", test, rope_attention_predictions(test)),
        _score_baseline("sinusoidal_attention", test, sinusoidal_attention_predictions(test)),
        _score_baseline("alibi_attention", test, predict_alibi(alibi_model, test), alibi_model),
    ]
    table = [
        {
            "method": item["name"],
            "rows": item["metrics"]["row_count"],
            "contexts": item["metrics"]["context_count"],
            "mae": item["metrics"]["mae"],
            "rank_correlation": item["metrics"]["rank_correlation"],
            "top1_accuracy": item["metrics"]["top1_accuracy"],
            "mrr": item["metrics"]["mrr"],
            "ndcg_at_4": item["metrics"]["ndcg_at_4"],
        }
        for item in baselines
    ]
    return {
        "schema_version": STAGE5_SCHEMA_VERSION,
        "stage": "stage5_attention_baselines",
        "seed": seed,
        "dataset": bundle.diagnostics["dataset"],
        "claim_boundary": {
            "supported": [
                "Deterministic comparison of phase-wrap scoring against classical and positional attention-scoring baselines on the existing synthetic attention-selection task.",
                "No hardware submission and no provider credentials required.",
            ],
            "excluded": [
                "production transformer superiority",
                "full transformer-scale validation",
                "broad quantum advantage",
            ],
        },
        "splits": {
            "train": bundle.diagnostics["splits"]["train"],
            "validation": bundle.diagnostics["splits"]["validation"],
            "test": bundle.diagnostics["splits"]["test"],
        },
        "bundle_diagnostics": bundle.diagnostics,
        "baselines": baselines,
        "table": table,
    }


def write_stage5_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "seed": result["seed"],
        "dataset": result["dataset"],
        "baseline_names": list(BASELINE_NAMES),
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


def print_stage5_table(result: dict[str, Any]) -> None:
    columns = ("method", "rows", "contexts", "mae", "rank_correlation", "top1_accuracy", "mrr", "ndcg_at_4")
    print(" | ".join(columns))
    print(" | ".join("---" for _ in columns))
    for row in result["table"]:
        print(" | ".join(str(row[column]) for column in columns))
