from __future__ import annotations

import csv
import hashlib
import json
import math
import random
from pathlib import Path
from typing import Any

import numpy as np

from .stage12_ruler_retrieval import (
    DEFAULT_CONTEXT_LENGTHS,
    DEFAULT_EXAMPLES_PER_TASK_LENGTH,
    DEFAULT_SEEDS as DATA_SEEDS,
    TASK_NAMES,
    Stage12Example,
    make_stage12_examples,
)
from .stage13_positional_adapter import split_examples
from .stage32_full_context_feature_bridge import (
    DEFAULT_MODEL_SEEDS,
    HIDDEN_DIM,
    full_context_bridge_features,
    train_full_context_bridge,
)


STAGE33_SCHEMA_VERSION = "qrope_stage33_temperature_calibration_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage33_temperature_calibration"
METHOD_NAMES = ("rope_relative", "sinusoidal", "phasewrap_distance_adapter", "phasewrap_multiscale_adapter")
TEMPERATURE_GRID = (0.25, 0.33, 0.5, 0.67, 0.8, 1.0, 1.25, 1.5, 2.0, 3.0, 4.0)


def _softmax(values: np.ndarray) -> np.ndarray:
    shifted = values - np.max(values)
    exp_values = np.exp(shifted)
    return exp_values / np.sum(exp_values)


def _params_from_record(record: dict[str, Any]) -> dict[str, np.ndarray]:
    return {key: np.array(value, dtype=float) for key, value in record["params"].items()}


def _logits(row: Stage12Example, method_name: str, params: dict[str, np.ndarray]) -> np.ndarray:
    features = full_context_bridge_features(row, method_name)
    hidden = np.tanh(features @ params["w1"] + params["b1"])
    return hidden @ params["w2"] + float(params["b2"][0])


def _ranked_indices(probabilities: np.ndarray) -> list[int]:
    return sorted(range(len(probabilities)), key=lambda index: (-float(probabilities[index]), index))


def _first_relevant_rank(probabilities: np.ndarray, target_positions: tuple[int, ...]) -> int:
    target_set = set(target_positions)
    for rank, index in enumerate(_ranked_indices(probabilities), start=1):
        if index in target_set:
            return rank
    raise RuntimeError("target absent from full context distribution")


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


def evaluate_with_temperature(rows: list[Stage12Example], method_name: str, params: dict[str, np.ndarray], temperature: float) -> dict[str, Any]:
    losses: list[float] = []
    top1_hits: list[float] = []
    reciprocal_ranks: list[float] = []
    target_masses: list[float] = []
    top1_confidences: list[float] = []
    ranks: list[int] = []
    for row in rows:
        probabilities = _softmax(_logits(row, method_name, params) / temperature)
        rank = _first_relevant_rank(probabilities, row.target_positions)
        top_index = _ranked_indices(probabilities)[0]
        top1_correct = 1.0 if top_index in set(row.target_positions) else 0.0
        target_mass = max(float(np.sum(probabilities[list(row.target_positions)])), 1e-12)
        losses.append(-math.log(target_mass))
        top1_hits.append(top1_correct)
        reciprocal_ranks.append(1.0 / float(rank))
        target_masses.append(target_mass)
        top1_confidences.append(float(probabilities[top_index]))
        ranks.append(rank)
    mean_loss = float(np.mean(losses))
    return {
        "row_count": len(rows),
        "temperature": temperature,
        "loss": round(mean_loss, 6),
        "perplexity": round(float(math.exp(mean_loss)), 6),
        "top1_accuracy": round(float(np.mean(top1_hits)), 6),
        "mrr": round(float(np.mean(reciprocal_ranks)), 6),
        "mean_target_probability": round(float(np.mean(target_masses)), 6),
        "target_probability_mae": round(float(np.mean([1.0 - value for value in target_masses])), 6),
        "mean_top1_confidence": round(float(np.mean(top1_confidences)), 6),
        "expected_calibration_error": round(_expected_calibration_error(top1_confidences, top1_hits), 6),
        "mean_first_relevant_rank": round(float(np.mean(ranks)), 6),
    }


def select_temperature(rows: list[Stage12Example], method_name: str, params: dict[str, np.ndarray], grid: tuple[float, ...] = TEMPERATURE_GRID) -> dict[str, Any]:
    scored = [evaluate_with_temperature(rows, method_name, params, temperature) for temperature in grid]
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
        "mean_target_probability",
        "target_probability_mae",
        "mean_top1_confidence",
        "expected_calibration_error",
        "mean_first_relevant_rank",
        "selected_temperature",
        "delta_target_probability",
        "delta_expected_calibration_error",
    )
    row: dict[str, Any] = {"method": method_name, "run_count": len(run_rows), "row_count": run_rows[0]["row_count"]}
    for metric_name in metric_names:
        values = [float(item[metric_name]) for item in run_rows]
        ci = _metric_ci(values, seed_text=f"stage33:{method_name}:{metric_name}")
        row[f"{metric_name}_mean"] = round(float(np.mean(values)), 6)
        row[f"{metric_name}_ci_low"] = ci["low"]
        row[f"{metric_name}_ci_high"] = ci["high"]
    return row


def run_stage33_benchmark(
    *,
    data_seeds: tuple[int, ...] = DATA_SEEDS,
    model_seeds: tuple[int, ...] = DEFAULT_MODEL_SEEDS,
    context_lengths: tuple[int, ...] = DEFAULT_CONTEXT_LENGTHS,
    examples_per_task_length: int = DEFAULT_EXAMPLES_PER_TASK_LENGTH,
    epochs: int = 45,
    method_names: tuple[str, ...] = METHOD_NAMES,
) -> dict[str, Any]:
    rows = make_stage12_examples(seeds=data_seeds, context_lengths=context_lengths, examples_per_task_length=examples_per_task_length)
    splits = split_examples(rows)
    training_records: list[dict[str, Any]] = []
    calibration_records: list[dict[str, Any]] = []
    run_table: list[dict[str, Any]] = []
    weak_runs: list[dict[str, Any]] = []
    for method_name in method_names:
        for model_seed in model_seeds:
            training = train_full_context_bridge(splits["train"], method_name, model_seed=model_seed, epochs=epochs)
            training_records.append(training)
            params = _params_from_record(training)
            calibration = select_temperature(splits["validation"], method_name, params)
            calibration_records.append({"method": method_name, "model_seed": model_seed, **calibration})
            uncalibrated_test_metrics = evaluate_with_temperature(splits["test"], method_name, params, 1.0)
            test_metrics = evaluate_with_temperature(splits["test"], method_name, params, float(calibration["selected_temperature"]))
            test_metrics["method"] = method_name
            test_metrics["model_seed"] = model_seed
            test_metrics["selected_temperature"] = calibration["selected_temperature"]
            test_metrics["uncalibrated_mean_target_probability"] = uncalibrated_test_metrics["mean_target_probability"]
            test_metrics["uncalibrated_expected_calibration_error"] = uncalibrated_test_metrics["expected_calibration_error"]
            test_metrics["delta_target_probability"] = round(
                float(test_metrics["mean_target_probability"]) - float(uncalibrated_test_metrics["mean_target_probability"]),
                6,
            )
            test_metrics["delta_expected_calibration_error"] = round(
                float(test_metrics["expected_calibration_error"]) - float(uncalibrated_test_metrics["expected_calibration_error"]),
                6,
            )
            run_table.append(test_metrics)
            if float(test_metrics["top1_accuracy"]) < 0.5:
                weak_runs.append({"method": method_name, "model_seed": model_seed, "top1_accuracy": test_metrics["top1_accuracy"], "mrr": test_metrics["mrr"], "criterion": "test_top1_accuracy_below_0.5"})
    table = [_aggregate_runs([row for row in run_table if row["method"] == method_name], method_name=method_name) for method_name in method_names]
    selection_table = sorted(table, key=lambda row: (row["top1_accuracy_mean"], row["mrr_mean"], row["mean_target_probability_mean"], -row["expected_calibration_error_mean"], row["method"]), reverse=True)
    return {
        "schema_version": STAGE33_SCHEMA_VERSION,
        "stage": "stage33_temperature_calibration",
        "dataset": "stage12_non_phase_cued_ruler_style_retrieval_v1",
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "data_seeds": list(data_seeds),
        "model_seeds": list(model_seeds),
        "context_lengths": list(context_lengths),
        "train_lengths": [128, 256],
        "validation_lengths": [512],
        "test_lengths": [1024],
        "examples_per_task_length": examples_per_task_length,
        "method_names": list(method_names),
        "train_row_count": len(splits["train"]),
        "validation_row_count": len(splits["validation"]),
        "test_row_count": len(splits["test"]),
        "model": {
            "base_model": "stage32_one_hidden_layer_full_context_feature_bridge",
            "hidden_dim": HIDDEN_DIM,
            "epochs": epochs,
            "posthoc_calibration": "temperature selected on validation loss over a fixed grid",
            "temperature_grid": list(TEMPERATURE_GRID),
        },
        "task": {
            "description": "Validation-selected post-hoc temperature calibration for the Stage 32 full-context feature bridge.",
            "target_construction": "Targets are selected by explicit retrieval rules, not by the PhaseWrap score.",
            "scope": "This is a calibration audit for a compact feature bridge, not a full decoder-only language-model benchmark.",
        },
        "claim_boundary": {
            "supported": [
                "A deterministic temperature-calibration audit for Stage 32 full-context feature-bridge outputs.",
                "Evidence about whether the PhaseWrap probability/calibration gap is closed by simple post-hoc temperature scaling.",
                "Confidence intervals over initialization seeds and explicit weak-run reporting.",
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
        "table": table,
        "selection_table": selection_table,
        "weak_runs": weak_runs,
        "best_method_by_test_top1_mrr_probability": selection_table[0]["method"],
    }


def write_stage33_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
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
        "method_names": result["method_names"],
        "model": result["model"],
        "task": result["task"],
        "result_path": str((output_dir / "results.json").as_posix()),
        "summary_csv_path": str((output_dir / "summary.csv").as_posix()),
        "per_run_csv_path": str((output_dir / "per_run_results.csv").as_posix()),
        "weak_runs_path": str((output_dir / "weak_runs.json").as_posix()),
        "claim_boundary": result["claim_boundary"],
    }
    paths = {
        "manifest": str(output_dir / "manifest.json"),
        "results": str(output_dir / "results.json"),
        "summary_csv": str(output_dir / "summary.csv"),
        "per_run_csv": str(output_dir / "per_run_results.csv"),
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
    return paths


def print_stage33_table(result: dict[str, Any]) -> None:
    columns = (
        "method",
        "run_count",
        "top1_accuracy_mean",
        "mrr_mean",
        "mean_target_probability_mean",
        "expected_calibration_error_mean",
        "delta_target_probability_mean",
        "delta_expected_calibration_error_mean",
        "selected_temperature_mean",
    )
    print(" | ".join(columns))
    print(" | ".join("---" for _ in columns))
    for row in result["selection_table"]:
        print(" | ".join(str(row[column]) for column in columns))
