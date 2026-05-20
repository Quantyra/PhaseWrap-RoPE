from __future__ import annotations

import csv
import hashlib
import json
import math
import random
from dataclasses import dataclass
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
from .stage13_positional_adapter import METHOD_NAMES, positional_features


STAGE14_SCHEMA_VERSION = "qrope_stage14_attention_readout_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage14_attention_readout"
TRAIN_LENGTHS = (128, 256)
VALIDATION_LENGTHS = (512,)
TEST_LENGTHS = (1024,)
VALUE_VOCAB_SIZE = 257


@dataclass(frozen=True)
class Stage14Example:
    example_id: str
    seed: int
    task: str
    sequence_length: int
    query_pos: int
    reference_delta: int
    key_positions: tuple[int, ...]
    target_positions: tuple[int, ...]
    candidate_values: tuple[int, ...]
    target_values: tuple[int, ...]
    source_stage12_id: str


def make_stage14_examples(
    *,
    seeds: tuple[int, ...] = DEFAULT_SEEDS,
    context_lengths: tuple[int, ...] = DEFAULT_CONTEXT_LENGTHS,
    examples_per_task_length: int = DEFAULT_EXAMPLES_PER_TASK_LENGTH,
) -> list[Stage14Example]:
    stage12_rows = make_stage12_examples(
        seeds=seeds,
        context_lengths=context_lengths,
        examples_per_task_length=examples_per_task_length,
    )
    rows: list[Stage14Example] = []
    for row in stage12_rows:
        candidate_values = []
        for index, position in enumerate(row.key_positions):
            token = 1 + ((row.seed * 37 + row.sequence_length * 11 + position * 7 + index * 13) % (VALUE_VOCAB_SIZE - 1))
            candidate_values.append(int(token))
        target_values = tuple(candidate_values[row.key_positions.index(position)] for position in row.target_positions)
        rows.append(
            Stage14Example(
                example_id=f"stage14_{row.example_id}",
                seed=row.seed,
                task=row.task,
                sequence_length=row.sequence_length,
                query_pos=row.query_pos,
                reference_delta=row.reference_delta,
                key_positions=row.key_positions,
                target_positions=row.target_positions,
                candidate_values=tuple(candidate_values),
                target_values=target_values,
                source_stage12_id=row.example_id,
            )
        )
    return rows


def split_examples(rows: list[Stage14Example]) -> dict[str, list[Stage14Example]]:
    return {
        "train": [row for row in rows if row.sequence_length in TRAIN_LENGTHS],
        "validation": [row for row in rows if row.sequence_length in VALIDATION_LENGTHS],
        "test": [row for row in rows if row.sequence_length in TEST_LENGTHS],
    }


def _stage12_proxy(row: Stage14Example) -> Stage12Example:
    return Stage12Example(
        example_id=row.source_stage12_id,
        seed=row.seed,
        task=row.task,
        sequence_length=row.sequence_length,
        query_pos=row.query_pos,
        query_token=0,
        reference_delta=row.reference_delta,
        target_positions=row.target_positions,
        target_deltas=tuple(row.query_pos - position for position in row.target_positions),
        tokens=tuple(0 for _ in range(row.sequence_length)),
        key_positions=row.key_positions,
        target_rule="stage14 proxy",
    )


def _softmax(values: np.ndarray) -> np.ndarray:
    shifted = values - np.max(values)
    exp_values = np.exp(shifted)
    return exp_values / np.sum(exp_values)


def _target_distribution(row: Stage14Example) -> np.ndarray:
    targets = np.zeros(len(row.key_positions), dtype=float)
    for position in row.target_positions:
        targets[row.key_positions.index(position)] = 1.0 / float(len(row.target_positions))
    return targets


def _attention_distribution(row: Stage14Example, method_name: str, weights: np.ndarray) -> np.ndarray:
    features = positional_features(_stage12_proxy(row), method_name)
    return _softmax(features @ weights)


def _value_distribution(row: Stage14Example, attention: np.ndarray) -> np.ndarray:
    values = np.zeros(VALUE_VOCAB_SIZE, dtype=float)
    for probability, token_id in zip(attention, row.candidate_values):
        values[token_id] += float(probability)
    return values


def _loss_and_gradient(rows: list[Stage14Example], method_name: str, weights: np.ndarray, l2: float) -> tuple[float, np.ndarray]:
    total_loss = 0.0
    gradient = np.zeros_like(weights)
    for row in rows:
        features = positional_features(_stage12_proxy(row), method_name)
        attention = _softmax(features @ weights)
        targets = _target_distribution(row)
        target_indices = [row.key_positions.index(position) for position in row.target_positions]
        target_mass = max(float(np.sum(attention[target_indices])), 1e-12)
        total_loss += -math.log(target_mass)
        gradient += features.T @ (attention - targets)
    total_loss = total_loss / float(len(rows)) + 0.5 * l2 * float(weights @ weights)
    gradient = gradient / float(len(rows)) + l2 * weights
    return float(total_loss), gradient


def train_readout(
    rows: list[Stage14Example],
    method_name: str,
    *,
    epochs: int = 220,
    learning_rate: float = 0.35,
    l2: float = 0.001,
) -> dict[str, Any]:
    if not rows:
        raise ValueError("rows must be non-empty")
    weights = np.zeros(positional_features(_stage12_proxy(rows[0]), method_name).shape[1], dtype=float)
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


def _ranked_indices(values: np.ndarray) -> list[int]:
    return sorted(range(len(values)), key=lambda index: (-float(values[index]), index))


def _first_relevant_rank(values: np.ndarray, targets: tuple[int, ...]) -> int:
    target_set = set(targets)
    for rank, index in enumerate(_ranked_indices(values), start=1):
        if index in target_set:
            return rank
    raise RuntimeError("target absent from distribution")


def _bootstrap_ci(values: list[float], *, seed_text: str, iterations: int = 600) -> dict[str, float]:
    if not values:
        raise ValueError("cannot bootstrap an empty metric list")
    rng = random.Random(int(hashlib.sha256(seed_text.encode("utf-8")).hexdigest()[:16], 16))
    means: list[float] = []
    for _ in range(iterations):
        sample = [values[rng.randrange(len(values))] for _ in range(len(values))]
        means.append(float(sum(sample) / len(sample)))
    means.sort()
    return {
        "low": round(means[int(0.025 * (iterations - 1))], 6),
        "high": round(means[int(0.975 * (iterations - 1))], 6),
    }


def evaluate_readout(rows: list[Stage14Example], method_name: str, weights: np.ndarray) -> dict[str, Any]:
    losses: list[float] = []
    top1_hits: list[float] = []
    reciprocal_ranks: list[float] = []
    target_masses: list[float] = []
    ranks: list[int] = []
    for row in rows:
        attention = _attention_distribution(row, method_name, weights)
        values = _value_distribution(row, attention)
        target_mass = max(float(np.sum(values[list(row.target_values)])), 1e-12)
        rank = _first_relevant_rank(values, row.target_values)
        top_value = _ranked_indices(values)[0]
        losses.append(-math.log(target_mass))
        top1_hits.append(1.0 if top_value in set(row.target_values) else 0.0)
        reciprocal_ranks.append(1.0 / float(rank))
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
        "mean_target_value_probability": round(target_mass_mean, 6),
        "target_value_probability_ci_low": _bootstrap_ci(target_masses, seed_text=f"{method_name}:prob")["low"],
        "target_value_probability_ci_high": _bootstrap_ci(target_masses, seed_text=f"{method_name}:prob")["high"],
        "mean_first_relevant_value_rank": round(float(np.mean(ranks)), 6),
    }


def run_stage14_benchmark(
    *,
    seeds: tuple[int, ...] = DEFAULT_SEEDS,
    context_lengths: tuple[int, ...] = DEFAULT_CONTEXT_LENGTHS,
    examples_per_task_length: int = DEFAULT_EXAMPLES_PER_TASK_LENGTH,
    epochs: int = 220,
) -> dict[str, Any]:
    rows = make_stage14_examples(
        seeds=seeds,
        context_lengths=context_lengths,
        examples_per_task_length=examples_per_task_length,
    )
    splits = split_examples(rows)
    table: list[dict[str, Any]] = []
    task_table: list[dict[str, Any]] = []
    training_records: list[dict[str, Any]] = []
    for method_name in METHOD_NAMES:
        training = train_readout(splits["train"], method_name, epochs=epochs)
        weights = np.array(training["weights"], dtype=float)
        training_records.append(training)
        row = evaluate_readout(splits["test"], method_name, weights)
        row["method"] = method_name
        table.append(row)
        for task_name in TASK_NAMES:
            task_rows = [example for example in splits["test"] if example.task == task_name]
            task_result = evaluate_readout(task_rows, method_name, weights)
            task_result["method"] = method_name
            task_result["task"] = task_name
            task_table.append(task_result)
    selection_table = sorted(
        table,
        key=lambda row: (row["top1_accuracy"], row["mrr"], row["mean_target_value_probability"], row["method"]),
        reverse=True,
    )
    return {
        "schema_version": STAGE14_SCHEMA_VERSION,
        "stage": "stage14_attention_readout",
        "dataset": "deterministic_non_phase_cued_key_value_attention_readout_v1",
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
            "description": "Train-short/test-long decoder attention readout over key-value retrieval rows derived from Stage 12.",
            "target_construction": "Targets are explicit retrieval-rule value tokens, not PhaseWrap-selected positions.",
            "note": "This isolates attention readout behavior. It is not a full language-model benchmark or proof that PhaseWrap-RoPE replaces RoPE.",
        },
        "claim_boundary": {
            "supported": [
                "A deterministic attention-readout comparison using non-phase-cued key-value retrieval targets.",
                "Evidence about whether PhaseWrap-derived adapters can retrieve held-out value tokens under train-short/test-long context extrapolation.",
                "Bootstrap intervals over held-out test rows for top-1, MRR, and target value probability.",
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
        "task_table": task_table,
        "best_method_by_top1_mrr": selection_table[0]["method"],
    }


def write_stage14_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
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


def print_stage14_table(result: dict[str, Any]) -> None:
    columns = (
        "method",
        "row_count",
        "top1_accuracy",
        "top1_ci_low",
        "top1_ci_high",
        "mrr",
        "mrr_ci_low",
        "mrr_ci_high",
        "mean_target_value_probability",
        "mean_first_relevant_value_rank",
    )
    print(" | ".join(columns))
    print(" | ".join("---" for _ in columns))
    for row in result["selection_table"]:
        print(" | ".join(str(row[column]) for column in columns))
