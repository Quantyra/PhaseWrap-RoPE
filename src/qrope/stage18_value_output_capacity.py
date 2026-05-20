from __future__ import annotations

import csv
import hashlib
import json
import math
import random
from pathlib import Path
from typing import Any

import numpy as np

from .stage14_attention_readout import (
    DEFAULT_CONTEXT_LENGTHS,
    DEFAULT_EXAMPLES_PER_TASK_LENGTH,
    DEFAULT_SEEDS,
    TASK_NAMES,
    VALUE_VOCAB_SIZE,
    Stage14Example,
    make_stage14_examples,
    split_examples,
)
from .stage17_small_decoder_value_model import EMBED_DIM


STAGE18_SCHEMA_VERSION = "qrope_stage18_value_output_capacity_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage18_value_output_capacity"
MODE_NAMES = ("uniform_attention", "teacher_forced_attention")


def _softmax(values: np.ndarray) -> np.ndarray:
    shifted = values - np.max(values)
    exp_values = np.exp(shifted)
    return exp_values / np.sum(exp_values)


def _attention(row: Stage14Example, mode_name: str) -> np.ndarray:
    if mode_name == "uniform_attention":
        return np.ones(len(row.key_positions), dtype=float) / float(len(row.key_positions))
    if mode_name == "teacher_forced_attention":
        attention = np.zeros(len(row.key_positions), dtype=float)
        for position in row.target_positions:
            attention[row.key_positions.index(position)] = 1.0 / float(len(row.target_positions))
        return attention
    raise ValueError(f"unknown mode_name: {mode_name}")


def _target_distribution(row: Stage14Example) -> np.ndarray:
    target = np.zeros(VALUE_VOCAB_SIZE, dtype=float)
    for token_id in row.target_values:
        target[token_id] = 1.0 / float(len(row.target_values))
    return target


def _init_params(seed: int, embed_dim: int = EMBED_DIM) -> dict[str, np.ndarray]:
    digest = hashlib.sha256(f"stage18:{seed}".encode("utf-8")).hexdigest()
    rng = np.random.default_rng(int(digest[:16], 16) % (2**32))
    return {
        "value_embedding": rng.normal(0.0, 0.03, size=(VALUE_VOCAB_SIZE, embed_dim)),
        "output_w": rng.normal(0.0, 0.03, size=(embed_dim, VALUE_VOCAB_SIZE)),
        "output_b": np.zeros(VALUE_VOCAB_SIZE, dtype=float),
    }


def _forward(row: Stage14Example, mode_name: str, params: dict[str, np.ndarray]) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    attention = _attention(row, mode_name)
    value_ids = np.array(row.candidate_values, dtype=int)
    candidate_embeddings = params["value_embedding"][value_ids]
    context = attention @ candidate_embeddings
    logits = context @ params["output_w"] + params["output_b"]
    probabilities = _softmax(logits)
    return probabilities, {
        "attention": attention,
        "value_ids": value_ids,
        "candidate_embeddings": candidate_embeddings,
        "context": context,
    }


def _loss_and_gradient(rows: list[Stage14Example], mode_name: str, params: dict[str, np.ndarray], l2: float) -> tuple[float, dict[str, np.ndarray]]:
    grads = {key: np.zeros_like(value) for key, value in params.items()}
    total_loss = 0.0
    for row in rows:
        target = _target_distribution(row)
        probabilities, cache = _forward(row, mode_name, params)
        target_mass = max(float(np.sum(probabilities[target > 0.0])), 1e-12)
        total_loss += -math.log(target_mass)
        grad_logits = probabilities - target
        context = cache["context"]
        grads["output_w"] += np.outer(context, grad_logits)
        grads["output_b"] += grad_logits
        grad_context = grad_logits @ params["output_w"].T
        for candidate_index, token_id in enumerate(cache["value_ids"]):
            grads["value_embedding"][token_id] += cache["attention"][candidate_index] * grad_context
    scale = 1.0 / float(len(rows))
    total_loss *= scale
    for key in grads:
        grads[key] *= scale
        if key != "output_b":
            total_loss += 0.5 * l2 * float(np.sum(params[key] * params[key]))
            grads[key] += l2 * params[key]
    return float(total_loss), grads


def train_capacity_model(
    rows: list[Stage14Example],
    mode_name: str,
    *,
    seed: int = 1801,
    epochs: int = 220,
    learning_rate: float = 0.3,
    l2: float = 0.0001,
) -> dict[str, Any]:
    if not rows:
        raise ValueError("rows must be non-empty")
    params = _init_params(seed)
    history: list[dict[str, float]] = []
    for epoch in range(epochs):
        loss, grads = _loss_and_gradient(rows, mode_name, params, l2)
        for key in params:
            params[key] -= learning_rate * grads[key]
        if epoch in {0, epochs // 4, epochs // 2, epochs - 1}:
            history.append({"epoch": epoch + 1, "loss": round(loss, 6)})
    return {
        "mode": mode_name,
        "seed": seed,
        "epochs": epochs,
        "learning_rate": learning_rate,
        "l2": l2,
        "embed_dim": EMBED_DIM,
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
    means = []
    for _ in range(iterations):
        sample = [values[rng.randrange(len(values))] for _ in range(len(values))]
        means.append(float(sum(sample) / len(sample)))
    means.sort()
    return {"low": round(means[int(0.025 * (iterations - 1))], 6), "high": round(means[int(0.975 * (iterations - 1))], 6)}


def evaluate_capacity_model(rows: list[Stage14Example], mode_name: str, params: dict[str, np.ndarray]) -> dict[str, Any]:
    losses: list[float] = []
    top1_hits: list[float] = []
    reciprocal_ranks: list[float] = []
    target_masses: list[float] = []
    ranks: list[int] = []
    for row in rows:
        probabilities, _ = _forward(row, mode_name, params)
        target_mass = max(float(np.sum(probabilities[list(row.target_values)])), 1e-12)
        rank = _first_relevant_rank(probabilities, row.target_values)
        top_value = _ranked_indices(probabilities)[0]
        losses.append(-math.log(target_mass))
        top1_hits.append(1.0 if top_value in set(row.target_values) else 0.0)
        reciprocal_ranks.append(1.0 / float(rank))
        target_masses.append(target_mass)
        ranks.append(rank)
    mean_loss = float(np.mean(losses))
    return {
        "row_count": len(rows),
        "loss": round(mean_loss, 6),
        "perplexity": round(float(math.exp(mean_loss)), 6),
        "top1_accuracy": round(float(np.mean(top1_hits)), 6),
        "top1_ci_low": _bootstrap_ci(top1_hits, seed_text=f"{mode_name}:top1")["low"],
        "top1_ci_high": _bootstrap_ci(top1_hits, seed_text=f"{mode_name}:top1")["high"],
        "mrr": round(float(np.mean(reciprocal_ranks)), 6),
        "mrr_ci_low": _bootstrap_ci(reciprocal_ranks, seed_text=f"{mode_name}:mrr")["low"],
        "mrr_ci_high": _bootstrap_ci(reciprocal_ranks, seed_text=f"{mode_name}:mrr")["high"],
        "mean_target_value_probability": round(float(np.mean(target_masses)), 6),
        "target_value_probability_ci_low": _bootstrap_ci(target_masses, seed_text=f"{mode_name}:prob")["low"],
        "target_value_probability_ci_high": _bootstrap_ci(target_masses, seed_text=f"{mode_name}:prob")["high"],
        "mean_first_relevant_value_rank": round(float(np.mean(ranks)), 6),
    }


def run_stage18_benchmark(
    *,
    seeds: tuple[int, ...] = DEFAULT_SEEDS,
    context_lengths: tuple[int, ...] = DEFAULT_CONTEXT_LENGTHS,
    examples_per_task_length: int = DEFAULT_EXAMPLES_PER_TASK_LENGTH,
    epochs: int = 220,
) -> dict[str, Any]:
    rows = make_stage14_examples(seeds=seeds, context_lengths=context_lengths, examples_per_task_length=examples_per_task_length)
    splits = split_examples(rows)
    table: list[dict[str, Any]] = []
    training_records: list[dict[str, Any]] = []
    for mode_name in MODE_NAMES:
        training = train_capacity_model(splits["train"], mode_name, epochs=epochs)
        params = _params_from_record(training)
        training_records.append(training)
        for split_name in ("train", "validation", "test"):
            row = evaluate_capacity_model(splits[split_name], mode_name, params)
            row["mode"] = mode_name
            row["split"] = split_name
            table.append(row)
    return {
        "schema_version": STAGE18_SCHEMA_VERSION,
        "stage": "stage18_value_output_capacity",
        "dataset": "deterministic_value_output_capacity_probe_v1",
        "no_hardware_submission": True,
        "mode_names": list(MODE_NAMES),
        "seeds": list(seeds),
        "context_lengths": list(context_lengths),
        "examples_per_task_length": examples_per_task_length,
        "train_row_count": len(splits["train"]),
        "validation_row_count": len(splits["validation"]),
        "test_row_count": len(splits["test"]),
        "model": {
            "type": "teacher_forced_or_uniform_attention_value_output_capacity_probe",
            "embed_dim": EMBED_DIM,
            "value_vocab_size": VALUE_VOCAB_SIZE,
            "epochs": epochs,
            "trained_parameters": "value embeddings, output projection, output bias",
        },
        "claim_boundary": {
            "supported": [
                "A deterministic capacity probe for the Stage 17 learned value-output bottleneck.",
                "Evidence about whether the value embedding/output projection can fit when attention is teacher-forced to the target key.",
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
    }


def write_stage18_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "dataset": result["dataset"],
        "no_hardware_submission": result["no_hardware_submission"],
        "mode_names": result["mode_names"],
        "train_row_count": result["train_row_count"],
        "validation_row_count": result["validation_row_count"],
        "test_row_count": result["test_row_count"],
        "model": result["model"],
        "result_path": str((output_dir / "results.json").as_posix()),
        "summary_csv_path": str((output_dir / "summary.csv").as_posix()),
        "claim_boundary": result["claim_boundary"],
    }
    paths = {"manifest": str(output_dir / "manifest.json"), "results": str(output_dir / "results.json"), "summary_csv": str(output_dir / "summary.csv")}
    public_result = dict(result)
    public_result["training_records"] = [{key: value for key, value in record.items() if key != "params"} for record in result["training_records"]]
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(public_result, indent=2, sort_keys=True), encoding="utf-8")
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(result["table"][0].keys()))
        writer.writeheader()
        writer.writerows(result["table"])
    return paths


def print_stage18_table(result: dict[str, Any]) -> None:
    columns = ("mode", "split", "row_count", "top1_accuracy", "mrr", "mean_target_value_probability", "mean_first_relevant_value_rank")
    print(" | ".join(columns))
    print(" | ".join("---" for _ in columns))
    for row in result["table"]:
        print(" | ".join(str(row[column]) for column in columns))
