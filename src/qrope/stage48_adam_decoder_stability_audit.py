from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .stage10_small_decoder_transformer import DEFAULT_SEEDS, TASK_NAMES
from .stage45_matched_decoder_only_gate import METHOD_NAMES
from .stage47_adam_decoder_generalization_audit import (
    DEFAULT_LEARNING_RATE,
    build_blocked_result as build_stage47_blocked_result,
    run_stage47_audit,
)


STAGE48_SCHEMA_VERSION = "qrope_stage48_adam_decoder_stability_audit_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage48_adam_decoder_stability_audit"
DEFAULT_STABILITY_SEEDS = DEFAULT_SEEDS
DEFAULT_EXAMPLES_PER_LENGTH = 2
DEFAULT_EPOCHS = 180
TINY_TEXT_TASK = "tiny_text_fact_qa"
RETRIEVAL_TASKS = tuple(task for task in TASK_NAMES if task != TINY_TEXT_TASK)


def _claim_boundary() -> dict[str, list[str]]:
    return {
        "supported": [
            "A multi-seed stability audit for the Stage 47 Adam one-block decoder result.",
            "Preservation of tiny text-fact QA positives and retrieval-generalization failures under the same fair method set.",
            "Evidence about whether the one-seed PhaseWrap tiny text-fact QA lead is stable across seeds.",
        ],
        "excluded": [
            "production transformer superiority",
            "full transformer-scale validation",
            "a claim that PhaseWrap-RoPE replaces RoPE",
            "a claim that a one-seed tiny text-fact QA lead is stable without multi-seed support",
            "broad quantum advantage",
        ],
    }


def build_blocked_result(*, reason: str = "missing_optional_autograd_dependency") -> dict[str, Any]:
    blocked = build_stage47_blocked_result(reason=reason)
    blocked["schema_version"] = STAGE48_SCHEMA_VERSION
    blocked["stage"] = "stage48_adam_decoder_stability_audit"
    blocked["claim_boundary"] = _claim_boundary()
    return blocked


def _best_row(rows: list[dict[str, Any]], *, task_name: str, split: str) -> dict[str, Any]:
    task_rows = [row for row in rows if row["task"] == task_name]
    return sorted(
        task_rows,
        key=lambda row: (
            row[f"{split}_top1_accuracy_mean"],
            row[f"{split}_mrr_mean"],
            row[f"{split}_mean_target_probability_mean"],
            -row[f"{split}_loss_mean"],
            row["method"],
        ),
        reverse=True,
    )[0]


def _decision(stage47_result: dict[str, Any]) -> dict[str, Any]:
    if stage47_result["status"] != "completed":
        return {
            "decision": "BLOCKED",
            "claim_boundary": "Stage 48 could not run because the Stage 47 dependency is blocked.",
        }
    rows = stage47_result["aggregate_table"]
    tiny_best = _best_row(rows, task_name=TINY_TEXT_TASK, split="test")
    retrieval_best = {task: _best_row(rows, task_name=task, split="test") for task in RETRIEVAL_TASKS}
    retrieval_generalizes = {
        task: row["test_top1_accuracy_mean"] > 0.0 for task, row in retrieval_best.items()
    }
    phasewrap_tiny_best = tiny_best["method"].startswith("phasewrap")
    all_retrieval_failed = not any(retrieval_generalizes.values())
    if phasewrap_tiny_best and all_retrieval_failed:
        decision = "PHASEWRAP_TINY_QA_STABLE_RETRIEVAL_FAILED"
        boundary = "PhaseWrap keeps the tiny text-fact QA lead across seeds, but retrieval still fails."
    elif all_retrieval_failed:
        decision = "TINY_QA_POSITIVE_NOT_PHASEWRAP_STABLE_RETRIEVAL_FAILED"
        boundary = "Tiny text-fact QA remains positive, but the one-seed PhaseWrap lead is not stable and retrieval still fails."
    else:
        decision = "RETRIEVAL_GENERALIZATION_PRESENT_REVIEW_REQUIRED"
        boundary = "At least one retrieval task generalizes; review positional ordering before updating claims."
    return {
        "decision": decision,
        "tiny_text_best_method": tiny_best["method"],
        "tiny_text_best_top1": tiny_best["test_top1_accuracy_mean"],
        "tiny_text_best_mrr": tiny_best["test_mrr_mean"],
        "tiny_text_best_target_probability": tiny_best["test_mean_target_probability_mean"],
        "phasewrap_tiny_text_best": phasewrap_tiny_best,
        "retrieval_best_methods": {task: row["method"] for task, row in retrieval_best.items()},
        "retrieval_best_top1": {task: row["test_top1_accuracy_mean"] for task, row in retrieval_best.items()},
        "retrieval_generalizes": retrieval_generalizes,
        "all_retrieval_failed": all_retrieval_failed,
        "claim_boundary": boundary,
    }


def run_stage48_audit(
    *,
    seeds: tuple[int, ...] = DEFAULT_STABILITY_SEEDS,
    examples_per_length: int = DEFAULT_EXAMPLES_PER_LENGTH,
    epochs: int = DEFAULT_EPOCHS,
    learning_rate: float = DEFAULT_LEARNING_RATE,
    method_names: tuple[str, ...] = METHOD_NAMES,
) -> dict[str, Any]:
    stage47_result = run_stage47_audit(
        seeds=seeds,
        examples_per_length=examples_per_length,
        epochs=epochs,
        learning_rate=learning_rate,
        method_names=method_names,
    )
    if stage47_result["status"] != "completed":
        return build_blocked_result(reason=stage47_result.get("blocked_reason", "stage47_blocked"))
    return {
        "schema_version": STAGE48_SCHEMA_VERSION,
        "stage": "stage48_adam_decoder_stability_audit",
        "status": "completed",
        "dataset": stage47_result["dataset"],
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "source_stage": "stage47_adam_decoder_generalization_audit",
        "method_names": list(method_names),
        "tasks": list(TASK_NAMES),
        "seeds": list(seeds),
        "examples_per_length": examples_per_length,
        "epochs": epochs,
        "learning_rate": learning_rate,
        "claim_boundary": _claim_boundary(),
        "stage47_decision": stage47_result["decision"],
        "failed_runs": stage47_result["failed_runs"],
        "run_table": stage47_result["run_table"],
        "aggregate_table": stage47_result["aggregate_table"],
        "ranking_table": stage47_result["ranking_table"],
        "decision": _decision(stage47_result),
    }


def write_stage48_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
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


def print_stage48_summary(result: dict[str, Any]) -> None:
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
    )
    print(" | ".join(columns))
    print(" | ".join("---" for _ in columns))
    for row in result["ranking_table"]:
        print(" | ".join(str(row[column]) for column in columns))
    print(f"decision: {result['decision']['decision']}")
    print(f"claim_boundary: {result['decision']['claim_boundary']}")
