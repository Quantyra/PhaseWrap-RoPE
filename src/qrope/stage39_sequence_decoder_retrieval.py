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
from .stage34_small_decoder_value_bridge import METHOD_NAMES


STAGE39_SCHEMA_VERSION = "qrope_stage39_sequence_decoder_retrieval_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage39_sequence_decoder_retrieval"
DEFAULT_MODEL_SEEDS = (3907, 3911, 3917, 3923, 3929)
FEATURE_DIM = 14
HIDDEN_DIM = 16
VALUE_EMBED_DIM = 48
DEFAULT_EPOCHS = 60
DEFAULT_LEARNING_RATE = 0.028
DEFAULT_L2 = 0.00001


def _softmax(values: np.ndarray) -> np.ndarray:
    shifted = values - np.max(values)
    exp_values = np.exp(shifted)
    return exp_values / np.sum(exp_values)


def _rope_inverse_frequencies(dim: int = 32, base: float = 10000.0) -> np.ndarray:
    return np.array([base ** (-2.0 * index / dim) for index in range(dim // 2)], dtype=float)


def _phasewrap_score(reference_delta: int, candidate_delta: int, period_pair: tuple[int, int] = (8, 12)) -> float:
    margins = []
    for period in period_pair:
        residual = phase_residual(reference_delta, candidate_delta, period)
        margins.append(math.cos(residual) - math.cos(2.0 * math.pi / float(period)))
    return float(margins[0] * margins[1])


def sequence_tokens(row: Stage14Example) -> np.ndarray:
    blocked = set(row.candidate_values) | set(row.target_values) | {0}
    tokens = np.zeros(row.query_pos, dtype=int)
    for position in range(row.query_pos):
        token_id = 1 + ((row.seed * 41 + row.sequence_length * 17 + position * 29) % (VALUE_VOCAB_SIZE - 1))
        while token_id in blocked:
            token_id = 1 + (token_id % (VALUE_VOCAB_SIZE - 1))
        tokens[position] = token_id
    for position, token_id in zip(row.key_positions, row.candidate_values):
        tokens[position] = token_id
    return tokens


def sequence_decoder_features(row: Stage14Example, method_name: str) -> np.ndarray:
    positions = np.arange(row.query_pos, dtype=int)
    candidate_deltas = row.query_pos - positions.astype(float)
    tokens = sequence_tokens(row)
    is_key = np.zeros(row.query_pos, dtype=float)
    for position in row.key_positions:
        is_key[position] = 1.0
    is_query_value = np.isin(tokens, np.array(row.candidate_values, dtype=int)).astype(float)
    recency = -candidate_deltas / float(row.query_pos)
    diff = float(row.reference_delta) - candidate_deltas
    features = np.zeros((row.query_pos, FEATURE_DIM), dtype=float)
    features[:, 0] = 1.0
    features[:, 1] = is_key
    features[:, 2] = is_query_value
    features[:, 3] = tokens.astype(float) / float(VALUE_VOCAB_SIZE)
    features[:, 4] = recency

    if method_name == "no_position":
        return features
    if method_name == "alibi":
        features[:, 5] = recency
        features[:, 6] = is_key * recency
        features[:, 7] = is_query_value * recency
        return features
    if method_name == "rope_relative":
        inv_freq = _rope_inverse_frequencies()
        rope = np.cos(diff[:, None] * inv_freq[None, :])
        features[:, 5] = np.mean(rope, axis=1)
        features[:, 6] = np.max(rope, axis=1)
        features[:, 7] = np.min(rope, axis=1)
        features[:, 8] = is_key * features[:, 5]
        features[:, 9] = is_query_value * features[:, 5]
        features[:, 10] = is_key * features[:, 6]
        return features
    if method_name == "sinusoidal":
        periods = np.array((4.0, 8.0, 16.0, 32.0, 64.0), dtype=float)
        waves = np.cos(2.0 * math.pi * diff[:, None] / periods[None, :])
        features[:, 5] = np.mean(waves, axis=1)
        features[:, 6] = np.max(waves, axis=1)
        features[:, 7] = np.min(waves, axis=1)
        features[:, 8] = is_key * features[:, 5]
        features[:, 9] = is_query_value * features[:, 5]
        features[:, 10] = is_key * features[:, 6]
        return features

    phase = np.array([_phasewrap_score(row.reference_delta, int(delta)) for delta in candidate_deltas], dtype=float)
    residual8 = np.array([phase_residual(row.reference_delta, int(delta), 8) for delta in candidate_deltas], dtype=float)
    residual12 = np.array([phase_residual(row.reference_delta, int(delta), 12) for delta in candidate_deltas], dtype=float)
    cos8 = np.cos(residual8)
    cos12 = np.cos(residual12)
    features[:, 5] = phase
    features[:, 6] = cos8
    features[:, 7] = cos12
    features[:, 8] = cos8 * cos12
    features[:, 9] = -np.abs(diff) / float(row.query_pos)
    features[:, 10] = is_key * phase
    features[:, 11] = is_query_value * phase
    features[:, 12] = is_key * features[:, 9]
    if method_name == "phasewrap_distance_adapter":
        return features
    if method_name == "phasewrap_multiscale_adapter":
        alt_8_24 = np.array([_phasewrap_score(row.reference_delta, int(delta), (8, 24)) for delta in candidate_deltas], dtype=float)
        alt_9_15 = np.array([_phasewrap_score(row.reference_delta, int(delta), (9, 15)) for delta in candidate_deltas], dtype=float)
        features[:, 12] = alt_8_24
        features[:, 13] = alt_9_15
        return features
    raise ValueError(f"unknown method_name: {method_name}")


def _target_value_distribution(row: Stage14Example) -> np.ndarray:
    target = np.zeros(VALUE_VOCAB_SIZE, dtype=float)
    for token_id in row.target_values:
        target[token_id] = 1.0 / float(len(row.target_values))
    return target


def _init_params(*, method_name: str, model_seed: int, hidden_dim: int, value_embed_dim: int) -> dict[str, np.ndarray]:
    seed_text = f"stage39:{method_name}:{model_seed}:{FEATURE_DIM}:{hidden_dim}:{value_embed_dim}"
    seed = int(hashlib.sha256(seed_text.encode("utf-8")).hexdigest()[:16], 16) % (2**32)
    rng = np.random.default_rng(seed)
    return {
        "w1": rng.normal(0.0, 0.035, size=(FEATURE_DIM, hidden_dim)),
        "b1": np.zeros(hidden_dim, dtype=float),
        "w2": rng.normal(0.0, 0.035, size=hidden_dim),
        "b2": np.zeros(1, dtype=float),
        "value_embedding": rng.normal(0.0, 0.04, size=(VALUE_VOCAB_SIZE, value_embed_dim)),
        "output_w": rng.normal(0.0, 0.04, size=(value_embed_dim, VALUE_VOCAB_SIZE)),
        "output_b": np.zeros(VALUE_VOCAB_SIZE, dtype=float),
    }


def _parameter_count(hidden_dim: int = HIDDEN_DIM, value_embed_dim: int = VALUE_EMBED_DIM) -> int:
    return (
        FEATURE_DIM * hidden_dim
        + hidden_dim
        + hidden_dim
        + 1
        + VALUE_VOCAB_SIZE * value_embed_dim
        + value_embed_dim * VALUE_VOCAB_SIZE
        + VALUE_VOCAB_SIZE
    )


def _forward(row: Stage14Example, method_name: str, params: dict[str, np.ndarray]) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    features = sequence_decoder_features(row, method_name)
    hidden_pre = features @ params["w1"] + params["b1"]
    hidden = np.tanh(hidden_pre)
    attention_logits = hidden @ params["w2"] + float(params["b2"][0])
    attention = _softmax(attention_logits)
    token_ids = sequence_tokens(row)
    token_embeddings = params["value_embedding"][token_ids]
    context = attention @ token_embeddings
    value_logits = context @ params["output_w"] + params["output_b"]
    value_probabilities = _softmax(value_logits)
    return value_probabilities, {
        "features": features,
        "hidden": hidden,
        "attention": attention,
        "token_ids": token_ids,
        "token_embeddings": token_embeddings,
        "context": context,
    }


def _loss_and_gradient(rows: list[Stage14Example], method_name: str, params: dict[str, np.ndarray], l2: float) -> tuple[float, dict[str, np.ndarray]]:
    grads = {key: np.zeros_like(value) for key, value in params.items()}
    total_loss = 0.0
    for row in rows:
        probabilities, cache = _forward(row, method_name, params)
        target = _target_value_distribution(row)
        target_mass = max(float(np.sum(probabilities[target > 0.0])), 1e-12)
        total_loss += -math.log(target_mass)

        grad_value_logits = probabilities - target
        context = cache["context"]
        attention = cache["attention"]
        token_embeddings = cache["token_embeddings"]
        hidden = cache["hidden"]
        features = cache["features"]

        grads["output_w"] += np.outer(context, grad_value_logits)
        grads["output_b"] += grad_value_logits
        grad_context = grad_value_logits @ params["output_w"].T
        for token_index, token_id in enumerate(cache["token_ids"]):
            grads["value_embedding"][token_id] += attention[token_index] * grad_context

        grad_attention = token_embeddings @ grad_context
        grad_attention_logits = attention * (grad_attention - float(attention @ grad_attention))
        grads["w2"] += hidden.T @ grad_attention_logits
        grads["b2"] += np.array([float(np.sum(grad_attention_logits))])
        grad_hidden = grad_attention_logits[:, None] * params["w2"][None, :]
        grad_hidden_pre = grad_hidden * (1.0 - hidden * hidden)
        grads["w1"] += features.T @ grad_hidden_pre
        grads["b1"] += np.sum(grad_hidden_pre, axis=0)

    scale = 1.0 / float(len(rows))
    total_loss *= scale
    for key, value in params.items():
        grads[key] *= scale
        if key not in {"output_b", "b1", "b2"}:
            total_loss += 0.5 * l2 * float(np.sum(value * value))
            grads[key] += l2 * value
    return float(total_loss), grads


def train_sequence_decoder(
    rows: list[Stage14Example],
    method_name: str,
    *,
    model_seed: int,
    epochs: int = DEFAULT_EPOCHS,
    learning_rate: float = DEFAULT_LEARNING_RATE,
    l2: float = DEFAULT_L2,
    hidden_dim: int = HIDDEN_DIM,
    value_embed_dim: int = VALUE_EMBED_DIM,
) -> dict[str, Any]:
    params = _init_params(method_name=method_name, model_seed=model_seed, hidden_dim=hidden_dim, value_embed_dim=value_embed_dim)
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
            history.append({"epoch": epoch, "loss": round(float(loss), 6)})
    rounded_params = {key: np.round(value, 8).tolist() for key, value in params.items()}
    param_bytes = json.dumps(rounded_params, sort_keys=True).encode("utf-8")
    return {
        "method": method_name,
        "model_seed": model_seed,
        "feature_dim": FEATURE_DIM,
        "hidden_dim": hidden_dim,
        "value_embed_dim": value_embed_dim,
        "parameter_count": _parameter_count(hidden_dim, value_embed_dim),
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


def evaluate_sequence_decoder(rows: list[Stage14Example], method_name: str, params: dict[str, np.ndarray]) -> dict[str, Any]:
    losses: list[float] = []
    top1_hits: list[float] = []
    reciprocal_ranks: list[float] = []
    target_masses: list[float] = []
    top1_confidences: list[float] = []
    ranks: list[int] = []
    for row in rows:
        probabilities, _ = _forward(row, method_name, params)
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


def _aggregate_runs(run_rows: list[dict[str, Any]], *, method_name: str, hidden_dim: int, value_embed_dim: int) -> dict[str, Any]:
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
        "feature_dim": FEATURE_DIM,
        "hidden_dim": hidden_dim,
        "value_embed_dim": value_embed_dim,
        "parameter_count": _parameter_count(hidden_dim, value_embed_dim),
        "attention_scope": "full_prefix_sequence_tokens",
    }
    for metric_name in metric_names:
        values = [float(item[metric_name]) for item in run_rows]
        ci = _metric_ci(values, seed_text=f"stage39:{method_name}:{metric_name}")
        row[f"{metric_name}_mean"] = round(float(np.mean(values)), 6)
        row[f"{metric_name}_ci_low"] = ci["low"]
        row[f"{metric_name}_ci_high"] = ci["high"]
    return row


def run_stage39_benchmark(
    *,
    data_seeds: tuple[int, ...] = DATA_SEEDS,
    model_seeds: tuple[int, ...] = DEFAULT_MODEL_SEEDS,
    context_lengths: tuple[int, ...] = DEFAULT_CONTEXT_LENGTHS,
    examples_per_task_length: int = DEFAULT_EXAMPLES_PER_TASK_LENGTH,
    epochs: int = DEFAULT_EPOCHS,
    learning_rate: float = DEFAULT_LEARNING_RATE,
    l2: float = DEFAULT_L2,
    hidden_dim: int = HIDDEN_DIM,
    value_embed_dim: int = VALUE_EMBED_DIM,
    method_names: tuple[str, ...] = METHOD_NAMES,
) -> dict[str, Any]:
    rows = make_stage14_examples(seeds=data_seeds, context_lengths=context_lengths, examples_per_task_length=examples_per_task_length)
    splits = split_examples(rows)
    training_records: list[dict[str, Any]] = []
    train_table: list[dict[str, Any]] = []
    validation_table: list[dict[str, Any]] = []
    run_table: list[dict[str, Any]] = []
    task_table: list[dict[str, Any]] = []
    weak_runs: list[dict[str, Any]] = []
    for method_name in method_names:
        for model_seed in model_seeds:
            training = train_sequence_decoder(
                splits["train"],
                method_name,
                model_seed=model_seed,
                epochs=epochs,
                learning_rate=learning_rate,
                l2=l2,
                hidden_dim=hidden_dim,
                value_embed_dim=value_embed_dim,
            )
            training_records.append(training)
            params = _params_from_record(training)
            for split_name, target_table in (("train", train_table), ("validation", validation_table), ("test", run_table)):
                row = evaluate_sequence_decoder(splits[split_name], method_name, params)
                row["method"] = method_name
                row["model_seed"] = model_seed
                row["split"] = split_name
                target_table.append(row)
            test_row = run_table[-1]
            if float(test_row["top1_accuracy"]) < 0.5:
                weak_runs.append({"method": method_name, "model_seed": model_seed, "top1_accuracy": test_row["top1_accuracy"], "mrr": test_row["mrr"], "criterion": "test_top1_accuracy_below_0.5"})
            for task_name in TASK_NAMES:
                task_rows = [example for example in splits["test"] if example.task == task_name]
                task_result = evaluate_sequence_decoder(task_rows, method_name, params)
                task_result["method"] = method_name
                task_result["model_seed"] = model_seed
                task_result["task"] = task_name
                task_table.append(task_result)
    table = [
        _aggregate_runs([row for row in run_table if row["method"] == method_name], method_name=method_name, hidden_dim=hidden_dim, value_embed_dim=value_embed_dim)
        for method_name in method_names
    ]
    train_summary = [
        _aggregate_runs([row for row in train_table if row["method"] == method_name], method_name=method_name, hidden_dim=hidden_dim, value_embed_dim=value_embed_dim)
        for method_name in method_names
    ]
    validation_summary = [
        _aggregate_runs([row for row in validation_table if row["method"] == method_name], method_name=method_name, hidden_dim=hidden_dim, value_embed_dim=value_embed_dim)
        for method_name in method_names
    ]
    selection_table = sorted(table, key=lambda row: (row["top1_accuracy_mean"], row["mrr_mean"], row["mean_target_value_probability_mean"], row["method"]), reverse=True)
    return {
        "schema_version": STAGE39_SCHEMA_VERSION,
        "stage": "stage39_sequence_decoder_retrieval",
        "dataset": "stage14_full_prefix_sequence_decoder_retrieval_v1",
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
            "type": "single_query_sequence_decoder_full_prefix_value_prediction",
            "feature_dim": FEATURE_DIM,
            "hidden_dim": hidden_dim,
            "value_vocab_size": VALUE_VOCAB_SIZE,
            "value_embed_dim": value_embed_dim,
            "parameter_count": _parameter_count(hidden_dim, value_embed_dim),
            "epochs": epochs,
            "learning_rate": learning_rate,
            "l2": l2,
            "optimizer": "full_batch_adam",
            "attention_scope": "all prefix sequence tokens compete",
            "trained_parameters": "feature bridge attention, token/value embeddings, output projection, output bias",
        },
        "task": {
            "description": "Train-short/test-long sequence-style decoder retrieval with all prefix tokens competing for attention.",
            "target_construction": "Targets are explicit Stage 12 retrieval-rule value tokens, not PhaseWrap-selected labels.",
            "scope": "This is a compact sequence-level decoder diagnostic, not a production language-model benchmark.",
        },
        "claim_boundary": {
            "supported": [
                "A deterministic sequence-level decoder retrieval diagnostic on non-phase-cued Stage 14 rows.",
                "Evidence about whether positional variants survive all-prefix token competition with learned value output.",
                "Matched architecture, optimizer, parameter count, data splits, confidence intervals, and weak-run reporting across positional variants.",
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
        "train_table": train_table,
        "validation_table": validation_table,
        "run_table": run_table,
        "task_table": task_table,
        "train_summary": train_summary,
        "validation_summary": validation_summary,
        "table": table,
        "selection_table": selection_table,
        "weak_runs": weak_runs,
        "best_method_by_test_top1_mrr": selection_table[0]["method"],
    }


def write_stage39_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
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
        "train_summary_csv_path": str((output_dir / "train_summary.csv").as_posix()),
        "validation_summary_csv_path": str((output_dir / "validation_summary.csv").as_posix()),
        "per_run_csv_path": str((output_dir / "per_run_results.csv").as_posix()),
        "task_summary_csv_path": str((output_dir / "task_summary.csv").as_posix()),
        "weak_runs_path": str((output_dir / "weak_runs.json").as_posix()),
        "claim_boundary": result["claim_boundary"],
    }
    paths = {
        "manifest": str(output_dir / "manifest.json"),
        "results": str(output_dir / "results.json"),
        "summary_csv": str(output_dir / "summary.csv"),
        "train_summary_csv": str(output_dir / "train_summary.csv"),
        "validation_summary_csv": str(output_dir / "validation_summary.csv"),
        "per_run_csv": str(output_dir / "per_run_results.csv"),
        "task_summary_csv": str(output_dir / "task_summary.csv"),
        "weak_runs": str(output_dir / "weak_runs.json"),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "weak_runs.json").write_text(json.dumps(result["weak_runs"], indent=2, sort_keys=True), encoding="utf-8")
    for file_name, table_name in (
        ("summary.csv", "table"),
        ("train_summary.csv", "train_summary"),
        ("validation_summary.csv", "validation_summary"),
        ("per_run_results.csv", "run_table"),
        ("task_summary.csv", "task_table"),
    ):
        with (output_dir / file_name).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(result[table_name][0].keys()))
            writer.writeheader()
            writer.writerows(result[table_name])
    return paths


def print_stage39_table(result: dict[str, Any]) -> None:
    columns = ("method", "run_count", "parameter_count", "top1_accuracy_mean", "mrr_mean", "mean_target_value_probability_mean", "expected_calibration_error_mean")
    print(" | ".join(columns))
    print(" | ".join("---" for _ in columns))
    for row in result["selection_table"]:
        print(" | ".join(str(row[column]) for column in columns))
