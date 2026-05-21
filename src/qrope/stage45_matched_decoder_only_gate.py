from __future__ import annotations

import csv
import hashlib
import json
import random
from pathlib import Path
from typing import Any

import numpy as np

from .stage10_small_decoder_transformer import (
    DEFAULT_SEEDS,
    EXAMPLES_PER_LENGTH,
    TASK_NAMES,
    TEST_LENGTHS,
    TRAIN_LENGTHS,
    VALIDATION_LENGTHS,
    autograd_available,
    evaluate_small_decoder,
    make_stage10_splits,
    train_small_decoder,
)


STAGE45_SCHEMA_VERSION = "qrope_stage45_matched_decoder_only_gate_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage45_matched_decoder_only_gate"
DEFAULT_EPOCHS = 60
METHOD_NAMES = (
    "no_position",
    "sinusoidal",
    "alibi",
    "rope_relative",
    "phasewrap_bias",
    "phasewrap_adapter",
)
STAGE10_METHOD_ALIASES = {"rope_relative": "rope"}
PROMOTION_MIN_TOP1 = 0.50


def _stage10_method_name(method_name: str) -> str:
    return STAGE10_METHOD_ALIASES.get(method_name, method_name)


def _bootstrap_ci(values: list[float], *, seed_text: str, iterations: int = 400) -> dict[str, float]:
    rng = random.Random(int(hashlib.sha256(seed_text.encode("utf-8")).hexdigest()[:16], 16))
    means: list[float] = []
    for _ in range(iterations):
        sample = [values[rng.randrange(len(values))] for _ in range(len(values))]
        means.append(float(sum(sample) / len(sample)))
    means.sort()
    return {"low": round(means[int(0.025 * (iterations - 1))], 6), "high": round(means[int(0.975 * (iterations - 1))], 6)}


def _claim_boundary() -> dict[str, list[str]]:
    return {
        "supported": [
            "A no-credential matched one-block decoder-only transformer gate after the Stage 44 compact plateau.",
            "Fair RoPE/ALiBI/sinusoidal/no-position/PhaseWrap comparisons under matched seeds, tasks, model shape, optimizer, epochs, and train-short/test-long splits.",
            "Preservation of both positive and negative downstream evidence through aggregate metrics, per-seed rows, and failed-run artifacts.",
        ],
        "excluded": [
            "production transformer superiority",
            "full transformer-scale validation",
            "a claim that PhaseWrap-RoPE replaces RoPE",
            "broad quantum advantage",
            "a claim that a one-block synthetic decoder gate is sufficient for promotion",
        ],
    }


def build_blocked_result(*, reason: str = "missing_optional_autograd_dependency") -> dict[str, Any]:
    return {
        "schema_version": STAGE45_SCHEMA_VERSION,
        "stage": "stage45_matched_decoder_only_gate",
        "status": "blocked",
        "blocked_reason": reason,
        "install_command": "python -m pip install -e \".[transformer]\"",
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "method_names": list(METHOD_NAMES),
        "tasks": list(TASK_NAMES),
        "seeds": list(DEFAULT_SEEDS),
        "claim_boundary": _claim_boundary(),
    }


def _aggregate(per_seed_table: list[dict[str, Any]], failed_runs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    aggregate_table: list[dict[str, Any]] = []
    for task_name in TASK_NAMES:
        for method_name in METHOD_NAMES:
            rows = [row for row in per_seed_table if row["task"] == task_name and row["method"] == method_name]
            if not rows:
                continue
            record: dict[str, Any] = {
                "task": task_name,
                "method": method_name,
                "seed_count": len(rows),
                "failed_run_count": len([run for run in failed_runs if run["task"] == task_name and run["method"] == method_name]),
            }
            for metric_name in (
                "validation_loss",
                "test_loss",
                "test_perplexity",
                "test_top1_accuracy",
                "test_mrr",
                "test_mean_target_probability",
                "test_target_probability_mae",
                "test_mean_top1_confidence",
                "test_expected_calibration_error",
                "final_training_loss",
            ):
                values = [float(row[metric_name]) for row in rows]
                ci = _bootstrap_ci(values, seed_text=f"stage45:{task_name}:{method_name}:{metric_name}")
                record[f"{metric_name}_mean"] = round(float(np.mean(values)), 6)
                record[f"{metric_name}_ci_low"] = ci["low"]
                record[f"{metric_name}_ci_high"] = ci["high"]
            aggregate_table.append(record)
    return aggregate_table


def _rank_table(aggregate_table: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        aggregate_table,
        key=lambda row: (
            row["task"],
            row["test_mrr_mean"],
            row["test_top1_accuracy_mean"],
            row["test_mean_target_probability_mean"],
            -row["test_loss_mean"],
            row["method"],
        ),
        reverse=True,
    )


def _gate_decision(aggregate_table: list[dict[str, Any]]) -> dict[str, Any]:
    best_by_task = {
        task_name: sorted(
            [row for row in aggregate_table if row["task"] == task_name],
            key=lambda row: (
                row["test_mrr_mean"],
                row["test_top1_accuracy_mean"],
                row["test_mean_target_probability_mean"],
                -row["test_loss_mean"],
                row["method"],
            ),
            reverse=True,
        )[0]
        for task_name in TASK_NAMES
    }
    phasewrap_best_tasks = [
        task_name
        for task_name, row in best_by_task.items()
        if row["method"].startswith("phasewrap") and row["test_top1_accuracy_mean"] >= PROMOTION_MIN_TOP1
    ]
    rope_best_tasks = [task_name for task_name, row in best_by_task.items() if row["method"] == "rope_relative"]
    high_confidence_tasks = [
        task_name for task_name, row in best_by_task.items() if row["test_top1_accuracy_mean"] >= PROMOTION_MIN_TOP1
    ]
    promotes = len(phasewrap_best_tasks) > 0 and len(phasewrap_best_tasks) == len(high_confidence_tasks)
    return {
        "decision": "PROMOTION_NOT_SUPPORTED" if not promotes else "PROMOTION_CANDIDATE_REQUIRES_REPLICATION",
        "promotion_min_top1": PROMOTION_MIN_TOP1,
        "best_method_by_task": {task_name: row["method"] for task_name, row in best_by_task.items()},
        "best_top1_by_task": {task_name: row["test_top1_accuracy_mean"] for task_name, row in best_by_task.items()},
        "phasewrap_best_tasks_above_threshold": phasewrap_best_tasks,
        "rope_best_tasks": rope_best_tasks,
        "high_confidence_tasks": high_confidence_tasks,
        "claim_boundary": (
            "This matched one-block decoder-only gate does not promote PhaseWrap-RoPE beyond the bounded claim."
            if not promotes
            else "This matched one-block decoder-only gate would justify replication, not a replacement claim by itself."
        ),
    }


def run_stage45_gate(
    *,
    seeds: tuple[int, ...] = DEFAULT_SEEDS,
    examples_per_length: int = EXAMPLES_PER_LENGTH,
    epochs: int = DEFAULT_EPOCHS,
    method_names: tuple[str, ...] = METHOD_NAMES,
) -> dict[str, Any]:
    if not autograd_available():
        return build_blocked_result()
    splits_by_task = make_stage10_splits(seeds=seeds, examples_per_length=examples_per_length)
    per_seed_table: list[dict[str, Any]] = []
    failed_runs: list[dict[str, Any]] = []
    for task_name, splits in splits_by_task.items():
        for seed in seeds:
            train_rows = [row for row in splits["train"] if row.seed == seed]
            validation_rows = [row for row in splits["validation"] if row.seed == seed]
            test_rows = [row for row in splits["test"] if row.seed == seed]
            for method_name in method_names:
                try:
                    stage10_method = _stage10_method_name(method_name)
                    trained = train_small_decoder(train_rows, stage10_method, seed=seed, epochs=epochs)
                    validation_metrics = evaluate_small_decoder(validation_rows, stage10_method, trained["weights"])
                    test_metrics = evaluate_small_decoder(test_rows, stage10_method, trained["weights"])
                    per_seed_table.append(
                        {
                            "task": task_name,
                            "seed": seed,
                            "method": method_name,
                            "stage10_method_alias": stage10_method,
                            "epochs": epochs,
                            "train_row_count": len(train_rows),
                            "validation_loss": validation_metrics["loss"],
                            "test_loss": test_metrics["loss"],
                            "test_perplexity": test_metrics["perplexity"],
                            "test_top1_accuracy": test_metrics["top1_accuracy"],
                            "test_mrr": test_metrics["mrr"],
                            "test_mean_target_probability": test_metrics["mean_target_probability"],
                            "test_target_probability_mae": test_metrics["target_probability_mae"],
                            "test_mean_top1_confidence": test_metrics["mean_top1_confidence"],
                            "test_expected_calibration_error": test_metrics["expected_calibration_error"],
                            "final_training_loss": trained["final_training_loss"],
                            "training_history": trained["training_history"],
                        }
                    )
                except Exception as exc:  # pragma: no cover - retained for evidence completeness.
                    failed_runs.append({"task": task_name, "seed": seed, "method": method_name, "error": str(exc)})
    aggregate_table = _aggregate(per_seed_table, failed_runs)
    ranking_table = _rank_table(aggregate_table)
    gate_decision = _gate_decision(aggregate_table)
    return {
        "schema_version": STAGE45_SCHEMA_VERSION,
        "stage": "stage45_matched_decoder_only_gate",
        "status": "completed",
        "dataset": "synthetic_small_decoder_train_short_test_long_v1",
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "source_model": "stage10_small_decoder_transformer one-block decoder-only attention",
        "method_names": list(method_names),
        "tasks": list(TASK_NAMES),
        "seeds": list(seeds),
        "train_lengths": list(TRAIN_LENGTHS),
        "validation_lengths": list(VALIDATION_LENGTHS),
        "test_lengths": list(TEST_LENGTHS),
        "examples_per_length": examples_per_length,
        "epochs": epochs,
        "model": {
            "type": "matched_one_block_decoder_only_single_head_attention",
            "trained_components": "token embeddings, q/k/v projections, output projection, positional scale",
            "fair_comparison_controls": [
                "same train/validation/test rows",
                "same seeds",
                "same optimizer and epoch count",
                "same model shape and trainable parameterization",
                "same metrics and artifact retention",
            ],
        },
        "claim_boundary": _claim_boundary(),
        "splits": {
            task_name: {
                split: {"row_count": len(rows), "lengths": sorted({row.sequence_length for row in rows})}
                for split, rows in splits.items()
            }
            for task_name, splits in splits_by_task.items()
        },
        "failed_runs": failed_runs,
        "per_seed_table": per_seed_table,
        "aggregate_table": aggregate_table,
        "ranking_table": ranking_table,
        "gate_decision": gate_decision,
    }


def write_stage45_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    result_name = "results.json" if result["status"] == "completed" else "preflight.json"
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "no_hardware_submission": result["no_hardware_submission"],
        "provider_credentials_required": result["provider_credentials_required"],
        "method_names": result["method_names"],
        "tasks": result["tasks"],
        "result_path": str((output_dir / result_name).as_posix()),
        "summary_csv_path": str((output_dir / "summary.csv").as_posix()),
        "per_seed_csv_path": str((output_dir / "per_seed_results.csv").as_posix()) if result["status"] == "completed" else None,
        "failed_runs_path": str((output_dir / "failed_runs.json").as_posix()) if result["status"] == "completed" else None,
        "gate_decision": result.get("gate_decision"),
        "claim_boundary": result.get("claim_boundary", {}),
    }
    paths = {"manifest": str(output_dir / "manifest.json"), "result": str(output_dir / result_name), "summary_csv": str(output_dir / "summary.csv")}
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / result_name).write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    if result["status"] != "completed":
        with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=("stage", "status", "blocked_reason", "install_command"))
            writer.writeheader()
            writer.writerow({"stage": result["stage"], "status": result["status"], "blocked_reason": result.get("blocked_reason", ""), "install_command": result.get("install_command", "")})
        return paths
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(result["aggregate_table"][0].keys()))
        writer.writeheader()
        writer.writerows(result["aggregate_table"])
    per_seed_rows = [{key: value for key, value in row.items() if key != "training_history"} for row in result["per_seed_table"]]
    with (output_dir / "per_seed_results.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(per_seed_rows[0].keys()))
        writer.writeheader()
        writer.writerows(per_seed_rows)
    (output_dir / "failed_runs.json").write_text(json.dumps(result["failed_runs"], indent=2, sort_keys=True), encoding="utf-8")
    paths["per_seed_csv"] = str(output_dir / "per_seed_results.csv")
    paths["failed_runs"] = str(output_dir / "failed_runs.json")
    return paths


def print_stage45_summary(result: dict[str, Any]) -> None:
    if result["status"] != "completed":
        print("stage | status | blocked_reason | install_command")
        print("--- | --- | --- | ---")
        print(" | ".join((result["stage"], result["status"], result.get("blocked_reason", ""), result.get("install_command", ""))))
        return
    columns = (
        "task",
        "method",
        "seed_count",
        "failed_run_count",
        "test_top1_accuracy_mean",
        "test_mrr_mean",
        "test_mean_target_probability_mean",
        "test_expected_calibration_error_mean",
    )
    print(" | ".join(columns))
    print(" | ".join("---" for _ in columns))
    for row in result["ranking_table"]:
        print(" | ".join(str(row[column]) for column in columns))
    print(f"decision: {result['gate_decision']['decision']}")
    print(f"claim_boundary: {result['gate_decision']['claim_boundary']}")
