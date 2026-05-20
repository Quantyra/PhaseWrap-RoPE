from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import numpy as np

from .stage13_positional_adapter import METHOD_NAMES, positional_features
from .stage14_attention_readout import (
    DEFAULT_CONTEXT_LENGTHS,
    DEFAULT_EXAMPLES_PER_TASK_LENGTH,
    DEFAULT_SEEDS,
    TASK_NAMES,
    _stage12_proxy,
    make_stage14_examples,
    split_examples,
)
from .stage15_learned_attention import (
    HIDDEN_DIM,
    _init_params,
    _loss_and_gradient,
    evaluate_learned_attention,
)


STAGE16_SCHEMA_VERSION = "qrope_stage16_learned_attention_stability_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage16_learned_attention_stability"
DEFAULT_INIT_SEEDS = (1009, 1013, 1019, 1021, 1031)


def train_with_init_seed(
    rows,
    method_name: str,
    init_seed: int,
    *,
    epochs: int = 180,
    learning_rate: float = 0.2,
    l2: float = 0.001,
) -> dict[str, Any]:
    if not rows:
        raise ValueError("rows must be non-empty")
    feature_dim = positional_features(_stage12_proxy(rows[0]), method_name).shape[1]
    params = _init_params(feature_dim, f"stage16:{method_name}:{init_seed}", hidden_dim=HIDDEN_DIM)
    history: list[dict[str, float]] = []
    for epoch in range(epochs):
        loss, grads = _loss_and_gradient(rows, method_name, params, l2)
        for key in params:
            params[key] -= learning_rate * grads[key]
        if epoch in {0, epochs // 4, epochs // 2, epochs - 1}:
            history.append({"epoch": epoch + 1, "loss": round(loss, 6)})
    return {
        "method": method_name,
        "init_seed": init_seed,
        "epochs": epochs,
        "learning_rate": learning_rate,
        "l2": l2,
        "hidden_dim": HIDDEN_DIM,
        "params": {key: np.round(value, 8).tolist() for key, value in params.items()},
        "training_history": history,
        "final_training_loss": history[-1]["loss"],
    }


def _params_from_record(record: dict[str, Any]) -> dict[str, np.ndarray]:
    return {key: np.array(value, dtype=float) for key, value in record["params"].items()}


def _mean_ci(values: list[float]) -> dict[str, float]:
    if not values:
        raise ValueError("cannot summarize empty values")
    sorted_values = sorted(values)
    low_index = int(0.025 * (len(sorted_values) - 1))
    high_index = int(0.975 * (len(sorted_values) - 1))
    return {
        "mean": round(float(np.mean(values)), 6),
        "min": round(float(min(values)), 6),
        "max": round(float(max(values)), 6),
        "ci_low": round(float(sorted_values[low_index]), 6),
        "ci_high": round(float(sorted_values[high_index]), 6),
    }


def run_stage16_benchmark(
    *,
    seeds: tuple[int, ...] = DEFAULT_SEEDS,
    context_lengths: tuple[int, ...] = DEFAULT_CONTEXT_LENGTHS,
    examples_per_task_length: int = DEFAULT_EXAMPLES_PER_TASK_LENGTH,
    init_seeds: tuple[int, ...] = DEFAULT_INIT_SEEDS,
    epochs: int = 180,
) -> dict[str, Any]:
    rows = make_stage14_examples(
        seeds=seeds,
        context_lengths=context_lengths,
        examples_per_task_length=examples_per_task_length,
    )
    splits = split_examples(rows)
    per_run_table: list[dict[str, Any]] = []
    training_records: list[dict[str, Any]] = []
    for method_name in METHOD_NAMES:
        for init_seed in init_seeds:
            training = train_with_init_seed(splits["train"], method_name, init_seed, epochs=epochs)
            training_records.append(training)
            metrics = evaluate_learned_attention(splits["test"], method_name, _params_from_record(training))
            per_run_table.append(
                {
                    "method": method_name,
                    "init_seed": init_seed,
                    "row_count": metrics["row_count"],
                    "top1_accuracy": metrics["top1_accuracy"],
                    "mrr": metrics["mrr"],
                    "mean_target_value_probability": metrics["mean_target_value_probability"],
                    "mean_first_relevant_value_rank": metrics["mean_first_relevant_value_rank"],
                    "loss": metrics["loss"],
                }
            )
    aggregate_table: list[dict[str, Any]] = []
    for method_name in METHOD_NAMES:
        rows_for_method = [row for row in per_run_table if row["method"] == method_name]
        record: dict[str, Any] = {"method": method_name, "init_seed_count": len(rows_for_method), "row_count": splits["test"].__len__()}
        for metric in ("top1_accuracy", "mrr", "mean_target_value_probability", "mean_first_relevant_value_rank", "loss"):
            summary = _mean_ci([float(row[metric]) for row in rows_for_method])
            for key, value in summary.items():
                record[f"{metric}_{key}"] = value
        aggregate_table.append(record)
    selection_table = sorted(
        aggregate_table,
        key=lambda row: (
            row["top1_accuracy_mean"],
            row["mrr_mean"],
            row["mean_target_value_probability_mean"],
            row["method"],
        ),
        reverse=True,
    )
    return {
        "schema_version": STAGE16_SCHEMA_VERSION,
        "stage": "stage16_learned_attention_stability",
        "dataset": "deterministic_non_phase_cued_key_value_learned_attention_stability_v1",
        "no_hardware_submission": True,
        "seeds": list(seeds),
        "context_lengths": list(context_lengths),
        "init_seeds": list(init_seeds),
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
            "replication_axis": "initialization seed",
        },
        "claim_boundary": {
            "supported": [
                "A deterministic initialization-stability check for the Stage 15 learned attention-readout benchmark.",
                "Evidence about whether PhaseWrap-plus-distance ranking behavior persists across multiple learned scorer initializations.",
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
        "per_run_table": per_run_table,
        "aggregate_table": aggregate_table,
        "selection_table": selection_table,
        "best_method_by_mean_top1_mrr": selection_table[0]["method"],
    }


def write_stage16_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "dataset": result["dataset"],
        "no_hardware_submission": result["no_hardware_submission"],
        "init_seeds": result["init_seeds"],
        "train_row_count": result["train_row_count"],
        "validation_row_count": result["validation_row_count"],
        "test_row_count": result["test_row_count"],
        "method_names": result["method_names"],
        "model": result["model"],
        "result_path": str((output_dir / "results.json").as_posix()),
        "summary_csv_path": str((output_dir / "summary.csv").as_posix()),
        "per_run_csv_path": str((output_dir / "per_run_results.csv").as_posix()),
        "claim_boundary": result["claim_boundary"],
    }
    paths = {
        "manifest": str(output_dir / "manifest.json"),
        "results": str(output_dir / "results.json"),
        "summary_csv": str(output_dir / "summary.csv"),
        "per_run_csv": str(output_dir / "per_run_results.csv"),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(result["aggregate_table"][0].keys()))
        writer.writeheader()
        writer.writerows(result["aggregate_table"])
    with (output_dir / "per_run_results.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(result["per_run_table"][0].keys()))
        writer.writeheader()
        writer.writerows(result["per_run_table"])
    return paths


def print_stage16_table(result: dict[str, Any]) -> None:
    columns = (
        "method",
        "init_seed_count",
        "top1_accuracy_mean",
        "top1_accuracy_min",
        "top1_accuracy_max",
        "mrr_mean",
        "mean_target_value_probability_mean",
        "mean_target_value_probability_min",
        "mean_target_value_probability_max",
    )
    print(" | ".join(columns))
    print(" | ".join("---" for _ in columns))
    for row in result["selection_table"]:
        print(" | ".join(str(row[column]) for column in columns))
