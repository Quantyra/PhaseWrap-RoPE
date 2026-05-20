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
from .stage13_positional_adapter import METHOD_NAMES


STAGE26_SCHEMA_VERSION = "qrope_stage26_compact_kv_qa_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage26_compact_kv_qa"
DEFAULT_SEEDS = (2601, 2611, 2621, 2633, 2647)
CONTEXT_LENGTHS = (256, 512, 1024, 2048)
TRAIN_LENGTHS = (256, 512)
VALIDATION_LENGTHS = (1024,)
TEST_LENGTHS = (2048,)
EXAMPLES_PER_LENGTH = 4
KEY_VOCAB_SIZE = 16
CANDIDATE_COUNT = 32


@dataclass(frozen=True)
class Stage26Example:
    example_id: str
    seed: int
    split: str
    sequence_length: int
    query_pos: int
    query_key: int
    candidate_positions: tuple[int, ...]
    candidate_keys: tuple[int, ...]
    candidate_values: tuple[int, ...]
    target_index: int
    target_position: int
    target_value: int


def _split_for_length(sequence_length: int) -> str:
    if sequence_length in TRAIN_LENGTHS:
        return "train"
    if sequence_length in VALIDATION_LENGTHS:
        return "validation"
    if sequence_length in TEST_LENGTHS:
        return "test"
    raise ValueError(f"unsupported sequence_length: {sequence_length}")


def make_stage26_examples(
    *,
    seeds: tuple[int, ...] = DEFAULT_SEEDS,
    context_lengths: tuple[int, ...] = CONTEXT_LENGTHS,
    examples_per_length: int = EXAMPLES_PER_LENGTH,
) -> list[Stage26Example]:
    rows: list[Stage26Example] = []
    for seed in seeds:
        for sequence_length in context_lengths:
            query_pos = sequence_length - 1
            for item_index in range(examples_per_length):
                rng = random.Random(f"stage26:{seed}:{sequence_length}:{item_index}")
                query_key = rng.randrange(KEY_VOCAB_SIZE)
                candidate_positions = sorted(rng.sample(range(4, query_pos - 4), CANDIDATE_COUNT))
                match_indices = sorted(rng.sample(range(CANDIDATE_COUNT), 3))
                candidate_keys = [rng.randrange(KEY_VOCAB_SIZE) for _ in range(CANDIDATE_COUNT)]
                for index in match_indices:
                    candidate_keys[index] = query_key
                for index, key in enumerate(candidate_keys):
                    if index not in match_indices and key == query_key:
                        candidate_keys[index] = (key + 1 + index) % KEY_VOCAB_SIZE
                target_index = max(match_indices, key=lambda index: candidate_positions[index])
                candidate_values = [
                    1 + ((seed * 31 + sequence_length * 17 + item_index * 13 + position * 7 + index * 19) % 997)
                    for index, position in enumerate(candidate_positions)
                ]
                rows.append(
                    Stage26Example(
                        example_id=f"kvqa_seed{seed}_L{sequence_length}_{item_index:03d}",
                        seed=seed,
                        split=_split_for_length(sequence_length),
                        sequence_length=sequence_length,
                        query_pos=query_pos,
                        query_key=query_key,
                        candidate_positions=tuple(candidate_positions),
                        candidate_keys=tuple(candidate_keys),
                        candidate_values=tuple(candidate_values),
                        target_index=target_index,
                        target_position=candidate_positions[target_index],
                        target_value=candidate_values[target_index],
                    )
                )
    return rows


def split_examples(rows: list[Stage26Example]) -> dict[str, list[Stage26Example]]:
    return {
        "train": [row for row in rows if row.split == "train"],
        "validation": [row for row in rows if row.split == "validation"],
        "test": [row for row in rows if row.split == "test"],
    }


def _phasewrap_score(delta: float) -> float:
    margins = []
    for period in (8, 12):
        residual = phase_residual(0, int(delta), period)
        margins.append(math.cos(residual) - math.cos(2.0 * math.pi / float(period)))
    return float(margins[0] * margins[1])


def candidate_features(row: Stage26Example, method_name: str) -> np.ndarray:
    deltas = row.query_pos - np.array(row.candidate_positions, dtype=float)
    content = np.array([1.0 if key == row.query_key else 0.0 for key in row.candidate_keys], dtype=float)
    recency = -deltas / float(row.query_pos)
    base = [np.ones(len(deltas)), content]
    if method_name == "no_position":
        return np.column_stack(base)
    if method_name == "alibi":
        return np.column_stack([*base, recency, content * recency])
    if method_name == "rope_relative":
        inv_freq = np.array([10_000.0 ** (-2.0 * index / 32.0) for index in range(16)], dtype=float)
        rope = np.cos(deltas[:, None] * inv_freq[None, :])
        return np.column_stack([*base, recency, rope, content[:, None] * rope])
    if method_name == "sinusoidal":
        periods = np.array((8.0, 16.0, 32.0, 64.0, 128.0), dtype=float)
        waves = np.cos(2.0 * math.pi * deltas[:, None] / periods[None, :])
        return np.column_stack([*base, recency, waves, content[:, None] * waves])
    phase_scores = np.array([_phasewrap_score(delta) for delta in deltas], dtype=float)
    residual8 = np.array([phase_residual(0, int(delta), 8) for delta in deltas], dtype=float)
    residual12 = np.array([phase_residual(0, int(delta), 12) for delta in deltas], dtype=float)
    cos8 = np.cos(residual8)
    cos12 = np.cos(residual12)
    if method_name == "phasewrap_score":
        return np.column_stack([*base, phase_scores, content * phase_scores])
    if method_name == "phasewrap_residual_adapter":
        phase = np.column_stack([phase_scores, cos8, cos12, cos8 * cos12])
        return np.column_stack([*base, recency, phase, content[:, None] * phase])
    if method_name == "phasewrap_distance_adapter":
        signed = deltas / float(row.query_pos)
        phase = np.column_stack([phase_scores, cos8, cos12, cos8 * cos12, recency, signed])
        return np.column_stack([*base, phase, content[:, None] * phase])
    raise ValueError(f"unknown method_name: {method_name}")


def _softmax(values: np.ndarray) -> np.ndarray:
    shifted = values - np.max(values)
    exp_values = np.exp(shifted)
    return exp_values / np.sum(exp_values)


def _loss_and_gradient(rows: list[Stage26Example], method_name: str, weights: np.ndarray, l2: float) -> tuple[float, np.ndarray]:
    total_loss = 0.0
    gradient = np.zeros_like(weights)
    for row in rows:
        features = candidate_features(row, method_name)
        probabilities = _softmax(features @ weights)
        target = np.zeros(len(row.candidate_positions), dtype=float)
        target[row.target_index] = 1.0
        total_loss += -math.log(max(float(probabilities[row.target_index]), 1e-12))
        gradient += features.T @ (probabilities - target)
    total_loss = total_loss / float(len(rows)) + 0.5 * l2 * float(weights @ weights)
    gradient = gradient / float(len(rows)) + l2 * weights
    return total_loss, gradient


def train_scorer(rows: list[Stage26Example], method_name: str, *, epochs: int = 260, learning_rate: float = 0.3, l2: float = 0.001) -> dict[str, Any]:
    weights = np.zeros(candidate_features(rows[0], method_name).shape[1], dtype=float)
    history: list[dict[str, float]] = []
    for epoch in range(epochs):
        loss, gradient = _loss_and_gradient(rows, method_name, weights, l2)
        weights -= learning_rate * gradient
        if epoch in {0, epochs // 2, epochs - 1}:
            history.append({"epoch": epoch + 1, "loss": round(float(loss), 6)})
    return {
        "method": method_name,
        "epochs": epochs,
        "learning_rate": learning_rate,
        "l2": l2,
        "weights": [round(float(value), 8) for value in weights.tolist()],
        "training_history": history,
        "final_training_loss": history[-1]["loss"],
    }


def _rank(probabilities: np.ndarray, target_index: int) -> int:
    ranked = sorted(range(len(probabilities)), key=lambda index: (-float(probabilities[index]), index))
    return ranked.index(target_index) + 1


def _bootstrap_ci(values: list[float], *, seed_text: str, iterations: int = 400) -> dict[str, float]:
    rng = random.Random(int(hashlib.sha256(seed_text.encode("utf-8")).hexdigest()[:16], 16))
    means: list[float] = []
    for _ in range(iterations):
        sample = [values[rng.randrange(len(values))] for _ in range(len(values))]
        means.append(float(sum(sample) / len(sample)))
    means.sort()
    return {"low": round(means[int(0.025 * (iterations - 1))], 6), "high": round(means[int(0.975 * (iterations - 1))], 6)}


def evaluate_scorer(rows: list[Stage26Example], method_name: str, weights: np.ndarray, *, split_name: str) -> dict[str, Any]:
    losses: list[float] = []
    top1_hits: list[float] = []
    reciprocal_ranks: list[float] = []
    target_probs: list[float] = []
    ranks: list[int] = []
    for row in rows:
        probabilities = _softmax(candidate_features(row, method_name) @ weights)
        rank = _rank(probabilities, row.target_index)
        target_probability = max(float(probabilities[row.target_index]), 1e-12)
        losses.append(-math.log(target_probability))
        top1_hits.append(1.0 if rank == 1 else 0.0)
        reciprocal_ranks.append(1.0 / float(rank))
        target_probs.append(target_probability)
        ranks.append(rank)
    mean_loss = float(np.mean(losses))
    top1_ci = _bootstrap_ci(top1_hits, seed_text=f"stage26:{method_name}:{split_name}:top1")
    mrr_ci = _bootstrap_ci(reciprocal_ranks, seed_text=f"stage26:{method_name}:{split_name}:mrr")
    return {
        "method": method_name,
        "split": split_name,
        "row_count": len(rows),
        "loss": round(mean_loss, 6),
        "perplexity": round(float(math.exp(mean_loss)), 6),
        "top1_accuracy": round(float(np.mean(top1_hits)), 6),
        "top1_ci_low": top1_ci["low"],
        "top1_ci_high": top1_ci["high"],
        "mrr": round(float(np.mean(reciprocal_ranks)), 6),
        "mrr_ci_low": mrr_ci["low"],
        "mrr_ci_high": mrr_ci["high"],
        "mean_target_probability": round(float(np.mean(target_probs)), 6),
        "mean_first_relevant_rank": round(float(np.mean(ranks)), 6),
    }


def run_stage26_benchmark(
    *,
    seeds: tuple[int, ...] = DEFAULT_SEEDS,
    context_lengths: tuple[int, ...] = CONTEXT_LENGTHS,
    examples_per_length: int = EXAMPLES_PER_LENGTH,
    epochs: int = 260,
    method_names: tuple[str, ...] = METHOD_NAMES,
) -> dict[str, Any]:
    rows = make_stage26_examples(seeds=seeds, context_lengths=context_lengths, examples_per_length=examples_per_length)
    splits = split_examples(rows)
    table: list[dict[str, Any]] = []
    training_records: list[dict[str, Any]] = []
    weak_runs: list[dict[str, Any]] = []
    for method_name in method_names:
        training = train_scorer(splits["train"], method_name, epochs=epochs)
        training_records.append(training)
        weights = np.array(training["weights"], dtype=float)
        for split_name in ("train", "validation", "test"):
            row = evaluate_scorer(splits[split_name], method_name, weights, split_name=split_name)
            table.append(row)
            if split_name == "test" and float(row["top1_accuracy"]) < 0.5:
                weak_runs.append({"method": method_name, "top1_accuracy": row["top1_accuracy"], "mrr": row["mrr"], "criterion": "test_top1_accuracy_below_0.5"})
    test_rows = [row for row in table if row["split"] == "test"]
    selection_table = sorted(test_rows, key=lambda row: (row["top1_accuracy"], row["mrr"], row["mean_target_probability"], row["method"]), reverse=True)
    return {
        "schema_version": STAGE26_SCHEMA_VERSION,
        "stage": "stage26_compact_kv_qa",
        "dataset": "deterministic_compact_key_value_qa_retrieval_v1",
        "no_hardware_submission": True,
        "seeds": list(seeds),
        "context_lengths": list(context_lengths),
        "train_lengths": list(TRAIN_LENGTHS),
        "validation_lengths": list(VALIDATION_LENGTHS),
        "test_lengths": list(TEST_LENGTHS),
        "examples_per_length": examples_per_length,
        "candidate_count": CANDIDATE_COUNT,
        "method_names": list(method_names),
        "train_row_count": len(splits["train"]),
        "validation_row_count": len(splits["validation"]),
        "test_row_count": len(splits["test"]),
        "epochs": epochs,
        "weak_runs": weak_runs,
        "claim_boundary": {
            "supported": [
                "A deterministic compact key-value QA retrieval benchmark with explicit content keys and train-short/test-long contexts.",
                "Evidence about whether positional mechanisms help select the latest matching key among distractors.",
                "Bootstrap intervals over rows and reported weak runs under a predeclared top-1 threshold.",
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
        "best_method_by_test_top1_mrr": selection_table[0]["method"],
    }


def write_stage26_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "dataset": result["dataset"],
        "no_hardware_submission": result["no_hardware_submission"],
        "method_names": result["method_names"],
        "train_row_count": result["train_row_count"],
        "validation_row_count": result["validation_row_count"],
        "test_row_count": result["test_row_count"],
        "result_path": str((output_dir / "results.json").as_posix()),
        "summary_csv_path": str((output_dir / "summary.csv").as_posix()),
        "weak_runs_path": str((output_dir / "weak_runs.json").as_posix()),
        "claim_boundary": result["claim_boundary"],
    }
    paths = {"manifest": str(output_dir / "manifest.json"), "results": str(output_dir / "results.json"), "summary_csv": str(output_dir / "summary.csv"), "weak_runs": str(output_dir / "weak_runs.json")}
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "weak_runs.json").write_text(json.dumps(result["weak_runs"], indent=2, sort_keys=True), encoding="utf-8")
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(result["table"][0].keys()))
        writer.writeheader()
        writer.writerows(result["table"])
    return paths


def print_stage26_table(result: dict[str, Any]) -> None:
    columns = ("method", "split", "row_count", "top1_accuracy", "mrr", "mean_target_probability", "mean_first_relevant_rank")
    print(" | ".join(columns))
    print(" | ".join("---" for _ in columns))
    for row in result["table"]:
        print(" | ".join(str(row[column]) for column in columns))
