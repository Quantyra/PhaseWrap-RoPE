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
    TASK_NAMES,
    TEST_LENGTHS,
    TRAIN_LENGTHS,
    VALIDATION_LENGTHS,
    _batch_loss,
    _init_vector,
    autograd_available,
    evaluate_small_decoder,
    make_stage10_splits,
)
from .stage45_matched_decoder_only_gate import METHOD_NAMES, _stage10_method_name


STAGE47_SCHEMA_VERSION = "qrope_stage47_adam_decoder_generalization_audit_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage47_adam_decoder_generalization_audit"
DEFAULT_AUDIT_SEEDS = (DEFAULT_SEEDS[0],)
DEFAULT_EXAMPLES_PER_LENGTH = 2
DEFAULT_EPOCHS = 300
DEFAULT_LEARNING_RATE = 0.03
CAPACITY_TRAIN_TOP1_THRESHOLD = 0.75
GENERALIZATION_TOP1_THRESHOLD = 0.50


def _bootstrap_ci(values: list[float], *, seed_text: str, iterations: int = 300) -> dict[str, float]:
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
            "A no-credential Adam optimizer audit for the matched one-block decoder-only gate.",
            "Evidence that optimizer hardening can establish train fit on the current one-block harness.",
            "Separated train/validation/test metrics showing whether train fit generalizes under the fair positional comparison.",
        ],
        "excluded": [
            "production transformer superiority",
            "full transformer-scale validation",
            "a claim that PhaseWrap-RoPE replaces RoPE",
            "a claim that train fit alone is promotion evidence",
            "broad quantum advantage",
        ],
    }


def build_blocked_result(*, reason: str = "missing_optional_autograd_dependency") -> dict[str, Any]:
    return {
        "schema_version": STAGE47_SCHEMA_VERSION,
        "stage": "stage47_adam_decoder_generalization_audit",
        "status": "blocked",
        "blocked_reason": reason,
        "install_command": "python -m pip install -e \".[transformer]\"",
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "method_names": list(METHOD_NAMES),
        "tasks": list(TASK_NAMES),
        "seeds": list(DEFAULT_AUDIT_SEEDS),
        "claim_boundary": _claim_boundary(),
    }


def train_adam_decoder(
    rows: list[Any],
    method_name: str,
    *,
    seed: int,
    epochs: int = DEFAULT_EPOCHS,
    learning_rate: float = DEFAULT_LEARNING_RATE,
) -> dict[str, Any]:
    from autograd import grad

    vector = _init_vector(seed)
    gradient = grad(lambda current: _batch_loss(current, rows, method_name))
    moment = np.zeros_like(vector)
    velocity = np.zeros_like(vector)
    beta1 = 0.9
    beta2 = 0.999
    epsilon = 1e-8
    history: list[dict[str, float]] = []
    for epoch in range(1, epochs + 1):
        loss_value = float(_batch_loss(vector, rows, method_name))
        grad_value = gradient(vector)
        moment = beta1 * moment + (1.0 - beta1) * grad_value
        velocity = beta2 * velocity + (1.0 - beta2) * (grad_value * grad_value)
        moment_hat = moment / (1.0 - beta1**epoch)
        velocity_hat = velocity / (1.0 - beta2**epoch)
        vector = vector - learning_rate * moment_hat / (np.sqrt(velocity_hat) + epsilon)
        if epoch in {1, epochs // 4, epochs // 2, (3 * epochs) // 4, epochs}:
            history.append({"epoch": epoch, "loss": round(loss_value, 6)})
    return {
        "weights": vector,
        "optimizer": "full_batch_adam",
        "epochs": epochs,
        "learning_rate": learning_rate,
        "training_history": history,
        "final_training_loss": history[-1]["loss"],
    }


def _metric_names(split: str) -> tuple[str, ...]:
    return (
        f"{split}_loss",
        f"{split}_perplexity",
        f"{split}_top1_accuracy",
        f"{split}_mrr",
        f"{split}_mean_target_probability",
        f"{split}_expected_calibration_error",
    )


def _aggregate(run_table: list[dict[str, Any]], failed_runs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    aggregate_table: list[dict[str, Any]] = []
    for task_name in TASK_NAMES:
        for method_name in METHOD_NAMES:
            rows = [row for row in run_table if row["task"] == task_name and row["method"] == method_name]
            if not rows:
                continue
            record: dict[str, Any] = {
                "task": task_name,
                "method": method_name,
                "seed_count": len(rows),
                "failed_run_count": len([run for run in failed_runs if run["task"] == task_name and run["method"] == method_name]),
            }
            for metric_name in _metric_names("train") + _metric_names("validation") + _metric_names("test") + ("final_training_loss",):
                values = [float(row[metric_name]) for row in rows]
                ci = _bootstrap_ci(values, seed_text=f"stage47:{task_name}:{method_name}:{metric_name}")
                record[f"{metric_name}_mean"] = round(float(np.mean(values)), 6)
                record[f"{metric_name}_ci_low"] = ci["low"]
                record[f"{metric_name}_ci_high"] = ci["high"]
            aggregate_table.append(record)
    return aggregate_table


def _best_row(rows: list[dict[str, Any]], split: str) -> dict[str, Any]:
    return sorted(
        rows,
        key=lambda row: (
            row[f"{split}_top1_accuracy_mean"],
            row[f"{split}_mrr_mean"],
            row[f"{split}_mean_target_probability_mean"],
            -row[f"{split}_loss_mean"],
            row["method"],
        ),
        reverse=True,
    )[0]


def _decision(aggregate_table: list[dict[str, Any]]) -> dict[str, Any]:
    best_train = _best_row(aggregate_table, "train")
    best_validation = _best_row(aggregate_table, "validation")
    best_test = _best_row(aggregate_table, "test")
    best_by_task = {
        task_name: {
            "validation": _best_row([row for row in aggregate_table if row["task"] == task_name], "validation"),
            "test": _best_row([row for row in aggregate_table if row["task"] == task_name], "test"),
        }
        for task_name in TASK_NAMES
    }
    capacity_established = best_train["train_top1_accuracy_mean"] >= CAPACITY_TRAIN_TOP1_THRESHOLD
    generalization_task_names = [
        task_name
        for task_name, split_rows in best_by_task.items()
        if split_rows["validation"]["validation_top1_accuracy_mean"] >= GENERALIZATION_TOP1_THRESHOLD
        and split_rows["test"]["test_top1_accuracy_mean"] >= GENERALIZATION_TOP1_THRESHOLD
    ]
    retrieval_task_names = [task_name for task_name in TASK_NAMES if task_name != "tiny_text_fact_qa"]
    retrieval_generalization_task_names = [
        task_name for task_name in generalization_task_names if task_name in retrieval_task_names
    ]
    all_tasks_generalize = len(generalization_task_names) == len(TASK_NAMES)
    all_retrieval_tasks_generalize = len(retrieval_generalization_task_names) == len(retrieval_task_names)
    any_task_generalizes = len(generalization_task_names) > 0
    phasewrap_generalization_task_names = [
        task_name
        for task_name in generalization_task_names
        if best_by_task[task_name]["test"]["method"].startswith("phasewrap")
    ]
    generalization_established = (
        all_tasks_generalize and all_retrieval_tasks_generalize
    )
    if not capacity_established:
        decision = "CAPACITY_NOT_ESTABLISHED"
        boundary = "Adam hardening still does not fit the one-block decoder training rows well enough for promotion."
    elif not generalization_established:
        decision = "TRAIN_FIT_WITH_PARTIAL_GENERALIZATION" if any_task_generalizes else "TRAIN_FIT_WITHOUT_GENERALIZATION"
        boundary = "Adam hardening establishes train fit, but generalization is incomplete across retrieval tasks, so positional-method promotion remains unsupported."
    else:
        decision = "GENERALIZATION_READY_FOR_POSITIONAL_COMPARISON"
        boundary = "The harness generalizes enough to support cautious positional-method interpretation."
    return {
        "decision": decision,
        "capacity_train_top1_threshold": CAPACITY_TRAIN_TOP1_THRESHOLD,
        "generalization_top1_threshold": GENERALIZATION_TOP1_THRESHOLD,
        "best_train_task": best_train["task"],
        "best_train_method": best_train["method"],
        "best_train_top1": best_train["train_top1_accuracy_mean"],
        "best_validation_task": best_validation["task"],
        "best_validation_method": best_validation["method"],
        "best_validation_top1": best_validation["validation_top1_accuracy_mean"],
        "best_test_task": best_test["task"],
        "best_test_method": best_test["method"],
        "best_test_top1": best_test["test_top1_accuracy_mean"],
        "generalization_task_names": generalization_task_names,
        "retrieval_generalization_task_names": retrieval_generalization_task_names,
        "phasewrap_generalization_task_names": phasewrap_generalization_task_names,
        "all_tasks_generalize": all_tasks_generalize,
        "all_retrieval_tasks_generalize": all_retrieval_tasks_generalize,
        "claim_boundary": boundary,
    }


def run_stage47_audit(
    *,
    seeds: tuple[int, ...] = DEFAULT_AUDIT_SEEDS,
    examples_per_length: int = DEFAULT_EXAMPLES_PER_LENGTH,
    epochs: int = DEFAULT_EPOCHS,
    learning_rate: float = DEFAULT_LEARNING_RATE,
    method_names: tuple[str, ...] = METHOD_NAMES,
) -> dict[str, Any]:
    if not autograd_available():
        return build_blocked_result()
    splits_by_task = make_stage10_splits(seeds=seeds, examples_per_length=examples_per_length)
    run_table: list[dict[str, Any]] = []
    failed_runs: list[dict[str, Any]] = []
    for task_name, splits in splits_by_task.items():
        for seed in seeds:
            train_rows = [row for row in splits["train"] if row.seed == seed]
            validation_rows = [row for row in splits["validation"] if row.seed == seed]
            test_rows = [row for row in splits["test"] if row.seed == seed]
            for method_name in method_names:
                try:
                    stage10_method = _stage10_method_name(method_name)
                    trained = train_adam_decoder(
                        train_rows,
                        stage10_method,
                        seed=seed,
                        epochs=epochs,
                        learning_rate=learning_rate,
                    )
                    train_metrics = evaluate_small_decoder(train_rows, stage10_method, trained["weights"])
                    validation_metrics = evaluate_small_decoder(validation_rows, stage10_method, trained["weights"])
                    test_metrics = evaluate_small_decoder(test_rows, stage10_method, trained["weights"])
                    row: dict[str, Any] = {
                        "task": task_name,
                        "seed": seed,
                        "method": method_name,
                        "stage10_method_alias": stage10_method,
                        "epochs": epochs,
                        "learning_rate": learning_rate,
                        "optimizer": trained["optimizer"],
                        "train_row_count": len(train_rows),
                        "validation_row_count": len(validation_rows),
                        "test_row_count": len(test_rows),
                        "final_training_loss": trained["final_training_loss"],
                        "training_history": trained["training_history"],
                    }
                    for split_name, metrics in (("train", train_metrics), ("validation", validation_metrics), ("test", test_metrics)):
                        row[f"{split_name}_loss"] = metrics["loss"]
                        row[f"{split_name}_perplexity"] = metrics["perplexity"]
                        row[f"{split_name}_top1_accuracy"] = metrics["top1_accuracy"]
                        row[f"{split_name}_mrr"] = metrics["mrr"]
                        row[f"{split_name}_mean_target_probability"] = metrics["mean_target_probability"]
                        row[f"{split_name}_expected_calibration_error"] = metrics["expected_calibration_error"]
                    run_table.append(row)
                except Exception as exc:  # pragma: no cover - retained for artifact completeness.
                    failed_runs.append({"task": task_name, "seed": seed, "method": method_name, "error": str(exc)})
    aggregate_table = _aggregate(run_table, failed_runs)
    ranking_table = sorted(
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
    return {
        "schema_version": STAGE47_SCHEMA_VERSION,
        "stage": "stage47_adam_decoder_generalization_audit",
        "status": "completed",
        "dataset": "synthetic_small_decoder_train_short_test_long_v1",
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "source_model": "stage10/stage45 one-block decoder-only attention with Adam optimizer",
        "method_names": list(method_names),
        "tasks": list(TASK_NAMES),
        "seeds": list(seeds),
        "train_lengths": list(TRAIN_LENGTHS),
        "validation_lengths": list(VALIDATION_LENGTHS),
        "test_lengths": list(TEST_LENGTHS),
        "examples_per_length": examples_per_length,
        "epochs": epochs,
        "learning_rate": learning_rate,
        "claim_boundary": _claim_boundary(),
        "failed_runs": failed_runs,
        "run_table": run_table,
        "aggregate_table": aggregate_table,
        "ranking_table": ranking_table,
        "decision": _decision(aggregate_table),
    }


def write_stage47_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
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
        "per_run_csv_path": str((output_dir / "per_run_results.csv").as_posix()) if result["status"] == "completed" else None,
        "failed_runs_path": str((output_dir / "failed_runs.json").as_posix()) if result["status"] == "completed" else None,
        "decision": result.get("decision"),
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
    per_run_rows = [{key: value for key, value in row.items() if key != "training_history"} for row in result["run_table"]]
    with (output_dir / "per_run_results.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(per_run_rows[0].keys()))
        writer.writeheader()
        writer.writerows(per_run_rows)
    (output_dir / "failed_runs.json").write_text(json.dumps(result["failed_runs"], indent=2, sort_keys=True), encoding="utf-8")
    paths["per_run_csv"] = str(output_dir / "per_run_results.csv")
    paths["failed_runs"] = str(output_dir / "failed_runs.json")
    return paths


def print_stage47_summary(result: dict[str, Any]) -> None:
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
        "train_top1_accuracy_mean",
        "validation_top1_accuracy_mean",
        "test_top1_accuracy_mean",
        "test_mrr_mean",
        "test_mean_target_probability_mean",
    )
    print(" | ".join(columns))
    print(" | ".join("---" for _ in columns))
    for row in result["ranking_table"]:
        print(" | ".join(str(row[column]) for column in columns))
    print(f"decision: {result['decision']['decision']}")
    print(f"claim_boundary: {result['decision']['claim_boundary']}")
