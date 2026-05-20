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
    TASK_NAMES,
    VALUE_VOCAB_SIZE,
    Stage14Example,
    _stage12_proxy,
    make_stage14_examples,
    split_examples,
)


STAGE20_SCHEMA_VERSION = "qrope_stage20_hardened_positional_value_model_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage20_hardened_positional_value_model"
EMBED_DIM = 12


def _softmax(values: np.ndarray) -> np.ndarray:
    shifted = values - np.max(values)
    exp_values = np.exp(shifted)
    return exp_values / np.sum(exp_values)


def _target_distribution(row: Stage14Example) -> np.ndarray:
    target = np.zeros(VALUE_VOCAB_SIZE, dtype=float)
    for token_id in row.target_values:
        target[token_id] = 1.0 / float(len(row.target_values))
    return target


def _init_params(method_name: str, feature_dim: int, seed: int, embed_dim: int) -> dict[str, np.ndarray]:
    digest = hashlib.sha256(f"stage20:{method_name}:{seed}:{embed_dim}".encode("utf-8")).hexdigest()
    rng = np.random.default_rng(int(digest[:16], 16) % (2**32))
    return {
        "attention_w": rng.normal(0.0, 0.02, size=feature_dim),
        "value_embedding": rng.normal(0.0, 0.04, size=(VALUE_VOCAB_SIZE, embed_dim)),
        "output_w": rng.normal(0.0, 0.04, size=(embed_dim, VALUE_VOCAB_SIZE)),
        "output_b": np.zeros(VALUE_VOCAB_SIZE, dtype=float),
    }


def _forward(row: Stage14Example, method_name: str, params: dict[str, np.ndarray]) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    features = positional_features(_stage12_proxy(row), method_name)
    attention = _softmax(features @ params["attention_w"])
    value_ids = np.array(row.candidate_values, dtype=int)
    candidate_embeddings = params["value_embedding"][value_ids]
    context = attention @ candidate_embeddings
    logits = context @ params["output_w"] + params["output_b"]
    probabilities = _softmax(logits)
    return probabilities, {
        "features": features,
        "attention": attention,
        "value_ids": value_ids,
        "candidate_embeddings": candidate_embeddings,
        "context": context,
    }


def _loss_and_gradient(
    rows: list[Stage14Example],
    method_name: str,
    params: dict[str, np.ndarray],
    l2: float,
) -> tuple[float, dict[str, np.ndarray]]:
    grads = {key: np.zeros_like(value) for key, value in params.items()}
    total_loss = 0.0
    for row in rows:
        target = _target_distribution(row)
        probabilities, cache = _forward(row, method_name, params)
        target_mass = max(float(np.sum(probabilities[target > 0.0])), 1e-12)
        total_loss += -math.log(target_mass)
        grad_logits = probabilities - target
        context = cache["context"]
        grads["output_w"] += np.outer(context, grad_logits)
        grads["output_b"] += grad_logits
        grad_context = grad_logits @ params["output_w"].T
        candidate_embeddings = cache["candidate_embeddings"]
        attention = cache["attention"]
        grad_attention = candidate_embeddings @ grad_context
        grad_attention_logits = attention * (grad_attention - float(grad_attention @ attention))
        grads["attention_w"] += cache["features"].T @ grad_attention_logits
        for candidate_index, token_id in enumerate(cache["value_ids"]):
            grads["value_embedding"][token_id] += attention[candidate_index] * grad_context
    scale = 1.0 / float(len(rows))
    total_loss *= scale
    for key in grads:
        grads[key] *= scale
        if key != "output_b":
            total_loss += 0.5 * l2 * float(np.sum(params[key] * params[key]))
            grads[key] += l2 * params[key]
    return float(total_loss), grads


def train_hardened_positional_value_model(
    rows: list[Stage14Example],
    method_name: str,
    *,
    seed: int = 2001,
    epochs: int = 500,
    learning_rate: float = 0.03,
    l2: float = 0.00001,
    embed_dim: int = EMBED_DIM,
) -> dict[str, Any]:
    if not rows:
        raise ValueError("rows must be non-empty")
    feature_dim = positional_features(_stage12_proxy(rows[0]), method_name).shape[1]
    params = _init_params(method_name, feature_dim, seed, embed_dim)
    moments = {key: np.zeros_like(value) for key, value in params.items()}
    velocities = {key: np.zeros_like(value) for key, value in params.items()}
    beta1 = 0.9
    beta2 = 0.999
    epsilon = 1e-8
    history: list[dict[str, float]] = []
    for epoch in range(1, epochs + 1):
        loss, grads = _loss_and_gradient(rows, method_name, params, l2)
        for key in params:
            moments[key] = beta1 * moments[key] + (1.0 - beta1) * grads[key]
            velocities[key] = beta2 * velocities[key] + (1.0 - beta2) * (grads[key] * grads[key])
            moment_hat = moments[key] / (1.0 - beta1**epoch)
            velocity_hat = velocities[key] / (1.0 - beta2**epoch)
            params[key] -= learning_rate * moment_hat / (np.sqrt(velocity_hat) + epsilon)
        if epoch in {1, epochs // 4, epochs // 2, (3 * epochs) // 4, epochs}:
            history.append({"epoch": epoch, "loss": round(loss, 6)})
    return {
        "method": method_name,
        "seed": seed,
        "epochs": epochs,
        "learning_rate": learning_rate,
        "l2": l2,
        "embed_dim": embed_dim,
        "optimizer": "full_batch_adam",
        "params": {key: np.round(value, 8).tolist() for key, value in params.items()},
        "training_history": history,
        "final_training_loss": history[-1]["loss"],
    }


def _params_from_record(record: dict[str, Any]) -> dict[str, np.ndarray]:
    return {key: np.array(value, dtype=float) for key, value in record["params"].items()}


def _ranked_indices(values: np.ndarray) -> list[int]:
    return sorted(range(len(values)), key=lambda index: (-float(values[index]), index))


def _first_relevant_rank(values: np.ndarray, targets: tuple[int, ...]) -> int:
    target_set = set(targets)
    for rank, index in enumerate(_ranked_indices(values), start=1):
        if index in target_set:
            return rank
    raise RuntimeError("target absent from distribution")


def _bootstrap_ci(values: list[float], *, seed_text: str, iterations: int = 600) -> dict[str, float]:
    rng = random.Random(int(hashlib.sha256(seed_text.encode("utf-8")).hexdigest()[:16], 16))
    means: list[float] = []
    for _ in range(iterations):
        sample = [values[rng.randrange(len(values))] for _ in range(len(values))]
        means.append(float(sum(sample) / len(sample)))
    means.sort()
    return {"low": round(means[int(0.025 * (iterations - 1))], 6), "high": round(means[int(0.975 * (iterations - 1))], 6)}


def evaluate_hardened_positional_value_model(rows: list[Stage14Example], method_name: str, params: dict[str, np.ndarray], *, split_name: str) -> dict[str, Any]:
    losses: list[float] = []
    top1_hits: list[float] = []
    reciprocal_ranks: list[float] = []
    target_masses: list[float] = []
    ranks: list[int] = []
    for row in rows:
        probabilities, _ = _forward(row, method_name, params)
        target_mass = max(float(np.sum(probabilities[list(row.target_values)])), 1e-12)
        rank = _first_relevant_rank(probabilities, row.target_values)
        top_value = _ranked_indices(probabilities)[0]
        losses.append(-math.log(target_mass))
        top1_hits.append(1.0 if top_value in set(row.target_values) else 0.0)
        reciprocal_ranks.append(1.0 / float(rank))
        target_masses.append(target_mass)
        ranks.append(rank)
    mean_loss = float(np.mean(losses))
    top1_ci = _bootstrap_ci(top1_hits, seed_text=f"{method_name}:{split_name}:top1")
    mrr_ci = _bootstrap_ci(reciprocal_ranks, seed_text=f"{method_name}:{split_name}:mrr")
    prob_ci = _bootstrap_ci(target_masses, seed_text=f"{method_name}:{split_name}:prob")
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
        "mean_target_value_probability": round(float(np.mean(target_masses)), 6),
        "target_value_probability_ci_low": prob_ci["low"],
        "target_value_probability_ci_high": prob_ci["high"],
        "mean_first_relevant_value_rank": round(float(np.mean(ranks)), 6),
    }


def run_stage20_benchmark(
    *,
    seeds: tuple[int, ...] = DEFAULT_SEEDS,
    context_lengths: tuple[int, ...] = DEFAULT_CONTEXT_LENGTHS,
    examples_per_task_length: int = DEFAULT_EXAMPLES_PER_TASK_LENGTH,
    epochs: int = 500,
    method_names: tuple[str, ...] = METHOD_NAMES,
    init_seed: int = 2001,
) -> dict[str, Any]:
    rows = make_stage14_examples(seeds=seeds, context_lengths=context_lengths, examples_per_task_length=examples_per_task_length)
    splits = split_examples(rows)
    table: list[dict[str, Any]] = []
    task_table: list[dict[str, Any]] = []
    training_records: list[dict[str, Any]] = []
    for method_name in method_names:
        training = train_hardened_positional_value_model(splits["train"], method_name, epochs=epochs, seed=init_seed)
        params = _params_from_record(training)
        training_records.append(training)
        for split_name in ("train", "validation", "test"):
            table.append(evaluate_hardened_positional_value_model(splits[split_name], method_name, params, split_name=split_name))
        for task_name in TASK_NAMES:
            task_rows = [example for example in splits["test"] if example.task == task_name]
            task_table.append(
                {
                    **evaluate_hardened_positional_value_model(task_rows, method_name, params, split_name=f"test:{task_name}"),
                    "task": task_name,
                }
            )
    test_rows = [row for row in table if row["split"] == "test"]
    selection_table = sorted(
        test_rows,
        key=lambda row: (row["top1_accuracy"], row["mrr"], row["mean_target_value_probability"], row["method"]),
        reverse=True,
    )
    return {
        "schema_version": STAGE20_SCHEMA_VERSION,
        "stage": "stage20_hardened_positional_value_model",
        "dataset": "deterministic_hardened_positional_value_model_v1",
        "no_hardware_submission": True,
        "seeds": list(seeds),
        "context_lengths": list(context_lengths),
        "examples_per_task_length": examples_per_task_length,
        "init_seed": init_seed,
        "train_row_count": len(splits["train"]),
        "validation_row_count": len(splits["validation"]),
        "test_row_count": len(splits["test"]),
        "method_names": list(method_names),
        "task_names": list(TASK_NAMES),
        "model": {
            "type": "learned_positional_attention_with_hardened_value_output",
            "embed_dim": EMBED_DIM,
            "value_vocab_size": VALUE_VOCAB_SIZE,
            "epochs": epochs,
            "init_seed": init_seed,
            "optimizer": "full_batch_adam",
            "trained_parameters": "attention feature weights, value embeddings, output projection, output bias",
        },
        "claim_boundary": {
            "supported": [
                "A deterministic local comparison of learned positional attention feature families using the hardened value-output path.",
                "Evidence about whether PhaseWrap-derived features remain competitive when positional attention is reintroduced on the Stage 14 value-token rows.",
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
        "best_method_by_test_top1_mrr": selection_table[0]["method"],
    }


def write_stage20_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "dataset": result["dataset"],
        "no_hardware_submission": result["no_hardware_submission"],
        "train_row_count": result["train_row_count"],
        "validation_row_count": result["validation_row_count"],
        "test_row_count": result["test_row_count"],
        "method_names": result["method_names"],
        "task_names": result["task_names"],
        "model": result["model"],
        "init_seed": result["init_seed"],
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
    public_result = dict(result)
    public_result["training_records"] = [{key: value for key, value in record.items() if key != "params"} for record in result["training_records"]]
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(public_result, indent=2, sort_keys=True), encoding="utf-8")
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(result["table"][0].keys()))
        writer.writeheader()
        writer.writerows(result["table"])
    with (output_dir / "task_summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(result["task_table"][0].keys()))
        writer.writeheader()
        writer.writerows(result["task_table"])
    return paths


def print_stage20_table(result: dict[str, Any]) -> None:
    columns = ("method", "split", "row_count", "top1_accuracy", "mrr", "mean_target_value_probability", "mean_first_relevant_value_rank")
    print(" | ".join(columns))
    print(" | ".join("---" for _ in columns))
    for row in result["table"]:
        print(" | ".join(str(row[column]) for column in columns))
