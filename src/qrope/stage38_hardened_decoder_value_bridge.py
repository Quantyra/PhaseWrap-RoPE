from __future__ import annotations

import csv
import hashlib
import json
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
    make_stage14_examples,
    split_examples,
)
from .stage34_small_decoder_value_bridge import (
    FEATURE_DIM,
    METHOD_NAMES,
    _parameter_count,
    _params_from_record,
    evaluate_decoder_value_bridge,
    train_decoder_value_bridge,
)


STAGE38_SCHEMA_VERSION = "qrope_stage38_hardened_decoder_value_bridge_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage38_hardened_decoder_value_bridge"
DEFAULT_MODEL_SEEDS = (3803, 3821, 3823, 3833, 3847)
HARDENED_HIDDEN_DIM = 16
HARDENED_VALUE_EMBED_DIM = 64
HARDENED_EPOCHS = 360
HARDENED_LEARNING_RATE = 0.03
HARDENED_L2 = 0.00001


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
    }
    for metric_name in metric_names:
        values = [float(item[metric_name]) for item in run_rows]
        ci = _metric_ci(values, seed_text=f"stage38:{method_name}:{metric_name}")
        row[f"{metric_name}_mean"] = round(float(np.mean(values)), 6)
        row[f"{metric_name}_ci_low"] = ci["low"]
        row[f"{metric_name}_ci_high"] = ci["high"]
    return row


def run_stage38_benchmark(
    *,
    data_seeds: tuple[int, ...] = DATA_SEEDS,
    model_seeds: tuple[int, ...] = DEFAULT_MODEL_SEEDS,
    context_lengths: tuple[int, ...] = DEFAULT_CONTEXT_LENGTHS,
    examples_per_task_length: int = DEFAULT_EXAMPLES_PER_TASK_LENGTH,
    epochs: int = HARDENED_EPOCHS,
    learning_rate: float = HARDENED_LEARNING_RATE,
    l2: float = HARDENED_L2,
    hidden_dim: int = HARDENED_HIDDEN_DIM,
    value_embed_dim: int = HARDENED_VALUE_EMBED_DIM,
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
            training = train_decoder_value_bridge(
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
                row = evaluate_decoder_value_bridge(splits[split_name], method_name, params)
                row["method"] = method_name
                row["model_seed"] = model_seed
                row["split"] = split_name
                target_table.append(row)
            test_row = run_table[-1]
            if float(test_row["top1_accuracy"]) < 0.5:
                weak_runs.append({"method": method_name, "model_seed": model_seed, "top1_accuracy": test_row["top1_accuracy"], "mrr": test_row["mrr"], "criterion": "test_top1_accuracy_below_0.5"})
            for task_name in TASK_NAMES:
                task_rows = [example for example in splits["test"] if example.task == task_name]
                task_result = evaluate_decoder_value_bridge(task_rows, method_name, params)
                task_result["method"] = method_name
                task_result["model_seed"] = model_seed
                task_result["task"] = task_name
                task_table.append(task_result)
    table = [
        _aggregate_runs(
            [row for row in run_table if row["method"] == method_name],
            method_name=method_name,
            hidden_dim=hidden_dim,
            value_embed_dim=value_embed_dim,
        )
        for method_name in method_names
    ]
    train_summary = [
        _aggregate_runs(
            [row for row in train_table if row["method"] == method_name],
            method_name=method_name,
            hidden_dim=hidden_dim,
            value_embed_dim=value_embed_dim,
        )
        for method_name in method_names
    ]
    validation_summary = [
        _aggregate_runs(
            [row for row in validation_table if row["method"] == method_name],
            method_name=method_name,
            hidden_dim=hidden_dim,
            value_embed_dim=value_embed_dim,
        )
        for method_name in method_names
    ]
    selection_table = sorted(table, key=lambda row: (row["top1_accuracy_mean"], row["mrr_mean"], row["mean_target_value_probability_mean"], row["method"]), reverse=True)
    return {
        "schema_version": STAGE38_SCHEMA_VERSION,
        "stage": "stage38_hardened_decoder_value_bridge",
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
            "type": "hardened_nonlinear_attention_plus_learned_value_output_bridge",
            "feature_dim": FEATURE_DIM,
            "hidden_dim": hidden_dim,
            "value_vocab_size": VALUE_VOCAB_SIZE,
            "value_embed_dim": value_embed_dim,
            "parameter_count": _parameter_count(hidden_dim, value_embed_dim),
            "epochs": epochs,
            "learning_rate": learning_rate,
            "l2": l2,
            "optimizer": "full_batch_adam",
            "trained_parameters": "feature bridge attention, value embeddings, output projection, output bias",
        },
        "task": {
            "description": "Train-short/test-long key-value retrieval with hardened learned attention and learned value-token output.",
            "target_construction": "Targets are explicit Stage 12 retrieval-rule value tokens, not PhaseWrap-selected labels.",
            "scope": "This tests whether capacity/training hardening improves the learned decoder-style value bridge without copy-value output.",
        },
        "claim_boundary": {
            "supported": [
                "A deterministic hardened compact decoder-style value benchmark on non-phase-cued retrieval rows.",
                "Evidence about whether larger value embeddings, larger hidden width, and longer Adam training improve Stage 34.",
                "Matched architecture, optimizer, parameter count, data splits, confidence intervals, and explicit weak-run reporting across positional variants.",
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


def write_stage38_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
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


def print_stage38_table(result: dict[str, Any]) -> None:
    columns = ("method", "run_count", "parameter_count", "top1_accuracy_mean", "mrr_mean", "mean_target_value_probability_mean", "expected_calibration_error_mean")
    print(" | ".join(columns))
    print(" | ".join("---" for _ in columns))
    for row in result["selection_table"]:
        print(" | ".join(str(row[column]) for column in columns))
