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
from .stage42_trainable_pointer_generator_sequence import (
    DEFAULT_INITIAL_COPY_GATE_LOGIT,
    DEFAULT_VALUE_EMBED_DIM,
    _expected_calibration_error,
    _first_relevant_rank,
    _forward,
    _init_params,
    _parameter_count,
    _params_from_record,
    _ranked_indices,
    evaluate_pointer_generator_sequence,
)


STAGE43_SCHEMA_VERSION = "qrope_stage43_generator_hardened_pointer_sequence_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage43_generator_hardened_pointer_sequence"
DEFAULT_MODEL_SEEDS = (4307, 4319, 4327, 4337, 4349)
DEFAULT_EPOCHS = 55
DEFAULT_LEARNING_RATE = 0.05
DEFAULT_L2 = 0.00005
DEFAULT_GENERATOR_LOSS_WEIGHT = 0.35


def _generator_target_loss_and_grad(
    prepared: PreparedSequenceRow,
    generator_probabilities: np.ndarray,
) -> tuple[float, np.ndarray]:
    target_mask = prepared.target_distribution > 0.0
    target_mass = max(float(np.sum(generator_probabilities[target_mask])), 1e-12)
    grad = np.zeros(VALUE_VOCAB_SIZE, dtype=float)
    grad[target_mask] = -1.0 / target_mass
    return -math.log(target_mass), grad


def _loss_and_gradient(
    rows: list[PreparedSequenceRow],
    params: dict[str, np.ndarray],
    l2: float,
    generator_loss_weight: float,
) -> tuple[float, dict[str, np.ndarray]]:
    grads = {key: np.zeros_like(value) for key, value in params.items()}
    total_loss = 0.0
    for prepared in rows:
        probabilities, cache = _forward(prepared, params)
        target_mask = prepared.target_distribution > 0.0
        target_mass = max(float(np.sum(probabilities[target_mask])), 1e-12)
        mixture_loss = -math.log(target_mass)

        grad_probabilities = np.zeros(VALUE_VOCAB_SIZE, dtype=float)
        grad_probabilities[target_mask] = -1.0 / target_mass

        copy_probabilities = cache["copy_probabilities"]
        generator_probabilities = cache["generator_probabilities"]
        copy_gate = float(cache["copy_gate"])
        context = cache["context"]
        attention = cache["attention"]
        token_embeddings = cache["token_embeddings"]
        hidden = cache["hidden"]

        generator_loss, grad_generator_target_probabilities = _generator_target_loss_and_grad(prepared, generator_probabilities)
        total_loss += mixture_loss + generator_loss_weight * generator_loss

        grad_copy_probabilities = copy_gate * grad_probabilities
        grad_generator_probabilities = (1.0 - copy_gate) * grad_probabilities
        grad_generator_probabilities += generator_loss_weight * grad_generator_target_probabilities
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


def train_generator_hardened_pointer_sequence(
    rows: list[PreparedSequenceRow],
    method_name: str,
    *,
    model_seed: int,
    epochs: int = DEFAULT_EPOCHS,
    learning_rate: float = DEFAULT_LEARNING_RATE,
    l2: float = DEFAULT_L2,
    generator_loss_weight: float = DEFAULT_GENERATOR_LOSS_WEIGHT,
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
        loss, grads = _loss_and_gradient(rows, params, l2, generator_loss_weight)
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
        "value_output_mode": "generator_hardened_pointer_generator_copy_vocab_mixture",
        "initial_copy_gate_logit": DEFAULT_INITIAL_COPY_GATE_LOGIT,
        "generator_loss_weight": generator_loss_weight,
        "params": rounded_params,
        "param_sha256": hashlib.sha256(param_bytes).hexdigest(),
        "training_history": history,
        "final_training_loss": history[-1]["loss"],
    }


def evaluate_generator_hardened_pointer_sequence(rows: list[PreparedSequenceRow], params: dict[str, np.ndarray]) -> dict[str, Any]:
    losses: list[float] = []
    generator_losses: list[float] = []
    top1_hits: list[float] = []
    generator_top1_hits: list[float] = []
    reciprocal_ranks: list[float] = []
    generator_reciprocal_ranks: list[float] = []
    target_masses: list[float] = []
    copy_target_masses: list[float] = []
    generator_target_masses: list[float] = []
    copy_gates: list[float] = []
    top1_confidences: list[float] = []
    ranks: list[int] = []
    generator_ranks: list[int] = []
    for prepared in rows:
        probabilities, cache = _forward(prepared, params)
        generator_probabilities = cache["generator_probabilities"]
        target_values = prepared.row.target_values
        target_mass = max(float(np.sum(probabilities[list(target_values)])), 1e-12)
        generator_target_mass = max(float(np.sum(generator_probabilities[list(target_values)])), 1e-12)
        rank = _first_relevant_rank(probabilities, target_values)
        generator_rank = _first_relevant_rank(generator_probabilities, target_values)
        top_value = _ranked_indices(probabilities)[0]
        generator_top_value = _ranked_indices(generator_probabilities)[0]
        top1_correct = 1.0 if top_value in set(target_values) else 0.0
        generator_top1_correct = 1.0 if generator_top_value in set(target_values) else 0.0

        losses.append(-math.log(target_mass))
        generator_losses.append(-math.log(generator_target_mass))
        top1_hits.append(top1_correct)
        generator_top1_hits.append(generator_top1_correct)
        reciprocal_ranks.append(1.0 / float(rank))
        generator_reciprocal_ranks.append(1.0 / float(generator_rank))
        target_masses.append(target_mass)
        copy_target_masses.append(float(np.sum(cache["copy_probabilities"][list(target_values)])))
        generator_target_masses.append(generator_target_mass)
        copy_gates.append(float(cache["copy_gate"]))
        top1_confidences.append(float(probabilities[top_value]))
        ranks.append(rank)
        generator_ranks.append(generator_rank)
    mean_loss = float(np.mean(losses))
    mean_generator_loss = float(np.mean(generator_losses))
    return {
        "row_count": len(rows),
        "loss": round(mean_loss, 6),
        "perplexity": round(float(math.exp(mean_loss)), 6),
        "generator_loss": round(mean_generator_loss, 6),
        "generator_perplexity": round(float(math.exp(mean_generator_loss)), 6),
        "top1_accuracy": round(float(np.mean(top1_hits)), 6),
        "mrr": round(float(np.mean(reciprocal_ranks)), 6),
        "generator_top1_accuracy": round(float(np.mean(generator_top1_hits)), 6),
        "generator_mrr": round(float(np.mean(generator_reciprocal_ranks)), 6),
        "mean_target_value_probability": round(float(np.mean(target_masses)), 6),
        "mean_target_attention_probability": round(float(np.mean(copy_target_masses)), 6),
        "mean_generator_target_probability": round(float(np.mean(generator_target_masses)), 6),
        "mean_copy_gate": round(float(np.mean(copy_gates)), 6),
        "target_value_probability_mae": round(float(np.mean([1.0 - value for value in target_masses])), 6),
        "mean_top1_confidence": round(float(np.mean(top1_confidences)), 6),
        "expected_calibration_error": round(_expected_calibration_error(top1_confidences, top1_hits), 6),
        "mean_first_relevant_value_rank": round(float(np.mean(ranks)), 6),
        "mean_generator_first_relevant_value_rank": round(float(np.mean(generator_ranks)), 6),
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
        "generator_loss",
        "top1_accuracy",
        "mrr",
        "generator_top1_accuracy",
        "generator_mrr",
        "mean_target_value_probability",
        "mean_target_attention_probability",
        "mean_generator_target_probability",
        "mean_copy_gate",
        "target_value_probability_mae",
        "mean_top1_confidence",
        "expected_calibration_error",
        "mean_first_relevant_value_rank",
        "mean_generator_first_relevant_value_rank",
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
        "value_output_mode": "generator_hardened_pointer_generator_copy_vocab_mixture",
        "curriculum": "train_128_256_512_validate_1024_test_2048",
    }
    for metric_name in metric_names:
        values = [float(item[metric_name]) for item in run_rows]
        ci = _metric_ci(values, seed_text=f"stage43:{method_name}:{metric_name}")
        row[f"{metric_name}_mean"] = round(float(np.mean(values)), 6)
        row[f"{metric_name}_ci_low"] = ci["low"]
        row[f"{metric_name}_ci_high"] = ci["high"]
    return row


def run_stage43_benchmark(
    *,
    data_seeds: tuple[int, ...] = DATA_SEEDS,
    model_seeds: tuple[int, ...] = DEFAULT_MODEL_SEEDS,
    context_lengths: tuple[int, ...] = DEFAULT_CONTEXT_LENGTHS,
    examples_per_task_length: int = DEFAULT_EXAMPLES_PER_TASK_LENGTH,
    epochs: int = DEFAULT_EPOCHS,
    learning_rate: float = DEFAULT_LEARNING_RATE,
    l2: float = DEFAULT_L2,
    generator_loss_weight: float = DEFAULT_GENERATOR_LOSS_WEIGHT,
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
            training = train_generator_hardened_pointer_sequence(
                prepared_splits["train"],
                method_name,
                model_seed=model_seed,
                epochs=epochs,
                learning_rate=learning_rate,
                l2=l2,
                generator_loss_weight=generator_loss_weight,
                hidden_dim=hidden_dim,
                value_embed_dim=value_embed_dim,
            )
            training_records.append(training)
            params = _params_from_record(training)
            for split_name, target_table in (("train", train_table), ("validation", validation_table), ("test", run_table)):
                row = evaluate_generator_hardened_pointer_sequence(prepared_splits[split_name], params)
                row["method"] = method_name
                row["model_seed"] = model_seed
                row["split"] = split_name
                target_table.append(row)
            test_row = run_table[-1]
            if float(test_row["top1_accuracy"]) < 0.5:
                weak_runs.append({"method": method_name, "model_seed": model_seed, "top1_accuracy": test_row["top1_accuracy"], "mrr": test_row["mrr"], "criterion": "test_top1_accuracy_below_0.5"})
            if float(test_row["generator_top1_accuracy"]) < 0.5:
                weak_runs.append({"method": method_name, "model_seed": model_seed, "generator_top1_accuracy": test_row["generator_top1_accuracy"], "generator_mrr": test_row["generator_mrr"], "criterion": "generator_test_top1_accuracy_below_0.5"})
            for task_name in TASK_NAMES:
                task_rows = [prepared for prepared in prepared_splits["test"] if prepared.row.task == task_name]
                task_result = evaluate_generator_hardened_pointer_sequence(task_rows, params)
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
    generator_selection_table = sorted(table, key=lambda row: (row["generator_top1_accuracy_mean"], row["generator_mrr_mean"], row["mean_generator_target_probability_mean"], row["method"]), reverse=True)
    return {
        "schema_version": STAGE43_SCHEMA_VERSION,
        "stage": "stage43_generator_hardened_pointer_sequence",
        "dataset": "stage14_full_prefix_generator_hardened_pointer_sequence_v1",
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
            "type": "single_query_sequence_decoder_generator_hardened_pointer_generator",
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
            "value_output_mode": "generator-hardened pointer-generator mixture of copied prefix-token mass and learned vocab distribution",
            "initial_copy_gate_logit": DEFAULT_INITIAL_COPY_GATE_LOGIT,
            "generator_loss_weight": generator_loss_weight,
        },
        "task": {
            "description": "Generator-target hardening follow-up to the Stage 42 trainable pointer-generator sequence diagnostic.",
            "target_construction": "Targets are explicit Stage 12 retrieval-rule value tokens, not PhaseWrap-selected labels.",
            "scope": "This tests whether the weak Stage 42 learned generator branch is a training-starvation bottleneck.",
        },
        "claim_boundary": {
            "supported": [
                "A deterministic generator-target-hardening diagnostic for the all-prefix compact sequence decoder.",
                "Evidence about whether direct generator supervision improves the Stage 42 weak learned vocab branch.",
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
        "generator_selection_table": generator_selection_table,
        "weak_runs": weak_runs,
        "best_method_by_test_top1_mrr": selection_table[0]["method"],
        "best_generator_method_by_test_top1_mrr": generator_selection_table[0]["method"],
    }


def write_stage43_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
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


def print_stage43_table(result: dict[str, Any]) -> None:
    columns = (
        "method",
        "run_count",
        "parameter_count",
        "top1_accuracy_mean",
        "mrr_mean",
        "mean_target_value_probability_mean",
        "generator_top1_accuracy_mean",
        "mean_generator_target_probability_mean",
        "mean_copy_gate_mean",
        "expected_calibration_error_mean",
    )
    print(" | ".join(columns))
    print(" | ".join("---" for _ in columns))
    for row in result["selection_table"]:
        print(" | ".join(str(row[column]) for column in columns))
