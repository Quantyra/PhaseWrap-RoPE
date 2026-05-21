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
    DEFAULT_SEEDS as DATA_SEEDS,
    TASK_NAMES,
    VALUE_VOCAB_SIZE,
    Stage14Example,
    make_stage14_examples,
    split_examples,
)
from .stage34_small_decoder_value_bridge import (
    FEATURE_DIM,
    HIDDEN_DIM,
    METHOD_NAMES,
    decoder_value_bridge_features,
)


STAGE36_SCHEMA_VERSION = "qrope_stage36_copy_value_bridge_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage36_copy_value_bridge"
DEFAULT_MODEL_SEEDS = (3607, 3613, 3617, 3623, 3631)


def _softmax(values: np.ndarray) -> np.ndarray:
    shifted = values - np.max(values)
    exp_values = np.exp(shifted)
    return exp_values / np.sum(exp_values)


def _target_attention_distribution(row: Stage14Example) -> np.ndarray:
    target = np.zeros(len(row.key_positions), dtype=float)
    for position in row.target_positions:
        target[row.key_positions.index(position)] = 1.0 / float(len(row.target_positions))
    return target


def _value_distribution(row: Stage14Example, attention: np.ndarray) -> np.ndarray:
    values = np.zeros(VALUE_VOCAB_SIZE, dtype=float)
    for probability, token_id in zip(attention, row.candidate_values):
        values[token_id] += float(probability)
    return values


def _init_params(*, method_name: str, model_seed: int, hidden_dim: int) -> dict[str, np.ndarray]:
    seed_text = f"stage36:{method_name}:{model_seed}:{FEATURE_DIM}:{hidden_dim}"
    seed = int(hashlib.sha256(seed_text.encode("utf-8")).hexdigest()[:16], 16) % (2**32)
    rng = np.random.default_rng(seed)
    return {
        "w1": rng.normal(0.0, 0.035, size=(FEATURE_DIM, hidden_dim)),
        "b1": np.zeros(hidden_dim, dtype=float),
        "w2": rng.normal(0.0, 0.035, size=hidden_dim),
        "b2": np.zeros(1, dtype=float),
    }


def _forward(row: Stage14Example, method_name: str, params: dict[str, np.ndarray]) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    features = decoder_value_bridge_features(row, method_name)
    hidden_pre = features @ params["w1"] + params["b1"]
    hidden = np.tanh(hidden_pre)
    logits = hidden @ params["w2"] + float(params["b2"][0])
    attention = _softmax(logits)
    return attention, {"features": features, "hidden": hidden}


def _loss_and_gradient(rows: list[Stage14Example], method_name: str, params: dict[str, np.ndarray], l2: float) -> tuple[float, dict[str, np.ndarray]]:
    grads = {key: np.zeros_like(value) for key, value in params.items()}
    total_loss = 0.0
    for row in rows:
        attention, cache = _forward(row, method_name, params)
        target = _target_attention_distribution(row)
        target_mass = max(float(np.sum(attention[target > 0.0])), 1e-12)
        total_loss += -math.log(target_mass)
        grad_logits = attention - target
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
    for key, value in params.items():
        grads[key] *= scale
        if key.startswith("w"):
            total_loss += 0.5 * l2 * float(np.sum(value * value))
            grads[key] += l2 * value
    return float(total_loss), grads


def _parameter_count(hidden_dim: int = HIDDEN_DIM) -> int:
    return FEATURE_DIM * hidden_dim + hidden_dim + hidden_dim + 1


def train_copy_value_bridge(
    rows: list[Stage14Example],
    method_name: str,
    *,
    model_seed: int,
    epochs: int = 80,
    learning_rate: float = 0.18,
    l2: float = 0.001,
    hidden_dim: int = HIDDEN_DIM,
) -> dict[str, Any]:
    params = _init_params(method_name=method_name, model_seed=model_seed, hidden_dim=hidden_dim)
    history: list[dict[str, float]] = []
    for epoch in range(1, epochs + 1):
        loss, grads = _loss_and_gradient(rows, method_name, params, l2)
        for key in params:
            params[key] -= learning_rate * grads[key]
        if epoch in {1, epochs // 4, epochs // 2, (3 * epochs) // 4, epochs}:
            history.append({"epoch": epoch, "loss": round(float(loss), 6)})
    rounded_params = {key: np.round(value, 8).tolist() for key, value in params.items()}
    param_bytes = json.dumps(rounded_params, sort_keys=True).encode("utf-8")
    return {
        "method": method_name,
        "model_seed": model_seed,
        "feature_dim": FEATURE_DIM,
        "hidden_dim": hidden_dim,
        "parameter_count": _parameter_count(hidden_dim),
        "epochs": epochs,
        "learning_rate": learning_rate,
        "l2": l2,
        "optimizer": "full_batch_gradient_descent",
        "value_output_mode": "copy_attention_mass_to_candidate_values",
        "params": rounded_params,
        "param_sha256": hashlib.sha256(param_bytes).hexdigest(),
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
    raise RuntimeError("target absent from value distribution")


def _expected_calibration_error(confidences: list[float], correctness: list[float], *, bins: int = 10) -> float:
    total = float(len(confidences))
    ece = 0.0
    for bin_index in range(bins):
        low = bin_index / float(bins)
        high = (bin_index + 1) / float(bins)
        if bin_index == bins - 1:
            indices = [index for index, value in enumerate(confidences) if low <= value <= high]
        else:
            indices = [index for index, value in enumerate(confidences) if low <= value < high]
        if not indices:
            continue
        avg_confidence = float(np.mean([confidences[index] for index in indices]))
        avg_accuracy = float(np.mean([correctness[index] for index in indices]))
        ece += (len(indices) / total) * abs(avg_confidence - avg_accuracy)
    return float(ece)


def evaluate_copy_value_bridge(rows: list[Stage14Example], method_name: str, params: dict[str, np.ndarray]) -> dict[str, Any]:
    losses: list[float] = []
    top1_hits: list[float] = []
    reciprocal_ranks: list[float] = []
    target_masses: list[float] = []
    top1_confidences: list[float] = []
    ranks: list[int] = []
    attention_target_masses: list[float] = []
    for row in rows:
        attention, _ = _forward(row, method_name, params)
        values = _value_distribution(row, attention)
        target_mass = max(float(np.sum(values[list(row.target_values)])), 1e-12)
        target_attention = _target_attention_distribution(row)
        attention_target_masses.append(float(np.sum(attention[target_attention > 0.0])))
        rank = _first_relevant_rank(values, row.target_values)
        top_value = _ranked_indices(values)[0]
        top1_correct = 1.0 if top_value in set(row.target_values) else 0.0
        losses.append(-math.log(target_mass))
        top1_hits.append(top1_correct)
        reciprocal_ranks.append(1.0 / float(rank))
        target_masses.append(target_mass)
        top1_confidences.append(float(values[top_value]))
        ranks.append(rank)
    mean_loss = float(np.mean(losses))
    return {
        "row_count": len(rows),
        "loss": round(mean_loss, 6),
        "perplexity": round(float(math.exp(mean_loss)), 6),
        "top1_accuracy": round(float(np.mean(top1_hits)), 6),
        "mrr": round(float(np.mean(reciprocal_ranks)), 6),
        "mean_target_value_probability": round(float(np.mean(target_masses)), 6),
        "mean_target_attention_probability": round(float(np.mean(attention_target_masses)), 6),
        "target_value_probability_mae": round(float(np.mean([1.0 - value for value in target_masses])), 6),
        "mean_top1_confidence": round(float(np.mean(top1_confidences)), 6),
        "expected_calibration_error": round(_expected_calibration_error(top1_confidences, top1_hits), 6),
        "mean_first_relevant_value_rank": round(float(np.mean(ranks)), 6),
    }


def _metric_ci(values: list[float], *, seed_text: str, iterations: int = 600) -> dict[str, float]:
    rng = random.Random(int(hashlib.sha256(seed_text.encode("utf-8")).hexdigest()[:16], 16))
    means: list[float] = []
    for _ in range(iterations):
        sample = [values[rng.randrange(len(values))] for _ in range(len(values))]
        means.append(float(sum(sample) / len(sample)))
    means.sort()
    return {"low": round(means[int(0.025 * (iterations - 1))], 6), "high": round(means[int(0.975 * (iterations - 1))], 6)}


def _aggregate_runs(run_rows: list[dict[str, Any]], *, method_name: str) -> dict[str, Any]:
    metric_names = (
        "loss",
        "top1_accuracy",
        "mrr",
        "mean_target_value_probability",
        "mean_target_attention_probability",
        "target_value_probability_mae",
        "mean_top1_confidence",
        "expected_calibration_error",
        "mean_first_relevant_value_rank",
    )
    row: dict[str, Any] = {
        "method": method_name,
        "run_count": len(run_rows),
        "row_count": run_rows[0]["row_count"],
        "feature_dim": FEATURE_DIM,
        "hidden_dim": HIDDEN_DIM,
        "parameter_count": _parameter_count(),
        "value_output_mode": "copy_attention_mass_to_candidate_values",
    }
    for metric_name in metric_names:
        values = [float(item[metric_name]) for item in run_rows]
        ci = _metric_ci(values, seed_text=f"stage36:{method_name}:{metric_name}")
        row[f"{metric_name}_mean"] = round(float(np.mean(values)), 6)
        row[f"{metric_name}_ci_low"] = ci["low"]
        row[f"{metric_name}_ci_high"] = ci["high"]
    return row


def run_stage36_benchmark(
    *,
    data_seeds: tuple[int, ...] = DATA_SEEDS,
    model_seeds: tuple[int, ...] = DEFAULT_MODEL_SEEDS,
    context_lengths: tuple[int, ...] = DEFAULT_CONTEXT_LENGTHS,
    examples_per_task_length: int = DEFAULT_EXAMPLES_PER_TASK_LENGTH,
    epochs: int = 80,
    method_names: tuple[str, ...] = METHOD_NAMES,
) -> dict[str, Any]:
    rows = make_stage14_examples(seeds=data_seeds, context_lengths=context_lengths, examples_per_task_length=examples_per_task_length)
    splits = split_examples(rows)
    training_records: list[dict[str, Any]] = []
    run_table: list[dict[str, Any]] = []
    task_table: list[dict[str, Any]] = []
    weak_runs: list[dict[str, Any]] = []
    for method_name in method_names:
        for model_seed in model_seeds:
            training = train_copy_value_bridge(splits["train"], method_name, model_seed=model_seed, epochs=epochs)
            training_records.append(training)
            params = _params_from_record(training)
            row = evaluate_copy_value_bridge(splits["test"], method_name, params)
            row["method"] = method_name
            row["model_seed"] = model_seed
            run_table.append(row)
            if float(row["top1_accuracy"]) < 0.5:
                weak_runs.append({"method": method_name, "model_seed": model_seed, "top1_accuracy": row["top1_accuracy"], "mrr": row["mrr"], "criterion": "test_top1_accuracy_below_0.5"})
            for task_name in TASK_NAMES:
                task_rows = [example for example in splits["test"] if example.task == task_name]
                task_result = evaluate_copy_value_bridge(task_rows, method_name, params)
                task_result["method"] = method_name
                task_result["model_seed"] = model_seed
                task_result["task"] = task_name
                task_table.append(task_result)
    table = [_aggregate_runs([row for row in run_table if row["method"] == method_name], method_name=method_name) for method_name in method_names]
    selection_table = sorted(table, key=lambda row: (row["top1_accuracy_mean"], row["mrr_mean"], row["mean_target_value_probability_mean"], row["method"]), reverse=True)
    return {
        "schema_version": STAGE36_SCHEMA_VERSION,
        "stage": "stage36_copy_value_bridge",
        "dataset": "stage14_non_phase_cued_key_value_retrieval_v1",
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "data_seeds": list(data_seeds),
        "model_seeds": list(model_seeds),
        "context_lengths": list(context_lengths),
        "train_lengths": [128, 256],
        "validation_lengths": [512],
        "test_lengths": [1024],
        "examples_per_task_length": examples_per_task_length,
        "task_names": list(TASK_NAMES),
        "method_names": list(method_names),
        "train_row_count": len(splits["train"]),
        "validation_row_count": len(splits["validation"]),
        "test_row_count": len(splits["test"]),
        "model": {
            "type": "nonlinear_attention_copy_value_bridge",
            "feature_dim": FEATURE_DIM,
            "hidden_dim": HIDDEN_DIM,
            "parameter_count": _parameter_count(),
            "epochs": epochs,
            "optimizer": "full_batch_gradient_descent",
            "trained_parameters": "feature bridge attention only",
            "value_output_mode": "copy attention mass to candidate value tokens",
        },
        "task": {
            "description": "Train-short/test-long key-value retrieval with copy-style value output.",
            "target_construction": "Targets are explicit Stage 12 retrieval-rule value tokens, not PhaseWrap-selected labels.",
            "scope": "This hardens value-output coupling to isolate learned attention selection more cleanly than Stage 34.",
        },
        "claim_boundary": {
            "supported": [
                "A deterministic copy-value bridge that removes the fragile learned value-token classifier from Stage 34.",
                "Evidence about learned attention selection when value output copies candidate values directly.",
                "Matched data splits, feature width, hidden width, model seeds, confidence intervals, and weak-run reporting.",
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
        "run_table": run_table,
        "task_table": task_table,
        "table": table,
        "selection_table": selection_table,
        "weak_runs": weak_runs,
        "best_method_by_test_top1_mrr": selection_table[0]["method"],
    }


def write_stage36_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "dataset": result["dataset"],
        "no_hardware_submission": result["no_hardware_submission"],
        "provider_credentials_required": result["provider_credentials_required"],
        "data_seeds": result["data_seeds"],
        "model_seeds": result["model_seeds"],
        "train_lengths": result["train_lengths"],
        "validation_lengths": result["validation_lengths"],
        "test_lengths": result["test_lengths"],
        "train_row_count": result["train_row_count"],
        "validation_row_count": result["validation_row_count"],
        "test_row_count": result["test_row_count"],
        "task_names": result["task_names"],
        "method_names": result["method_names"],
        "model": result["model"],
        "task": result["task"],
        "result_path": str((output_dir / "results.json").as_posix()),
        "summary_csv_path": str((output_dir / "summary.csv").as_posix()),
        "per_run_csv_path": str((output_dir / "per_run_results.csv").as_posix()),
        "task_summary_csv_path": str((output_dir / "task_summary.csv").as_posix()),
        "weak_runs_path": str((output_dir / "weak_runs.json").as_posix()),
        "claim_boundary": result["claim_boundary"],
    }
    paths = {
        "manifest": str(output_dir / "manifest.json"),
        "results": str(output_dir / "results.json"),
        "summary_csv": str(output_dir / "summary.csv"),
        "per_run_csv": str(output_dir / "per_run_results.csv"),
        "task_summary_csv": str(output_dir / "task_summary.csv"),
        "weak_runs": str(output_dir / "weak_runs.json"),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "weak_runs.json").write_text(json.dumps(result["weak_runs"], indent=2, sort_keys=True), encoding="utf-8")
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(result["table"][0].keys()))
        writer.writeheader()
        writer.writerows(result["table"])
    with (output_dir / "per_run_results.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(result["run_table"][0].keys()))
        writer.writeheader()
        writer.writerows(result["run_table"])
    with (output_dir / "task_summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(result["task_table"][0].keys()))
        writer.writeheader()
        writer.writerows(result["task_table"])
    return paths


def print_stage36_table(result: dict[str, Any]) -> None:
    columns = ("method", "run_count", "parameter_count", "top1_accuracy_mean", "mrr_mean", "mean_target_value_probability_mean", "mean_target_attention_probability_mean")
    print(" | ".join(columns))
    print(" | ".join("---" for _ in columns))
    for row in result["selection_table"]:
        print(" | ".join(str(row[column]) for column in columns))
