from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .stage45_matched_decoder_only_gate import METHOD_NAMES
from .stage52_two_block_decoder_feasibility_audit import GENERALIZATION_TOP1_THRESHOLD, RETRIEVAL_TASKS
from .stage61_support_complete_two_block_audit import DEFAULT_AUDIT_SEEDS, DEFAULT_EXAMPLES_PER_LENGTH
from .stage84_support_auxiliary_pointer_generator_audit import DEFAULT_SUPPORT_AUX_WEIGHT
from .stage85_dual_auxiliary_pointer_generator_audit import (
    DEFAULT_LEARNING_RATE,
    DEFAULT_TARGET_ATTENTION_AUX_WEIGHT,
    build_blocked_result as build_stage85_blocked_result,
    run_stage85_audit,
)


STAGE86_SCHEMA_VERSION = "qrope_stage86_dual_auxiliary_budget_sensitivity_audit_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage86_dual_auxiliary_budget_sensitivity_audit"
DEFAULT_EPOCH_BUDGETS = (10, 20)


def _claim_boundary() -> dict[str, list[str]]:
    return {
        "supported": [
            "A no-credential budget-sensitivity audit for the Stage 85 dual-auxiliary pointer-generator path.",
            "Evidence about whether Stage 85's below-threshold exact-offset result is explained by a short training budget.",
            "Fair RoPE/ALiBI/sinusoidal/no-position/PhaseWrap comparisons with failed-run retention.",
        ],
        "excluded": [
            "production transformer superiority",
            "full transformer-scale validation",
            "a claim that PhaseWrap-RoPE replaces RoPE",
            "a claim that budget tuning alone establishes positional-method promotion",
            "a claim that auxiliary-supervised diagnostics are standard free decoder-only language modeling",
            "broad quantum advantage",
        ],
    }


def build_blocked_result(*, reason: str = "missing_optional_autograd_dependency") -> dict[str, Any]:
    result = build_stage85_blocked_result(reason=reason)
    result.update(
        {
            "schema_version": STAGE86_SCHEMA_VERSION,
            "stage": "stage86_dual_auxiliary_budget_sensitivity_audit",
            "source_stage": "stage85_dual_auxiliary_pointer_generator_audit",
            "epoch_budgets": list(DEFAULT_EPOCH_BUDGETS),
            "claim_boundary": _claim_boundary(),
        }
    )
    return result


def _budget_summary(result: dict[str, Any]) -> dict[str, Any]:
    decision = result["decision"]
    return {
        "epochs": result["epochs"],
        "status": result["status"],
        "decision": decision["decision"],
        "claim_boundary": decision["claim_boundary"],
        "capacity_established": decision["capacity_established"],
        "best_train_top1": decision["best_train_top1"],
        "retrieval_best_methods": decision["retrieval_best_methods"],
        "retrieval_best_top1": decision["retrieval_best_top1"],
        "retrieval_best_target_probability": {
            task: max(
                row["test_mean_target_probability_mean"]
                for row in result["aggregate_table"]
                if row["task"] == task
            )
            for task in RETRIEVAL_TASKS
        },
        "tiny_text_best_method": decision["tiny_text_best_method"],
        "tiny_text_best_top1": decision["tiny_text_best_top1"],
        "phase_cued_best_support_accuracy": decision["phase_cued_best_support_accuracy"],
        "retrieval_attention_repaired_tasks": decision["retrieval_attention_repaired_tasks"],
        "generalized_original_retrieval_tasks": decision["generalized_original_retrieval_tasks"],
        "failed_run_count": len(result["failed_runs"]),
        "aggregate_table": result["aggregate_table"],
        "failed_runs": result["failed_runs"],
    }


def _decision(budget_summaries: list[dict[str, Any]]) -> dict[str, Any]:
    best_by_task: dict[str, dict[str, Any]] = {}
    for task in RETRIEVAL_TASKS:
        candidates = [
            {
                "epochs": summary["epochs"],
                "method": summary["retrieval_best_methods"][task],
                "top1": summary["retrieval_best_top1"][task],
                "target_probability": summary["retrieval_best_target_probability"][task],
            }
            for summary in budget_summaries
        ]
        best_by_task[task] = sorted(candidates, key=lambda row: (row["top1"], row["target_probability"], row["epochs"], row["method"]), reverse=True)[0]
    generalized = [task for task, row in best_by_task.items() if row["top1"] >= GENERALIZATION_TOP1_THRESHOLD]
    phasewrap_generalized = [task for task in generalized if str(best_by_task[task]["method"]).startswith("phasewrap")]
    capacity_established = any(bool(summary["capacity_established"]) for summary in budget_summaries)
    if not capacity_established:
        decision = "DUAL_AUXILIARY_BUDGET_CAPACITY_NOT_ESTABLISHED"
        boundary = "The tested dual-auxiliary training budgets do not establish train capacity."
    elif all(task in generalized for task in RETRIEVAL_TASKS):
        decision = "DUAL_AUXILIARY_BUDGET_RETRIEVAL_REVIEW_REQUIRED"
        boundary = "At least one dual-auxiliary budget crosses both retrieval thresholds; review method ordering before any claim update."
    elif generalized:
        decision = "DUAL_AUXILIARY_BUDGET_PARTIAL_RETRIEVAL"
        boundary = "A longer dual-auxiliary budget crosses at least one retrieval threshold but not the full retrieval gate."
    else:
        decision = "DUAL_AUXILIARY_BUDGET_WITHOUT_RETRIEVAL_GENERALIZATION"
        boundary = "Increasing the practical dual-auxiliary budget does not repair held-out retrieval generalization."
    return {
        "decision": decision,
        "claim_boundary": boundary,
        "generalization_top1_threshold": GENERALIZATION_TOP1_THRESHOLD,
        "capacity_established": capacity_established,
        "best_retrieval_by_task": best_by_task,
        "generalized_original_retrieval_tasks": generalized,
        "phasewrap_retrieval_generalized_tasks": phasewrap_generalized,
        "best_tiny_text_top1": max(summary["tiny_text_best_top1"] for summary in budget_summaries),
        "failed_run_count": sum(summary["failed_run_count"] for summary in budget_summaries),
    }


def run_stage86_audit(
    *,
    epoch_budgets: tuple[int, ...] = DEFAULT_EPOCH_BUDGETS,
    seeds: tuple[int, ...] = DEFAULT_AUDIT_SEEDS,
    examples_per_length: int = DEFAULT_EXAMPLES_PER_LENGTH,
    learning_rate: float = DEFAULT_LEARNING_RATE,
    support_aux_weight: float = DEFAULT_SUPPORT_AUX_WEIGHT,
    target_attention_aux_weight: float = DEFAULT_TARGET_ATTENTION_AUX_WEIGHT,
    method_names: tuple[str, ...] = METHOD_NAMES,
) -> dict[str, Any]:
    budget_summaries: list[dict[str, Any]] = []
    for epochs in epoch_budgets:
        result = run_stage85_audit(
            seeds=seeds,
            examples_per_length=examples_per_length,
            epochs=epochs,
            learning_rate=learning_rate,
            support_aux_weight=support_aux_weight,
            target_attention_aux_weight=target_attention_aux_weight,
            method_names=method_names,
        )
        if result["status"] == "blocked":
            blocked = build_blocked_result(reason=result.get("blocked_reason", "missing_optional_autograd_dependency"))
            blocked["epoch_budgets"] = list(epoch_budgets)
            return blocked
        budget_summaries.append(_budget_summary(result))
    return {
        "schema_version": STAGE86_SCHEMA_VERSION,
        "stage": "stage86_dual_auxiliary_budget_sensitivity_audit",
        "status": "completed",
        "dataset": "synthetic_stage10_support_complete_rows_multitask_dual_auxiliary_budget_sensitivity_v1",
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "source_stage": "stage85_dual_auxiliary_pointer_generator_audit",
        "method_names": list(method_names),
        "tasks": list(RETRIEVAL_TASKS) + ["tiny_text_fact_qa"],
        "seeds": list(seeds),
        "examples_per_length": examples_per_length,
        "epoch_budgets": list(epoch_budgets),
        "learning_rate": learning_rate,
        "support_aux_weight": support_aux_weight,
        "target_attention_aux_weight": target_attention_aux_weight,
        "claim_boundary": _claim_boundary(),
        "budget_summaries": budget_summaries,
        "decision": _decision(budget_summaries),
    }


def write_stage86_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
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
        "source_stage": result["source_stage"],
        "epoch_budgets": result["epoch_budgets"],
        "result_path": str((output_dir / result_name).as_posix()),
        "summary_csv_path": str((output_dir / "summary.csv").as_posix()),
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
    rows: list[dict[str, Any]] = []
    for summary in result["budget_summaries"]:
        for task in RETRIEVAL_TASKS:
            rows.append(
                {
                    "epochs": summary["epochs"],
                    "task": task,
                    "best_method": summary["retrieval_best_methods"][task],
                    "best_top1": summary["retrieval_best_top1"][task],
                    "best_target_probability": summary["retrieval_best_target_probability"][task],
                    "decision": summary["decision"],
                    "failed_run_count": summary["failed_run_count"],
                }
            )
        rows.append(
            {
                "epochs": summary["epochs"],
                "task": "tiny_text_fact_qa",
                "best_method": summary["tiny_text_best_method"],
                "best_top1": summary["tiny_text_best_top1"],
                "best_target_probability": "",
                "decision": summary["decision"],
                "failed_run_count": summary["failed_run_count"],
            }
        )
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return paths


def print_stage86_summary(result: dict[str, Any]) -> None:
    if result["status"] != "completed":
        print("stage | status | blocked_reason | install_command")
        print("--- | --- | --- | ---")
        print(" | ".join((result["stage"], result["status"], result.get("blocked_reason", ""), result.get("install_command", ""))))
        return
    columns = ("epochs", "task", "best_method", "best_top1", "best_target_probability", "failed_run_count")
    print(" | ".join(columns))
    print(" | ".join("---" for _ in columns))
    for summary in result["budget_summaries"]:
        for task in RETRIEVAL_TASKS:
            print(
                " | ".join(
                    str(value)
                    for value in (
                        summary["epochs"],
                        task,
                        summary["retrieval_best_methods"][task],
                        summary["retrieval_best_top1"][task],
                        summary["retrieval_best_target_probability"][task],
                        summary["failed_run_count"],
                    )
                )
            )
    print(f"decision: {result['decision']['decision']}")
    print(f"claim_boundary: {result['decision']['claim_boundary']}")
