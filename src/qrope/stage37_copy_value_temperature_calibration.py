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
from .stage33_temperature_calibration import TEMPERATURE_GRID
from .stage34_small_decoder_value_bridge import FEATURE_DIM, HIDDEN_DIM, METHOD_NAMES, decoder_value_bridge_features
from .stage36_copy_value_bridge import _parameter_count, _params_from_record, train_copy_value_bridge


STAGE37_SCHEMA_VERSION = "qrope_stage37_copy_value_temperature_calibration_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage37_copy_value_temperature_calibration"
DEFAULT_MODEL_SEEDS = (3707, 3719, 3727, 3733, 3739)


def _softmax(values: np.ndarray) -> np.ndarray:
    shifted = values - np.max(values)
    exp_values = np.exp(shifted)
    return exp_values / np.sum(exp_values)


def _copy_value_logits(row: Stage14Example, method_name: str, params: dict[str, np.ndarray]) -> np.ndarray:
    features = decoder_value_bridge_features(row, method_name)
    hidden = np.tanh(features @ params["w1"] + params["b1"])
    return hidden @ params["w2"] + float(params["b2"][0])


def _value_distribution(row: Stage14Example, attention: np.ndarray) -> np.ndarray:
    values = np.zeros(VALUE_VOCAB_SIZE, dtype=float)
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


def evaluate_copy_value_with_temperature(
    rows: list[Stage14Example],
    method_name: str,
    params: dict[str, np.ndarray],
    temperature: float,
) -> dict[str, Any]:
    losses: list[float] = []
    top1_hits: list[float] = []
    reciprocal_ranks: list[float] = []
    target_value_masses: list[float] = []
    target_attention_masses: list[float] = []
    top1_confidences: list[float] = []
    ranks: list[int] = []
    for row in rows:
        attention = _softmax(_copy_value_logits(row, method_name, params) / temperature)
        values = _value_distribution(row, attention)
        target_value_mass = max(float(np.sum(values[list(row.target_values)])), 1e-12)
        target_attention_mass = max(
            float(sum(float(attention[index]) for index, position in enumerate(row.key_positions) if position in set(row.target_positions))),
            1e-12,
        )
        rank = _first_relevant_rank(values, row.target_values)
        top_value = _ranked_indices(values)[0]
        top1_correct = 1.0 if top_value in set(row.target_values) else 0.0
        losses.append(-math.log(target_value_mass))
        top1_hits.append(top1_correct)
        reciprocal_ranks.append(1.0 / float(rank))
        target_value_masses.append(target_value_mass)
        target_attention_masses.append(target_attention_mass)
        top1_confidences.append(float(values[top_value]))
        ranks.append(rank)
    mean_loss = float(np.mean(losses))
    return {
        "row_count": len(rows),
        "temperature": temperature,
        "loss": round(mean_loss, 6),
        "perplexity": round(float(math.exp(mean_loss)), 6),
        "top1_accuracy": round(float(np.mean(top1_hits)), 6),
        "mrr": round(float(np.mean(reciprocal_ranks)), 6),
        "mean_target_value_probability": round(float(np.mean(target_value_masses)), 6),
        "mean_target_attention_probability": round(float(np.mean(target_attention_masses)), 6),
        "target_value_probability_mae": round(float(np.mean([1.0 - value for value in target_value_masses])), 6),
        "mean_top1_confidence": round(float(np.mean(top1_confidences)), 6),
        "expected_calibration_error": round(_expected_calibration_error(top1_confidences, top1_hits), 6),
        "mean_first_relevant_value_rank": round(float(np.mean(ranks)), 6),
    }


def select_copy_value_temperature(
    rows: list[Stage14Example],
    method_name: str,
    params: dict[str, np.ndarray],
    grid: tuple[float, ...] = TEMPERATURE_GRID,
) -> dict[str, Any]:
    scored = [evaluate_copy_value_with_temperature(rows, method_name, params, temperature) for temperature in grid]
    best = sorted(scored, key=lambda row: (row["loss"], row["expected_calibration_error"], row["temperature"]))[0]
    return {"selected_temperature": best["temperature"], "validation_table": scored, "selection_metric": "validation_loss_then_ece"}


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
        "selected_temperature",
        "delta_target_value_probability",
        "delta_target_attention_probability",
        "delta_expected_calibration_error",
    )
    row: dict[str, Any] = {
        "method": method_name,
        "run_count": len(run_rows),
        "row_count": run_rows[0]["row_count"],
        "feature_dim": FEATURE_DIM,
        "hidden_dim": HIDDEN_DIM,
        "parameter_count": _parameter_count(),
        "value_output_mode": "copy_attention_mass_to_candidate_values",
        "posthoc_calibration": "temperature selected on validation loss over a fixed grid",
    }
    for metric_name in metric_names:
        values = [float(item[metric_name]) for item in run_rows]
        ci = _metric_ci(values, seed_text=f"stage37:{method_name}:{metric_name}")
        row[f"{metric_name}_mean"] = round(float(np.mean(values)), 6)
        row[f"{metric_name}_ci_low"] = ci["low"]
        row[f"{metric_name}_ci_high"] = ci["high"]
    return row


def run_stage37_benchmark(
    *,
    data_seeds: tuple[int, ...] = DATA_SEEDS,
    model_seeds: tuple[int, ...] = DEFAULT_MODEL_SEEDS,
    context_lengths: tuple[int, ...] = DEFAULT_CONTEXT_LENGTHS,
    examples_per_task_length: int = DEFAULT_EXAMPLES_PER_TASK_LENGTH,
    epochs: int = 80,
    method_names: tuple[str, ...] = METHOD_NAMES,
    temperature_grid: tuple[float, ...] = TEMPERATURE_GRID,
) -> dict[str, Any]:
    rows = make_stage14_examples(seeds=data_seeds, context_lengths=context_lengths, examples_per_task_length=examples_per_task_length)
    splits = split_examples(rows)
    training_records: list[dict[str, Any]] = []
    calibration_records: list[dict[str, Any]] = []
    run_table: list[dict[str, Any]] = []
    task_table: list[dict[str, Any]] = []
    weak_runs: list[dict[str, Any]] = []
    for method_name in method_names:
        for model_seed in model_seeds:
            training = train_copy_value_bridge(splits["train"], method_name, model_seed=model_seed, epochs=epochs)
            training_records.append(training)
            params = _params_from_record(training)
            calibration = select_copy_value_temperature(splits["validation"], method_name, params, grid=temperature_grid)
            calibration_records.append({"method": method_name, "model_seed": model_seed, **calibration})
            uncalibrated_test_metrics = evaluate_copy_value_with_temperature(splits["test"], method_name, params, 1.0)
            test_metrics = evaluate_copy_value_with_temperature(splits["test"], method_name, params, float(calibration["selected_temperature"]))
            test_metrics["method"] = method_name
            test_metrics["model_seed"] = model_seed
            test_metrics["selected_temperature"] = calibration["selected_temperature"]
            test_metrics["uncalibrated_mean_target_value_probability"] = uncalibrated_test_metrics["mean_target_value_probability"]
            test_metrics["uncalibrated_mean_target_attention_probability"] = uncalibrated_test_metrics["mean_target_attention_probability"]
            test_metrics["uncalibrated_expected_calibration_error"] = uncalibrated_test_metrics["expected_calibration_error"]
            test_metrics["delta_target_value_probability"] = round(
                float(test_metrics["mean_target_value_probability"]) - float(uncalibrated_test_metrics["mean_target_value_probability"]),
                6,
            )
            test_metrics["delta_target_attention_probability"] = round(
                float(test_metrics["mean_target_attention_probability"]) - float(uncalibrated_test_metrics["mean_target_attention_probability"]),
                6,
            )
            test_metrics["delta_expected_calibration_error"] = round(
                float(test_metrics["expected_calibration_error"]) - float(uncalibrated_test_metrics["expected_calibration_error"]),
                6,
            )
            run_table.append(test_metrics)
            if float(test_metrics["top1_accuracy"]) < 0.5:
                weak_runs.append({"method": method_name, "model_seed": model_seed, "top1_accuracy": test_metrics["top1_accuracy"], "mrr": test_metrics["mrr"], "criterion": "test_top1_accuracy_below_0.5"})
            for task_name in TASK_NAMES:
                task_rows = [example for example in splits["test"] if example.task == task_name]
                task_result = evaluate_copy_value_with_temperature(task_rows, method_name, params, float(calibration["selected_temperature"]))
                task_result["method"] = method_name
                task_result["model_seed"] = model_seed
                task_result["task"] = task_name
                task_result["selected_temperature"] = calibration["selected_temperature"]
                task_table.append(task_result)
    table = [_aggregate_runs([row for row in run_table if row["method"] == method_name], method_name=method_name) for method_name in method_names]
    selection_table = sorted(table, key=lambda row: (row["top1_accuracy_mean"], row["mrr_mean"], row["mean_target_value_probability_mean"], -row["expected_calibration_error_mean"], row["method"]), reverse=True)
    return {
        "schema_version": STAGE37_SCHEMA_VERSION,
        "stage": "stage37_copy_value_temperature_calibration",
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
            "base_model": "stage36_nonlinear_attention_copy_value_bridge",
            "feature_dim": FEATURE_DIM,
            "hidden_dim": HIDDEN_DIM,
            "parameter_count": _parameter_count(),
            "epochs": epochs,
            "optimizer": "full_batch_gradient_descent",
            "trained_parameters": "feature bridge attention only",
            "value_output_mode": "copy attention mass to candidate value tokens",
            "posthoc_calibration": "temperature selected on validation loss over a fixed grid",
            "temperature_grid": list(temperature_grid),
        },
        "task": {
            "description": "Validation-selected post-hoc temperature calibration for the Stage 36 copy-value bridge.",
            "target_construction": "Targets are explicit Stage 12 retrieval-rule value tokens, not PhaseWrap-selected labels.",
            "scope": "This tests whether the remaining Stage 36 probability-mass gap is a scalar sharpness issue.",
        },
        "claim_boundary": {
            "supported": [
                "A deterministic temperature-calibration audit for the Stage 36 copy-value bridge.",
                "Evidence about whether scalar attention sharpness closes the copy-value probability-mass gap.",
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
        "calibration_records": calibration_records,
        "run_table": run_table,
        "task_table": task_table,
        "table": table,
        "selection_table": selection_table,
        "weak_runs": weak_runs,
        "best_method_by_test_top1_mrr_probability": selection_table[0]["method"],
    }


def write_stage37_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
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


def print_stage37_table(result: dict[str, Any]) -> None:
    columns = (
        "method",
        "run_count",
        "top1_accuracy_mean",
        "mrr_mean",
        "mean_target_value_probability_mean",
        "expected_calibration_error_mean",
        "delta_target_value_probability_mean",
        "delta_expected_calibration_error_mean",
        "selected_temperature_mean",
    )
    print(" | ".join(columns))
    print(" | ".join("---" for _ in columns))
    for row in result["selection_table"]:
        print(" | ".join(str(row[column]) for column in columns))
