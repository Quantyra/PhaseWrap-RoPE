from __future__ import annotations

import csv
import hashlib
import json
import math
import random
from pathlib import Path
from typing import Any

import numpy as np

from .stage13_positional_adapter import METHOD_NAMES, positional_features
from .stage14_attention_readout import (
    DEFAULT_CONTEXT_LENGTHS,
    DEFAULT_EXAMPLES_PER_TASK_LENGTH,
    DEFAULT_SEEDS,
    DEFAULT_OUTPUT_DIR as STAGE14_OUTPUT_DIR,
    TASK_NAMES,
    Stage14Example,
    _stage12_proxy,
    make_stage14_examples,
    split_examples,
)


STAGE15_SCHEMA_VERSION = "qrope_stage15_learned_attention_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage15_learned_attention"
HIDDEN_DIM = 8


def _softmax(values: np.ndarray) -> np.ndarray:
    shifted = values - np.max(values)
    exp_values = np.exp(shifted)
    return exp_values / np.sum(exp_values)


def _target_distribution(row: Stage14Example) -> np.ndarray:
    targets = np.zeros(len(row.key_positions), dtype=float)
    for position in row.target_positions:
        targets[row.key_positions.index(position)] = 1.0 / float(len(row.target_positions))
    return targets


def _init_params(feature_dim: int, seed_text: str, hidden_dim: int = HIDDEN_DIM) -> dict[str, np.ndarray]:
    seed = int(hashlib.sha256(seed_text.encode("utf-8")).hexdigest()[:16], 16) % (2**32)
    rng = np.random.default_rng(seed)
    return {
        "w1": rng.normal(0.0, 0.03, size=(feature_dim, hidden_dim)),
        "b1": np.zeros(hidden_dim, dtype=float),
        "w2": rng.normal(0.0, 0.03, size=hidden_dim),
        "b2": np.zeros(1, dtype=float),
    }


def _forward(row: Stage14Example, method_name: str, params: dict[str, np.ndarray]) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    features = positional_features(_stage12_proxy(row), method_name)
    hidden_pre = features @ params["w1"] + params["b1"]
    hidden = np.tanh(hidden_pre)
    logits = hidden @ params["w2"] + float(params["b2"][0])
    probabilities = _softmax(logits)
    cache = {"features": features, "hidden": hidden, "probabilities": probabilities}
    return probabilities, cache


def _loss_and_gradient(
    rows: list[Stage14Example],
    method_name: str,
    params: dict[str, np.ndarray],
    l2: float,
) -> tuple[float, dict[str, np.ndarray]]:
    grads = {key: np.zeros_like(value) for key, value in params.items()}
    total_loss = 0.0
    for row in rows:
        targets = _target_distribution(row)
        probabilities, cache = _forward(row, method_name, params)
        target_mass = max(float(np.sum(probabilities[targets > 0.0])), 1e-12)
        total_loss += -math.log(target_mass)
        grad_logits = probabilities - targets
        hidden = cache["hidden"]
        features = cache["features"]
        grads["w2"] += hidden.T @ grad_logits
        grads["b2"] += np.array([float(np.sum(grad_logits))])
        grad_hidden = grad_logits[:, None] * params["w2"][None, :]
        grad_hidden_pre = grad_hidden * (1.0 - hidden * hidden)
        grads["w1"] += features.T @ grad_hidden_pre
        grads["b1"] += np.sum(grad_hidden_pre, axis=0)
    scale = 1.0 / float(len(rows))
    total_loss *= scale
    for key in grads:
        grads[key] *= scale
        if key.startswith("w"):
            total_loss += 0.5 * l2 * float(np.sum(params[key] * params[key]))
            grads[key] += l2 * params[key]
    return float(total_loss), grads


def train_learned_attention(
    rows: list[Stage14Example],
    method_name: str,
    *,
    epochs: int = 180,
    learning_rate: float = 0.2,
    l2: float = 0.001,
    hidden_dim: int = HIDDEN_DIM,
) -> dict[str, Any]:
    if not rows:
        raise ValueError("rows must be non-empty")
    feature_dim = positional_features(_stage12_proxy(rows[0]), method_name).shape[1]
    params = _init_params(feature_dim, f"stage15:{method_name}:{hidden_dim}", hidden_dim=hidden_dim)
    history: list[dict[str, float]] = []
    for epoch in range(epochs):
        loss, grads = _loss_and_gradient(rows, method_name, params, l2)
        for key in params:
            params[key] -= learning_rate * grads[key]
        if epoch in {0, epochs // 4, epochs // 2, epochs - 1}:
            history.append({"epoch": epoch + 1, "loss": round(loss, 6)})
    return {
        "method": method_name,
        "epochs": epochs,
        "learning_rate": learning_rate,
        "l2": l2,
        "hidden_dim": hidden_dim,
        "params": {key: np.round(value, 8).tolist() for key, value in params.items()},
        "training_history": history,
        "final_training_loss": history[-1]["loss"],
    }


def _params_from_record(record: dict[str, Any]) -> dict[str, np.ndarray]:
    return {key: np.array(value, dtype=float) for key, value in record["params"].items()}


def _value_distribution(row: Stage14Example, attention: np.ndarray) -> np.ndarray:
    max_value = max(max(row.candidate_values), max(row.target_values)) + 1
    values = np.zeros(max_value, dtype=float)
    for probability, token_id in zip(attention, row.candidate_values):
        values[token_id] += float(probability)
    return values


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


def evaluate_learned_attention(rows: list[Stage14Example], method_name: str, params: dict[str, np.ndarray]) -> dict[str, Any]:
    losses: list[float] = []
    top1_hits: list[float] = []
    reciprocal_ranks: list[float] = []
    target_masses: list[float] = []
    ranks: list[int] = []
    for row in rows:
        attention, _ = _forward(row, method_name, params)
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


def run_stage15_benchmark(
    *,
    seeds: tuple[int, ...] = DEFAULT_SEEDS,
    context_lengths: tuple[int, ...] = DEFAULT_CONTEXT_LENGTHS,
    examples_per_task_length: int = DEFAULT_EXAMPLES_PER_TASK_LENGTH,
    epochs: int = 180,
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
        training = train_learned_attention(splits["train"], method_name, epochs=epochs)
        training_records.append(training)
        params = _params_from_record(training)
        row = evaluate_learned_attention(splits["test"], method_name, params)
        row["method"] = method_name
        table.append(row)
        for task_name in TASK_NAMES:
            task_rows = [example for example in splits["test"] if example.task == task_name]
            task_result = evaluate_learned_attention(task_rows, method_name, params)
            task_result["method"] = method_name
            task_result["task"] = task_name
            task_table.append(task_result)
    selection_table = sorted(
        table,
        key=lambda row: (row["top1_accuracy"], row["mrr"], row["mean_target_value_probability"], row["method"]),
        reverse=True,
    )
    return {
        "schema_version": STAGE15_SCHEMA_VERSION,
        "stage": "stage15_learned_attention",
        "dataset": "deterministic_non_phase_cued_key_value_learned_attention_v1",
        "no_hardware_submission": True,
        "source_stage14_output_dir": str(STAGE14_OUTPUT_DIR.as_posix()),
        "seeds": list(seeds),
        "context_lengths": list(context_lengths),
        "train_lengths": [128, 256],
        "validation_lengths": [512],
        "test_lengths": [1024],
        "examples_per_task_length": examples_per_task_length,
        "train_row_count": len(splits["train"]),
        "validation_row_count": len(splits["validation"]),
        "test_row_count": len(splits["test"]),
        "method_names": list(METHOD_NAMES),
        "task_names": list(TASK_NAMES),
        "model": {
            "type": "one_hidden_layer_attention_scorer_over_positional_features",
            "hidden_dim": HIDDEN_DIM,
            "epochs": epochs,
            "trained_parameters": "feature-to-hidden weights, hidden bias, hidden-to-logit weights, logit bias",
        },
        "task": {
            "description": "Learned attention scorer over Stage 14 non-phase-cued key-value readout rows.",
            "target_construction": "Targets are explicit retrieval-rule value tokens, not PhaseWrap-selected positions.",
            "note": "This is a compact learned attention-readout benchmark, not a full decoder-only transformer or proof that PhaseWrap-RoPE replaces RoPE.",
        },
        "claim_boundary": {
            "supported": [
                "A deterministic train-short/test-long learned attention-readout comparison on non-phase-cued key-value rows.",
                "Evidence about whether a nonlinear scorer over PhaseWrap-derived features preserves Stage 14 value retrieval behavior.",
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


def write_stage15_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
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
        "model": result["model"],
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


def print_stage15_table(result: dict[str, Any]) -> None:
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
