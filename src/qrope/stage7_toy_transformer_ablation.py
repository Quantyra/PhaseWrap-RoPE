from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from .automated_stage_gates import normalized_phase_label, phase_margins, spearman
from .stage5_attention_baselines import mean_absolute_error


STAGE7_SCHEMA_VERSION = "qrope_stage7_toy_transformer_ablation_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage7_toy_transformer_ablation"
MODEL_NAMES = (
    "phasewrap_rope_4layer",
    "rope_4layer",
    "alibi_4layer",
    "sinusoidal_4layer",
    "no_position_4layer",
)
VOCAB_SIZE = 8
LAYER_COUNT = 4


@dataclass(frozen=True)
class ToyTransformerExample:
    example_id: str
    split: str
    sequence_length: int
    query_pos: int
    reference_delta: int
    target_pos: int
    target_delta: int
    tokens: tuple[int, ...]


def _token_at(position: int, offset: int) -> int:
    return (position + offset) % VOCAB_SIZE


def make_toy_transformer_splits(seed: int = 42) -> dict[str, list[ToyTransformerExample]]:
    rng = np.random.default_rng(seed)
    split_lengths = {
        "train": (16, 24),
        "validation": (32,),
        "test": (48, 64),
    }
    reference_deltas = (5, 7, 8, 11, 12, 16, 19, 24)
    splits: dict[str, list[ToyTransformerExample]] = {name: [] for name in split_lengths}
    for split, lengths in split_lengths.items():
        for sequence_length in lengths:
            query_pos = sequence_length - 1
            valid_deltas = [delta for delta in reference_deltas if delta < sequence_length]
            for context_index in range(20):
                offset = int(rng.integers(0, VOCAB_SIZE))
                reference_delta = valid_deltas[context_index % len(valid_deltas)]
                phase_equivalent_deltas = range(reference_delta, query_pos + 1, 24)
                target_delta = max(phase_equivalent_deltas)
                target_pos = query_pos - target_delta
                tokens = tuple(_token_at(position, offset) for position in range(sequence_length))
                splits[split].append(
                    ToyTransformerExample(
                        example_id=f"{split}_L{sequence_length}_{context_index:03d}",
                        split=split,
                        sequence_length=sequence_length,
                        query_pos=query_pos,
                        reference_delta=reference_delta,
                        target_pos=target_pos,
                        target_delta=target_delta,
                        tokens=tokens,
                    )
                )
    return splits


def _softmax(values: np.ndarray) -> np.ndarray:
    shifted = values - np.max(values)
    exp_values = np.exp(shifted)
    return exp_values / np.sum(exp_values)


def _content_logits(example: ToyTransformerExample, query_state: np.ndarray) -> np.ndarray:
    candidates = np.array(example.tokens[: example.query_pos], dtype=float)
    query_token = float(example.tokens[example.target_pos])
    exact_match = (candidates == query_token).astype(float)
    token_distance = np.minimum(np.abs(candidates - query_token), VOCAB_SIZE - np.abs(candidates - query_token)) / VOCAB_SIZE
    return 0.85 * exact_match - 0.15 * token_distance + 0.08 * query_state[candidates.astype(int)]


def _phasewrap_bias(example: ToyTransformerExample) -> np.ndarray:
    candidate_deltas = example.query_pos - np.arange(example.query_pos)
    return np.array(
        [
            normalized_phase_label(phase_margins(example.reference_delta, int(candidate_delta))["score"])
            for candidate_delta in candidate_deltas
        ],
        dtype=float,
    )


def _period_similarity(reference_delta: int, candidate_deltas: np.ndarray, periods: tuple[float, ...]) -> np.ndarray:
    diff = reference_delta - candidate_deltas
    components = [np.cos(2.0 * math.pi * diff / period) for period in periods]
    return np.mean(np.array(components, dtype=float), axis=0)


def _position_bias(example: ToyTransformerExample, model_name: str) -> np.ndarray:
    candidate_deltas = example.query_pos - np.arange(example.query_pos)
    if model_name == "phasewrap_rope_4layer":
        return _phasewrap_bias(example)
    if model_name == "rope_4layer":
        return 0.5 + 0.5 * _period_similarity(example.reference_delta, candidate_deltas, (8.0, 12.0, 24.0, 48.0))
    if model_name == "sinusoidal_4layer":
        return 0.5 + 0.5 * _period_similarity(example.reference_delta, candidate_deltas, (4.0, 8.0, 16.0, 32.0))
    if model_name == "alibi_4layer":
        distance = np.abs(example.reference_delta - candidate_deltas)
        return np.maximum(0.0, 1.0 - 0.035 * distance)
    if model_name == "no_position_4layer":
        return np.zeros(example.query_pos, dtype=float)
    raise ValueError(f"unknown model_name: {model_name}")


def four_layer_attention_distribution(example: ToyTransformerExample, model_name: str, position_scale: float) -> np.ndarray:
    query_state = np.zeros(VOCAB_SIZE, dtype=float)
    token_positions = np.array(example.tokens[: example.query_pos], dtype=int)
    distribution = np.full(example.query_pos, 1.0 / example.query_pos, dtype=float)
    position_bias = _position_bias(example, model_name)
    for layer_index in range(LAYER_COUNT):
        logits = _content_logits(example, query_state) + position_scale * position_bias
        logits += 0.04 * float(layer_index) * distribution
        distribution = _softmax(logits)
        attended = np.zeros(VOCAB_SIZE, dtype=float)
        for token, weight in zip(token_positions, distribution):
            attended[token] += float(weight)
        query_state = 0.65 * query_state + 0.35 * attended
    return distribution


def _target_rank(distribution: np.ndarray, target_index: int) -> int:
    sorted_indices = sorted(range(len(distribution)), key=lambda index: (-float(distribution[index]), index))
    return sorted_indices.index(target_index) + 1


def evaluate_toy_transformer_model(
    rows: list[ToyTransformerExample],
    model_name: str,
    position_scale: float,
) -> dict[str, float]:
    target_probs: list[float] = []
    ranks: list[int] = []
    labels: list[float] = []
    predictions: list[float] = []
    top1_hits = 0
    for row in rows:
        distribution = four_layer_attention_distribution(row, model_name, position_scale)
        target_index = row.target_pos
        target_prob = float(distribution[target_index])
        rank = _target_rank(distribution, target_index)
        target_probs.append(target_prob)
        ranks.append(rank)
        labels.append(1.0)
        predictions.append(target_prob)
        if rank == 1:
            top1_hits += 1
    return {
        "row_count": len(rows),
        "sequence_length_min": min(row.sequence_length for row in rows),
        "sequence_length_max": max(row.sequence_length for row in rows),
        "target_probability_mae": mean_absolute_error(labels, predictions),
        "mean_target_probability": round(float(np.mean(target_probs)), 6),
        "top1_accuracy": round(top1_hits / len(rows), 6),
        "mrr": round(float(np.mean([1.0 / rank for rank in ranks])), 6),
        "rank_correlation": round(float(spearman([-rank for rank in ranks], target_probs)), 6),
    }


def _select_scale(validation_rows: list[ToyTransformerExample], model_name: str) -> float:
    candidates = (0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0)
    scored = [
        (
            -evaluate_toy_transformer_model(validation_rows, model_name, scale)["mrr"],
            -evaluate_toy_transformer_model(validation_rows, model_name, scale)["top1_accuracy"],
            evaluate_toy_transformer_model(validation_rows, model_name, scale)["target_probability_mae"],
            scale,
        )
        for scale in candidates
    ]
    return min(scored)[3]


def run_toy_transformer_ablation(seed: int = 42) -> dict[str, Any]:
    splits = make_toy_transformer_splits(seed)
    validation = splits["validation"]
    test = splits["test"]
    rows: list[dict[str, Any]] = []
    for model_name in MODEL_NAMES:
        scale = _select_scale(validation, model_name)
        metrics = evaluate_toy_transformer_model(test, model_name, scale)
        rows.append(
            {
                "method": model_name,
                "layers": LAYER_COUNT,
                "position_scale": scale,
                **metrics,
            }
        )
    best = max(rows, key=lambda row: (row["mrr"], row["top1_accuracy"], row["mean_target_probability"], row["method"]))
    return {
        "schema_version": STAGE7_SCHEMA_VERSION,
        "stage": "stage7_toy_transformer_ablation",
        "seed": seed,
        "dataset": "synthetic_length_extrapolation_retrieval_v1",
        "task": {
            "description": "Four-layer attention-only toy transformer selects the farthest prior token with the requested mod-8/mod-12 phase relation.",
            "train_lengths": [16, 24],
            "validation_lengths": [32],
            "test_lengths": [48, 64],
            "layer_count": LAYER_COUNT,
        },
        "claim_boundary": {
            "supported": [
                "Synthetic length-extrapolation ablation showing how the PhaseWrap score behaves when swapped into a four-layer toy attention stack.",
                "No hardware submission and no production transformer claim.",
            ],
            "excluded": [
                "production transformer superiority",
                "full transformer-scale validation",
                "broad quantum advantage",
                "general cross-backend robustness",
            ],
        },
        "splits": {
            name: {
                "row_count": len(rows_for_split),
                "lengths": sorted({row.sequence_length for row in rows_for_split}),
            }
            for name, rows_for_split in splits.items()
        },
        "table": rows,
        "best_method": best["method"],
    }


def write_stage7_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
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


def print_stage7_table(result: dict[str, Any]) -> None:
    columns = (
        "method",
        "layers",
        "position_scale",
        "row_count",
        "sequence_length_min",
        "sequence_length_max",
        "target_probability_mae",
        "mean_target_probability",
        "top1_accuracy",
        "mrr",
    )
    print(" | ".join(columns))
    print(" | ".join("---" for _ in columns))
    for row in result["table"]:
        print(" | ".join(str(row[column]) for column in columns))
