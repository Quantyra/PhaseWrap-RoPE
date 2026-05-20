from __future__ import annotations

import csv
import hashlib
import json
import math
import random
from pathlib import Path
from typing import Any

import numpy as np

from .automated_stage_gates import phase_residual
from .stage12_ruler_retrieval import (
    DEFAULT_CONTEXT_LENGTHS,
    DEFAULT_EXAMPLES_PER_TASK_LENGTH,
    DEFAULT_SEEDS,
    TASK_NAMES,
    Stage12Example,
    make_stage12_examples,
)


STAGE13_SCHEMA_VERSION = "qrope_stage13_positional_adapter_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage13_positional_adapter"
TRAIN_LENGTHS = (128, 256)
VALIDATION_LENGTHS = (512,)
TEST_LENGTHS = (1024,)
METHOD_NAMES = (
    "no_position",
    "alibi",
    "rope_relative",
    "sinusoidal",
    "phasewrap_score",
    "phasewrap_residual_adapter",
    "phasewrap_distance_adapter",
)


def _phasewrap_score(reference_delta: int, candidate_delta: int) -> float:
    margins = []
    for period in (8, 12):
        residual = phase_residual(reference_delta, candidate_delta, period)
        margins.append(math.cos(residual) - math.cos(2.0 * math.pi / float(period)))
    return float(margins[0] * margins[1])


def _rope_inverse_frequencies(dim: int = 32, base: float = 10000.0) -> np.ndarray:
    return np.array([base ** (-2.0 * index / dim) for index in range(dim // 2)], dtype=float)


def positional_features(example: Stage12Example, method_name: str) -> np.ndarray:
    candidate_positions = np.array(example.key_positions, dtype=int)
    candidate_deltas = example.query_pos - candidate_positions.astype(float)
    diff = float(example.reference_delta) - candidate_deltas
    if method_name == "no_position":
        return np.ones((len(candidate_positions), 1), dtype=float)
    if method_name == "alibi":
        return np.column_stack([np.ones(len(candidate_positions)), -candidate_deltas / float(example.query_pos)])
    if method_name == "rope_relative":
        inv_freq = _rope_inverse_frequencies()
        return np.column_stack([np.ones(len(candidate_positions)), np.cos(diff[:, None] * inv_freq[None, :])])
    if method_name == "sinusoidal":
        periods = np.array((4.0, 8.0, 16.0, 32.0, 64.0), dtype=float)
        return np.column_stack([np.ones(len(candidate_positions)), np.cos(2.0 * math.pi * diff[:, None] / periods[None, :])])
    phase_scores = np.array([_phasewrap_score(example.reference_delta, int(delta)) for delta in candidate_deltas], dtype=float)
    if method_name == "phasewrap_score":
        return np.column_stack([np.ones(len(candidate_positions)), phase_scores])
    residual8 = np.array([phase_residual(example.reference_delta, int(delta), 8) for delta in candidate_deltas], dtype=float)
    residual12 = np.array([phase_residual(example.reference_delta, int(delta), 12) for delta in candidate_deltas], dtype=float)
    cos8 = np.cos(residual8)
    cos12 = np.cos(residual12)
    if method_name == "phasewrap_residual_adapter":
        return np.column_stack([np.ones(len(candidate_positions)), phase_scores, cos8, cos12, cos8 * cos12])
    if method_name == "phasewrap_distance_adapter":
        distance = -np.abs(diff) / float(example.query_pos)
        signed = diff / float(example.query_pos)
        return np.column_stack([np.ones(len(candidate_positions)), phase_scores, cos8, cos12, cos8 * cos12, distance, signed])
    raise ValueError(f"unknown method_name: {method_name}")


def split_examples(examples: list[Stage12Example]) -> dict[str, list[Stage12Example]]:
    return {
        "train": [example for example in examples if example.sequence_length in TRAIN_LENGTHS],
        "validation": [example for example in examples if example.sequence_length in VALIDATION_LENGTHS],
        "test": [example for example in examples if example.sequence_length in TEST_LENGTHS],
    }


def _softmax(values: np.ndarray) -> np.ndarray:
    shifted = values - np.max(values)
    exp_values = np.exp(shifted)
    return exp_values / np.sum(exp_values)


def _target_distribution(example: Stage12Example) -> np.ndarray:
    candidate_positions = tuple(example.key_positions)
    targets = np.zeros(len(candidate_positions), dtype=float)
    for position in example.target_positions:
        targets[candidate_positions.index(position)] = 1.0 / float(len(example.target_positions))
    return targets


def _loss_and_gradient(rows: list[Stage12Example], method_name: str, weights: np.ndarray, l2: float) -> tuple[float, np.ndarray]:
    total_loss = 0.0
    gradient = np.zeros_like(weights)
    for row in rows:
        features = positional_features(row, method_name)
        probabilities = _softmax(features @ weights)
        targets = _target_distribution(row)
        candidate_positions = tuple(row.key_positions)
        target_candidate_indices = [candidate_positions.index(position) for position in row.target_positions]
        target_mass = max(float(np.sum(probabilities[target_candidate_indices])), 1e-12)
        total_loss += -math.log(target_mass)
        gradient += features.T @ (probabilities - targets)
    total_loss = total_loss / float(len(rows)) + 0.5 * l2 * float(weights @ weights)
    gradient = gradient / float(len(rows)) + l2 * weights
    return float(total_loss), gradient


def train_adapter(
    rows: list[Stage12Example],
    method_name: str,
    *,
    epochs: int = 220,
    learning_rate: float = 0.35,
    l2: float = 0.001,
) -> dict[str, Any]:
    if not rows:
        raise ValueError("rows must be non-empty")
    weights = np.zeros(positional_features(rows[0], method_name).shape[1], dtype=float)
    history: list[dict[str, float]] = []
    for epoch in range(epochs):
        loss, gradient = _loss_and_gradient(rows, method_name, weights, l2)
        weights -= learning_rate * gradient
        if epoch in {0, epochs // 4, epochs // 2, epochs - 1}:
            history.append({"epoch": epoch + 1, "loss": round(loss, 6)})
    return {
        "method": method_name,
        "epochs": epochs,
        "learning_rate": learning_rate,
        "l2": l2,
        "weights": [round(float(value), 8) for value in weights.tolist()],
        "training_history": history,
        "final_training_loss": history[-1]["loss"],
    }


def _ranked_indices(probabilities: np.ndarray) -> list[int]:
    return sorted(range(len(probabilities)), key=lambda index: (-float(probabilities[index]), index))


def _first_relevant_rank(probabilities: np.ndarray, target_candidate_indices: tuple[int, ...]) -> int:
    target_set = set(target_candidate_indices)
    for rank, index in enumerate(_ranked_indices(probabilities), start=1):
        if index in target_set:
            return rank
    raise RuntimeError("target absent from candidate distribution")


def _bootstrap_ci(values: list[float], *, seed_text: str, iterations: int = 600) -> dict[str, float]:
    if not values:
        raise ValueError("cannot bootstrap an empty metric list")
    rng = random.Random(int(hashlib.sha256(seed_text.encode("utf-8")).hexdigest()[:16], 16))
    means: list[float] = []
    for _ in range(iterations):
        sample = [values[rng.randrange(len(values))] for _ in range(len(values))]
        means.append(float(sum(sample) / len(sample)))
    means.sort()
    low_index = int(0.025 * (iterations - 1))
    high_index = int(0.975 * (iterations - 1))
    return {"low": round(means[low_index], 6), "high": round(means[high_index], 6)}


def evaluate_adapter(rows: list[Stage12Example], method_name: str, weights: np.ndarray) -> dict[str, Any]:
    losses: list[float] = []
    reciprocal_ranks: list[float] = []
    top1_hits: list[float] = []
    target_masses: list[float] = []
    ranks: list[int] = []
    for row in rows:
        probabilities = _softmax(positional_features(row, method_name) @ weights)
        candidate_positions = tuple(row.key_positions)
        target_candidate_indices = tuple(candidate_positions.index(position) for position in row.target_positions)
        rank = _first_relevant_rank(probabilities, target_candidate_indices)
        top_index = _ranked_indices(probabilities)[0]
        target_mass = max(float(np.sum(probabilities[list(target_candidate_indices)])), 1e-12)
        losses.append(-math.log(target_mass))
        reciprocal_ranks.append(1.0 / float(rank))
        top1_hits.append(1.0 if top_index in set(target_candidate_indices) else 0.0)
        target_masses.append(target_mass)
        ranks.append(rank)
    mean_loss = float(np.mean(losses))
    top1 = float(np.mean(top1_hits))
    mrr = float(np.mean(reciprocal_ranks))
    target_mass_mean = float(np.mean(target_masses))
    return {
        "row_count": len(rows),
        "loss": round(mean_loss, 6),
        "perplexity": round(float(math.exp(mean_loss)), 6),
        "top1_accuracy": round(top1, 6),
        "top1_ci_low": _bootstrap_ci(top1_hits, seed_text=f"{method_name}:top1")["low"],
        "top1_ci_high": _bootstrap_ci(top1_hits, seed_text=f"{method_name}:top1")["high"],
        "mrr": round(mrr, 6),
        "mrr_ci_low": _bootstrap_ci(reciprocal_ranks, seed_text=f"{method_name}:mrr")["low"],
        "mrr_ci_high": _bootstrap_ci(reciprocal_ranks, seed_text=f"{method_name}:mrr")["high"],
        "mean_target_probability_mass": round(target_mass_mean, 6),
        "target_probability_mass_ci_low": _bootstrap_ci(target_masses, seed_text=f"{method_name}:prob")["low"],
        "target_probability_mass_ci_high": _bootstrap_ci(target_masses, seed_text=f"{method_name}:prob")["high"],
        "mean_first_relevant_rank": round(float(np.mean(ranks)), 6),
    }


def run_stage13_benchmark(
    *,
    seeds: tuple[int, ...] = DEFAULT_SEEDS,
    context_lengths: tuple[int, ...] = DEFAULT_CONTEXT_LENGTHS,
    examples_per_task_length: int = DEFAULT_EXAMPLES_PER_TASK_LENGTH,
    epochs: int = 220,
) -> dict[str, Any]:
    examples = make_stage12_examples(
        seeds=seeds,
        context_lengths=context_lengths,
        examples_per_task_length=examples_per_task_length,
    )
    splits = split_examples(examples)
    table: list[dict[str, Any]] = []
    per_task_table: list[dict[str, Any]] = []
    training_records: list[dict[str, Any]] = []
    for method_name in METHOD_NAMES:
        training = train_adapter(splits["train"], method_name, epochs=epochs)
        training_records.append(training)
        weights = np.array(training["weights"], dtype=float)
        row = evaluate_adapter(splits["test"], method_name, weights)
        row["method"] = method_name
        table.append(row)
        for task_name in TASK_NAMES:
            task_rows = [example for example in splits["test"] if example.task == task_name]
            task_result = evaluate_adapter(task_rows, method_name, weights)
            task_result["method"] = method_name
            task_result["task"] = task_name
            per_task_table.append(task_result)
    selection_table = sorted(
        table,
        key=lambda row: (row["top1_accuracy"], row["mrr"], row["mean_target_probability_mass"], row["method"]),
        reverse=True,
    )
    return {
        "schema_version": STAGE13_SCHEMA_VERSION,
        "stage": "stage13_positional_adapter",
        "dataset": "deterministic_ruler_style_non_phase_cued_retrieval_v1",
        "no_hardware_submission": True,
        "seeds": list(seeds),
        "context_lengths": list(context_lengths),
        "train_lengths": list(TRAIN_LENGTHS),
        "validation_lengths": list(VALIDATION_LENGTHS),
        "test_lengths": list(TEST_LENGTHS),
        "examples_per_task_length": examples_per_task_length,
        "train_row_count": len(splits["train"]),
        "validation_row_count": len(splits["validation"]),
        "test_row_count": len(splits["test"]),
        "method_names": list(METHOD_NAMES),
        "task_names": list(TASK_NAMES),
        "task": {
            "description": "Train-short/test-long positional-adapter benchmark on the Stage 12 non-phase-cued retrieval packet.",
            "target_construction": "Targets are inherited from Stage 12 explicit retrieval rules, not from PhaseWrap score maximization.",
            "note": "This is a compact positional-adapter experiment, not a production transformer benchmark or proof that PhaseWrap-RoPE replaces RoPE.",
        },
        "claim_boundary": {
            "supported": [
                "A deterministic train-short/test-long comparison of positional feature adapters on non-phase-cued retrieval rows.",
                "Evidence about whether PhaseWrap-derived residual/distance features can close the Stage 12 exact-offset retrieval gap.",
                "Bootstrap intervals over test rows for top-1, MRR, and target probability mass.",
            ],
            "excluded": [
                "production transformer superiority",
                "full transformer-scale validation",
                "broad quantum advantage",
                "general cross-backend robustness",
                "a claim that PhaseWrap-RoPE is a validated RoPE replacement",
            ],
        },
        "training_records": training_records,
        "table": table,
        "selection_table": selection_table,
        "task_table": per_task_table,
        "best_method_by_top1_mrr": selection_table[0]["method"],
    }


def write_stage13_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "dataset": result["dataset"],
        "no_hardware_submission": result["no_hardware_submission"],
        "train_lengths": result["train_lengths"],
        "validation_lengths": result["validation_lengths"],
        "test_lengths": result["test_lengths"],
        "train_row_count": result["train_row_count"],
        "validation_row_count": result["validation_row_count"],
        "test_row_count": result["test_row_count"],
        "method_names": result["method_names"],
        "task_names": result["task_names"],
        "result_path": str((output_dir / "results.json").as_posix()),
        "summary_csv_path": str((output_dir / "summary.csv").as_posix()),
        "task_summary_csv_path": str((output_dir / "task_summary.csv").as_posix()),
        "claim_boundary": result["claim_boundary"],
    }
    paths = {
        "manifest": str(output_dir / "manifest.json"),
        "results": str(output_dir / "results.json"),
        "summary_csv": str(output_dir / "summary.csv"),
        "task_summary_csv": str(output_dir / "task_summary.csv"),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(result["table"][0].keys()))
        writer.writeheader()
        writer.writerows(result["table"])
    with (output_dir / "task_summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(result["task_table"][0].keys()))
        writer.writeheader()
        writer.writerows(result["task_table"])
    return paths


def print_stage13_table(result: dict[str, Any]) -> None:
    columns = (
        "method",
        "row_count",
        "top1_accuracy",
        "top1_ci_low",
        "top1_ci_high",
        "mrr",
        "mrr_ci_low",
        "mrr_ci_high",
        "mean_target_probability_mass",
        "mean_first_relevant_rank",
    )
    print(" | ".join(columns))
    print(" | ".join("---" for _ in columns))
    for row in result["selection_table"]:
        print(" | ".join(str(row[column]) for column in columns))
