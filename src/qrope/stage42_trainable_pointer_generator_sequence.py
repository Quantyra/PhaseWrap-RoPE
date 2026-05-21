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
    DEFAULT_EXAMPLES_PER_TASK_LENGTH,
    DEFAULT_SEEDS as DATA_SEEDS,
    TASK_NAMES,
    VALUE_VOCAB_SIZE,
    make_stage14_examples,
)
from .stage34_small_decoder_value_bridge import METHOD_NAMES
from .stage39_sequence_decoder_retrieval import FEATURE_DIM, HIDDEN_DIM
from .stage40_sequence_length_curriculum import (
    DEFAULT_CONTEXT_LENGTHS,
    TEST_LENGTHS,
    TRAIN_LENGTHS,
    VALIDATION_LENGTHS,
    PreparedSequenceRow,
    prepare_sequence_rows,
    split_by_curriculum_lengths,
)


STAGE42_SCHEMA_VERSION = "qrope_stage42_trainable_pointer_generator_sequence_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage42_trainable_pointer_generator_sequence"
DEFAULT_MODEL_SEEDS = (4201, 4211, 4217, 4219, 4229)
DEFAULT_EPOCHS = 40
DEFAULT_LEARNING_RATE = 0.06
DEFAULT_L2 = 0.00005
DEFAULT_VALUE_EMBED_DIM = 8
DEFAULT_INITIAL_COPY_GATE_LOGIT = 1.5


def _softmax(values: np.ndarray) -> np.ndarray:
    shifted = values - np.max(values)
    exp_values = np.exp(shifted)
    return exp_values / np.sum(exp_values)


def _sigmoid(value: float) -> float:
    if value >= 0.0:
        z = math.exp(-value)
        return 1.0 / (1.0 + z)
    z = math.exp(value)
    return z / (1.0 + z)


def _init_params(*, method_name: str, model_seed: int, hidden_dim: int, value_embed_dim: int) -> dict[str, np.ndarray]:
    seed_text = f"stage42:{method_name}:{model_seed}:{FEATURE_DIM}:{hidden_dim}:{value_embed_dim}"
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
        "gate_w": np.zeros(value_embed_dim, dtype=float),
        "gate_b": np.array([DEFAULT_INITIAL_COPY_GATE_LOGIT], dtype=float),
    }


def _parameter_count(hidden_dim: int = HIDDEN_DIM, value_embed_dim: int = DEFAULT_VALUE_EMBED_DIM) -> int:
    return (
        FEATURE_DIM * hidden_dim
        + hidden_dim
        + hidden_dim
        + 1
        + VALUE_VOCAB_SIZE * value_embed_dim
        + value_embed_dim * VALUE_VOCAB_SIZE
        + VALUE_VOCAB_SIZE
        + value_embed_dim
        + 1
    )


def _copy_distribution(token_ids: np.ndarray, attention: np.ndarray) -> np.ndarray:
    values = np.zeros(VALUE_VOCAB_SIZE, dtype=float)
    np.add.at(values, token_ids, attention)
    return values


def _forward(prepared: PreparedSequenceRow, params: dict[str, np.ndarray]) -> tuple[np.ndarray, dict[str, np.ndarray | float]]:
    hidden_pre = prepared.features @ params["w1"] + params["b1"]
    hidden = np.tanh(hidden_pre)
    attention_logits = hidden @ params["w2"] + float(params["b2"][0])
    attention = _softmax(attention_logits)

    copy_probabilities = _copy_distribution(prepared.token_ids, attention)
    token_embeddings = params["value_embedding"][prepared.token_ids]
    context = attention @ token_embeddings
    generator_logits = context @ params["output_w"] + params["output_b"]
    generator_probabilities = _softmax(generator_logits)

    copy_gate = _sigmoid(float(context @ params["gate_w"] + params["gate_b"][0]))
    probabilities = copy_gate * copy_probabilities + (1.0 - copy_gate) * generator_probabilities
    return probabilities, {
        "hidden": hidden,
        "attention": attention,
        "copy_probabilities": copy_probabilities,
        "token_embeddings": token_embeddings,
        "context": context,
        "generator_probabilities": generator_probabilities,
        "copy_gate": copy_gate,
    }


def _loss_and_gradient(rows: list[PreparedSequenceRow], params: dict[str, np.ndarray], l2: float) -> tuple[float, dict[str, np.ndarray]]:
    grads = {key: np.zeros_like(value) for key, value in params.items()}
    total_loss = 0.0
    for prepared in rows:
        probabilities, cache = _forward(prepared, params)
        target_mask = prepared.target_distribution > 0.0
        target_mass = max(float(np.sum(probabilities[target_mask])), 1e-12)
        total_loss += -math.log(target_mass)

        grad_probabilities = np.zeros(VALUE_VOCAB_SIZE, dtype=float)
        grad_probabilities[target_mask] = -1.0 / target_mass

        copy_probabilities = cache["copy_probabilities"]
        generator_probabilities = cache["generator_probabilities"]
        copy_gate = float(cache["copy_gate"])
        context = cache["context"]
        attention = cache["attention"]
        token_embeddings = cache["token_embeddings"]
        hidden = cache["hidden"]

        grad_copy_probabilities = copy_gate * grad_probabilities
        grad_generator_probabilities = (1.0 - copy_gate) * grad_probabilities
        grad_copy_gate = float(grad_probabilities @ (copy_probabilities - generator_probabilities))

        grad_generator_logits = generator_probabilities * (
            grad_generator_probabilities - float(generator_probabilities @ grad_generator_probabilities)
        )
        grads["output_w"] += np.outer(context, grad_generator_logits)
        grads["output_b"] += grad_generator_logits
        grad_context = grad_generator_logits @ params["output_w"].T

        grad_gate_logit = grad_copy_gate * copy_gate * (1.0 - copy_gate)
        grads["gate_w"] += context * grad_gate_logit
        grads["gate_b"] += np.array([grad_gate_logit])
        grad_context += params["gate_w"] * grad_gate_logit

        np.add.at(grads["value_embedding"], prepared.token_ids, attention[:, None] * grad_context[None, :])

        grad_attention = token_embeddings @ grad_context
        grad_attention += grad_copy_probabilities[prepared.token_ids]
        grad_attention_logits = attention * (grad_attention - float(attention @ grad_attention))

        grads["w2"] += hidden.T @ grad_attention_logits
        grads["b2"] += np.array([float(np.sum(grad_attention_logits))])
        grad_hidden = grad_attention_logits[:, None] * params["w2"][None, :]
        grad_hidden_pre = grad_hidden * (1.0 - hidden * hidden)
        grads["w1"] += prepared.features.T @ grad_hidden_pre
        grads["b1"] += np.sum(grad_hidden_pre, axis=0)

    scale = 1.0 / float(len(rows))
    total_loss *= scale
    for key, value in params.items():
        grads[key] *= scale
        if key not in {"output_b", "b1", "b2", "gate_b"}:
            total_loss += 0.5 * l2 * float(np.sum(value * value))
            grads[key] += l2 * value
    return float(total_loss), grads


def train_pointer_generator_sequence(
    rows: list[PreparedSequenceRow],
    method_name: str,
    *,
    model_seed: int,
    epochs: int = DEFAULT_EPOCHS,
    learning_rate: float = DEFAULT_LEARNING_RATE,
    l2: float = DEFAULT_L2,
    hidden_dim: int = HIDDEN_DIM,
    value_embed_dim: int = DEFAULT_VALUE_EMBED_DIM,
) -> dict[str, Any]:
    params = _init_params(method_name=method_name, model_seed=model_seed, hidden_dim=hidden_dim, value_embed_dim=value_embed_dim)
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
        "feature_dim": FEATURE_DIM,
        "hidden_dim": hidden_dim,
        "value_embed_dim": value_embed_dim,
        "parameter_count": _parameter_count(hidden_dim, value_embed_dim),
        "epochs": epochs,
        "learning_rate": learning_rate,
        "l2": l2,
        "optimizer": "full_batch_adam",
        "value_output_mode": "trainable_pointer_generator_copy_vocab_mixture",
        "initial_copy_gate_logit": DEFAULT_INITIAL_COPY_GATE_LOGIT,
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


def evaluate_pointer_generator_sequence(rows: list[PreparedSequenceRow], params: dict[str, np.ndarray]) -> dict[str, Any]:
    losses: list[float] = []
    top1_hits: list[float] = []
    reciprocal_ranks: list[float] = []
    target_masses: list[float] = []
    copy_target_masses: list[float] = []
    generator_target_masses: list[float] = []
    copy_gates: list[float] = []
    top1_confidences: list[float] = []
    ranks: list[int] = []
    for prepared in rows:
        probabilities, cache = _forward(prepared, params)
        target_values = prepared.row.target_values
        target_mass = max(float(np.sum(probabilities[list(target_values)])), 1e-12)
        rank = _first_relevant_rank(probabilities, target_values)
        top_value = _ranked_indices(probabilities)[0]
        top1_correct = 1.0 if top_value in set(target_values) else 0.0

        losses.append(-math.log(target_mass))
        top1_hits.append(top1_correct)
        reciprocal_ranks.append(1.0 / float(rank))
        target_masses.append(target_mass)
        copy_target_masses.append(float(np.sum(cache["copy_probabilities"][list(target_values)])))
        generator_target_masses.append(float(np.sum(cache["generator_probabilities"][list(target_values)])))
        copy_gates.append(float(cache["copy_gate"]))
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
        "mean_target_attention_probability": round(float(np.mean(copy_target_masses)), 6),
        "mean_generator_target_probability": round(float(np.mean(generator_target_masses)), 6),
        "mean_copy_gate": round(float(np.mean(copy_gates)), 6),
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
        "mean_target_attention_probability",
        "mean_generator_target_probability",
        "mean_copy_gate",
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
        "value_output_mode": "trainable_pointer_generator_copy_vocab_mixture",
        "curriculum": "train_128_256_512_validate_1024_test_2048",
    }
    for metric_name in metric_names:
        values = [float(item[metric_name]) for item in run_rows]
        ci = _metric_ci(values, seed_text=f"stage42:{method_name}:{metric_name}")
        row[f"{metric_name}_mean"] = round(float(np.mean(values)), 6)
        row[f"{metric_name}_ci_low"] = ci["low"]
        row[f"{metric_name}_ci_high"] = ci["high"]
    return row


def run_stage42_benchmark(
    *,
    data_seeds: tuple[int, ...] = DATA_SEEDS,
    model_seeds: tuple[int, ...] = DEFAULT_MODEL_SEEDS,
    context_lengths: tuple[int, ...] = DEFAULT_CONTEXT_LENGTHS,
    examples_per_task_length: int = DEFAULT_EXAMPLES_PER_TASK_LENGTH,
    epochs: int = DEFAULT_EPOCHS,
    learning_rate: float = DEFAULT_LEARNING_RATE,
    l2: float = DEFAULT_L2,
    hidden_dim: int = HIDDEN_DIM,
    value_embed_dim: int = DEFAULT_VALUE_EMBED_DIM,
    method_names: tuple[str, ...] = METHOD_NAMES,
) -> dict[str, Any]:
    rows = make_stage14_examples(seeds=data_seeds, context_lengths=context_lengths, examples_per_task_length=examples_per_task_length)
    raw_splits = split_by_curriculum_lengths(rows)
    training_records: list[dict[str, Any]] = []
    train_table: list[dict[str, Any]] = []
    validation_table: list[dict[str, Any]] = []
    run_table: list[dict[str, Any]] = []
    task_table: list[dict[str, Any]] = []
    weak_runs: list[dict[str, Any]] = []
    for method_name in method_names:
        prepared_splits = {split_name: prepare_sequence_rows(split_rows, method_name) for split_name, split_rows in raw_splits.items()}
        for model_seed in model_seeds:
            training = train_pointer_generator_sequence(
                prepared_splits["train"],
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
                row = evaluate_pointer_generator_sequence(prepared_splits[split_name], params)
                row["method"] = method_name
                row["model_seed"] = model_seed
                row["split"] = split_name
                target_table.append(row)
            test_row = run_table[-1]
            if float(test_row["top1_accuracy"]) < 0.5:
                weak_runs.append({"method": method_name, "model_seed": model_seed, "top1_accuracy": test_row["top1_accuracy"], "mrr": test_row["mrr"], "criterion": "test_top1_accuracy_below_0.5"})
            for task_name in TASK_NAMES:
                task_rows = [prepared for prepared in prepared_splits["test"] if prepared.row.task == task_name]
                task_result = evaluate_pointer_generator_sequence(task_rows, params)
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
        "schema_version": STAGE42_SCHEMA_VERSION,
        "stage": "stage42_trainable_pointer_generator_sequence",
        "dataset": "stage14_full_prefix_trainable_pointer_generator_sequence_v1",
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "data_seeds": list(data_seeds),
        "model_seeds": list(model_seeds),
        "context_lengths": list(context_lengths),
        "train_lengths": list(TRAIN_LENGTHS),
        "validation_lengths": list(VALIDATION_LENGTHS),
        "test_lengths": list(TEST_LENGTHS),
        "examples_per_task_length": examples_per_task_length,
        "task_names": list(TASK_NAMES),
        "method_names": list(method_names),
        "train_row_count": len(raw_splits["train"]),
        "validation_row_count": len(raw_splits["validation"]),
        "test_row_count": len(raw_splits["test"]),
        "model": {
            "type": "single_query_sequence_decoder_trainable_pointer_generator",
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
            "curriculum": "train 128/256/512, validate 1024, test 2048",
            "trained_parameters": "feature bridge attention, token/value embeddings, output projection, output bias, copy/generator gate",
            "value_output_mode": "trainable pointer-generator mixture of copied prefix-token mass and learned vocab distribution",
            "initial_copy_gate_logit": DEFAULT_INITIAL_COPY_GATE_LOGIT,
        },
        "task": {
            "description": "Trainable pointer-generator follow-up to the Stage 41 deterministic pointer/copy sequence diagnostic.",
            "target_construction": "Targets are explicit Stage 12 retrieval-rule value tokens, not PhaseWrap-selected labels.",
            "scope": "This tests whether a learned copy/vocab mixture preserves the Stage 41 sequence-length repair.",
        },
        "claim_boundary": {
            "supported": [
                "A deterministic trainable pointer-generator diagnostic for the all-prefix compact sequence decoder.",
                "Evidence about whether learned copy/vocab mixing preserves the Stage 41 sequence-length repair.",
                "Matched feature bridge, optimizer, data splits, confidence intervals, and weak-run reporting across positional variants.",
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


def write_stage42_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
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


def print_stage42_table(result: dict[str, Any]) -> None:
    columns = (
        "method",
        "run_count",
        "parameter_count",
        "top1_accuracy_mean",
        "mrr_mean",
        "mean_target_value_probability_mean",
        "mean_copy_gate_mean",
        "expected_calibration_error_mean",
    )
    print(" | ".join(columns))
    print(" | ".join("---" for _ in columns))
    for row in result["selection_table"]:
        print(" | ".join(str(row[column]) for column in columns))
