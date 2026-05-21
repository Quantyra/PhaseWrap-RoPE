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
from .stage34_small_decoder_value_bridge import METHOD_NAMES, VALUE_EMBED_DIM


STAGE35_SCHEMA_VERSION = "qrope_stage35_value_bridge_bottleneck_diagnostic_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage35_value_bridge_bottleneck_diagnostic"
DEFAULT_MODEL_SEEDS = (3503, 3511, 3517, 3527, 3529)


def _softmax(values: np.ndarray) -> np.ndarray:
    shifted = values - np.max(values)
    exp_values = np.exp(shifted)
    return exp_values / np.sum(exp_values)


def _teacher_forced_attention(row: Stage14Example) -> np.ndarray:
    attention = np.zeros(len(row.key_positions), dtype=float)
    for position in row.target_positions:
        attention[row.key_positions.index(position)] = 1.0 / float(len(row.target_positions))
    return attention


def _target_value_distribution(row: Stage14Example) -> np.ndarray:
    target = np.zeros(VALUE_VOCAB_SIZE, dtype=float)
    for token_id in row.target_values:
        target[token_id] = 1.0 / float(len(row.target_values))
    return target


def _init_params(*, method_name: str, model_seed: int, value_embed_dim: int) -> dict[str, np.ndarray]:
    seed_text = f"stage35:{method_name}:{model_seed}:{value_embed_dim}"
    seed = int(hashlib.sha256(seed_text.encode("utf-8")).hexdigest()[:16], 16) % (2**32)
    rng = np.random.default_rng(seed)
    return {
        "value_embedding": rng.normal(0.0, 0.04, size=(VALUE_VOCAB_SIZE, value_embed_dim)),
        "output_w": rng.normal(0.0, 0.04, size=(value_embed_dim, VALUE_VOCAB_SIZE)),
        "output_b": np.zeros(VALUE_VOCAB_SIZE, dtype=float),
    }


def _forward(row: Stage14Example, params: dict[str, np.ndarray]) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    attention = _teacher_forced_attention(row)
    value_ids = np.array(row.candidate_values, dtype=int)
    candidate_embeddings = params["value_embedding"][value_ids]
    context = attention @ candidate_embeddings
    logits = context @ params["output_w"] + params["output_b"]
    probabilities = _softmax(logits)
    return probabilities, {
        "attention": attention,
        "value_ids": value_ids,
        "context": context,
    }


def _loss_and_gradient(rows: list[Stage14Example], params: dict[str, np.ndarray], l2: float) -> tuple[float, dict[str, np.ndarray]]:
    grads = {key: np.zeros_like(value) for key, value in params.items()}
    total_loss = 0.0
    for row in rows:
        target = _target_value_distribution(row)
        probabilities, cache = _forward(row, params)
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
    for key, value in params.items():
        grads[key] *= scale
        if key != "output_b":
            total_loss += 0.5 * l2 * float(np.sum(value * value))
            grads[key] += l2 * value
    return float(total_loss), grads


def _parameter_count(value_embed_dim: int = VALUE_EMBED_DIM) -> int:
    return VALUE_VOCAB_SIZE * value_embed_dim + value_embed_dim * VALUE_VOCAB_SIZE + VALUE_VOCAB_SIZE


def train_teacher_forced_value_bridge(
    rows: list[Stage14Example],
    method_name: str,
    *,
    model_seed: int,
    epochs: int = 160,
    learning_rate: float = 0.035,
    l2: float = 0.00001,
    value_embed_dim: int = VALUE_EMBED_DIM,
) -> dict[str, Any]:
    params = _init_params(method_name=method_name, model_seed=model_seed, value_embed_dim=value_embed_dim)
    moments = {key: np.zeros_like(value) for key, value in params.items()}
    velocities = {key: np.zeros_like(value) for key, value in params.items()}
    beta1 = 0.9
    beta2 = 0.999
    epsilon = 1e-8
    history: list[dict[str, float]] = []
    for epoch in range(1, epochs + 1):
        loss, grads = _loss_and_gradient(rows, params, l2)
        for key in params:
            moments[key] = beta1 * moments[key] + (1.0 - beta1) * grads[key]
            velocities[key] = beta2 * velocities[key] + (1.0 - beta2) * (grads[key] * grads[key])
            moment_hat = moments[key] / (1.0 - beta1**epoch)
            velocity_hat = velocities[key] / (1.0 - beta2**epoch)
            params[key] -= learning_rate * moment_hat / (np.sqrt(velocity_hat) + epsilon)
        if epoch in {1, epochs // 4, epochs // 2, (3 * epochs) // 4, epochs}:
            history.append({"epoch": epoch, "loss": round(float(loss), 6)})
    rounded_params = {key: np.round(value, 8).tolist() for key, value in params.items()}
    param_bytes = json.dumps(rounded_params, sort_keys=True).encode("utf-8")
    return {
        "method": method_name,
        "model_seed": model_seed,
        "attention_mode": "teacher_forced_target_positions",
        "value_embed_dim": value_embed_dim,
        "parameter_count": _parameter_count(value_embed_dim),
        "epochs": epochs,
        "learning_rate": learning_rate,
        "l2": l2,
        "optimizer": "full_batch_adam",
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


def evaluate_teacher_forced_value_bridge(rows: list[Stage14Example], params: dict[str, np.ndarray]) -> dict[str, Any]:
    losses: list[float] = []
    top1_hits: list[float] = []
    reciprocal_ranks: list[float] = []
    target_masses: list[float] = []
    top1_confidences: list[float] = []
    ranks: list[int] = []
    for row in rows:
        probabilities, _ = _forward(row, params)
        target_mass = max(float(np.sum(probabilities[list(row.target_values)])), 1e-12)
        rank = _first_relevant_rank(probabilities, row.target_values)
        top_value = _ranked_indices(probabilities)[0]
        top1_correct = 1.0 if top_value in set(row.target_values) else 0.0
        losses.append(-math.log(target_mass))
        top1_hits.append(top1_correct)
        reciprocal_ranks.append(1.0 / float(rank))
        target_masses.append(target_mass)
        top1_confidences.append(float(probabilities[top_value]))
        ranks.append(rank)
    mean_loss = float(np.mean(losses))
    return {
        "row_count": len(rows),
        "loss": round(mean_loss, 6),
        "perplexity": round(float(math.exp(mean_loss)), 6),
        "top1_accuracy": round(float(np.mean(top1_hits)), 6),
        "mrr": round(float(np.mean(reciprocal_ranks)), 6),
        "mean_target_value_probability": round(float(np.mean(target_masses)), 6),
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
        "target_value_probability_mae",
        "mean_top1_confidence",
        "expected_calibration_error",
        "mean_first_relevant_value_rank",
    )
    row: dict[str, Any] = {
        "method": method_name,
        "run_count": len(run_rows),
        "row_count": run_rows[0]["row_count"],
        "attention_mode": "teacher_forced_target_positions",
        "value_embed_dim": VALUE_EMBED_DIM,
        "parameter_count": _parameter_count(),
    }
    for metric_name in metric_names:
        values = [float(item[metric_name]) for item in run_rows]
        ci = _metric_ci(values, seed_text=f"stage35:{method_name}:{metric_name}")
        row[f"{metric_name}_mean"] = round(float(np.mean(values)), 6)
        row[f"{metric_name}_ci_low"] = ci["low"]
        row[f"{metric_name}_ci_high"] = ci["high"]
    return row


def _diagnosis(table: list[dict[str, Any]]) -> dict[str, Any]:
    top1_values = [float(row["top1_accuracy_mean"]) for row in table]
    probability_values = [float(row["mean_target_value_probability_mean"]) for row in table]
    mean_top1 = float(np.mean(top1_values))
    mean_probability = float(np.mean(probability_values))
    if mean_top1 >= 0.9 and mean_probability >= 0.8:
        verdict = "stage34_gap_is_primarily_attention_selection"
    elif mean_top1 >= 0.5:
        verdict = "value_output_partly_viable_attention_selection_still_primary"
    else:
        verdict = "value_output_capacity_or_generalization_remains_a_live_bottleneck"
    return {
        "verdict": verdict,
        "mean_top1_across_methods": round(mean_top1, 6),
        "mean_target_value_probability_across_methods": round(mean_probability, 6),
        "interpretation": "Teacher-forced target attention removes positional selection. Remaining errors measure value-output capacity/generalization rather than PhaseWrap attention ranking.",
    }


def run_stage35_benchmark(
    *,
    data_seeds: tuple[int, ...] = DATA_SEEDS,
    model_seeds: tuple[int, ...] = DEFAULT_MODEL_SEEDS,
    context_lengths: tuple[int, ...] = DEFAULT_CONTEXT_LENGTHS,
    examples_per_task_length: int = DEFAULT_EXAMPLES_PER_TASK_LENGTH,
    epochs: int = 160,
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
            training = train_teacher_forced_value_bridge(splits["train"], method_name, model_seed=model_seed, epochs=epochs)
            training_records.append(training)
            params = _params_from_record(training)
            row = evaluate_teacher_forced_value_bridge(splits["test"], params)
            row["method"] = method_name
            row["model_seed"] = model_seed
            run_table.append(row)
            if float(row["top1_accuracy"]) < 0.9:
                weak_runs.append(
                    {
                        "method": method_name,
                        "model_seed": model_seed,
                        "top1_accuracy": row["top1_accuracy"],
                        "mrr": row["mrr"],
                        "criterion": "teacher_forced_test_top1_accuracy_below_0.9",
                    }
                )
            for task_name in TASK_NAMES:
                task_rows = [example for example in splits["test"] if example.task == task_name]
                task_result = evaluate_teacher_forced_value_bridge(task_rows, params)
                task_result["method"] = method_name
                task_result["model_seed"] = model_seed
                task_result["task"] = task_name
                task_table.append(task_result)
    table = [_aggregate_runs([row for row in run_table if row["method"] == method_name], method_name=method_name) for method_name in method_names]
    selection_table = sorted(table, key=lambda row: (row["top1_accuracy_mean"], row["mrr_mean"], row["mean_target_value_probability_mean"], row["method"]), reverse=True)
    return {
        "schema_version": STAGE35_SCHEMA_VERSION,
        "stage": "stage35_value_bridge_bottleneck_diagnostic",
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
            "type": "teacher_forced_attention_value_output_diagnostic",
            "attention_mode": "teacher_forced_target_positions",
            "value_vocab_size": VALUE_VOCAB_SIZE,
            "value_embed_dim": VALUE_EMBED_DIM,
            "parameter_count": _parameter_count(),
            "epochs": epochs,
            "optimizer": "full_batch_adam",
            "trained_parameters": "value embeddings, output projection, output bias",
        },
        "task": {
            "description": "Teacher-forced value-output diagnostic on the Stage 34 key-value retrieval rows.",
            "target_construction": "Targets are explicit Stage 12 retrieval-rule value tokens, not PhaseWrap-selected labels.",
            "scope": "This removes positional attention selection and tests value-output capacity/generalization.",
        },
        "claim_boundary": {
            "supported": [
                "A deterministic diagnostic separating Stage 34 value-output behavior from learned positional attention selection.",
                "Evidence about whether the compact learned value-output path works when target attention is supplied.",
                "Matched data splits, optimizer, value-output dimensions, confidence intervals, and weak-run reporting.",
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
        "diagnosis": _diagnosis(table),
        "best_method_by_test_top1_mrr": selection_table[0]["method"],
    }


def write_stage35_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
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
        "diagnosis": result["diagnosis"],
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


def print_stage35_table(result: dict[str, Any]) -> None:
    columns = ("method", "run_count", "parameter_count", "top1_accuracy_mean", "mrr_mean", "mean_target_value_probability_mean", "expected_calibration_error_mean")
    print(" | ".join(columns))
    print(" | ".join("---" for _ in columns))
    for row in result["selection_table"]:
        print(" | ".join(str(row[column]) for column in columns))
    print(f"diagnosis: {result['diagnosis']['verdict']}")
