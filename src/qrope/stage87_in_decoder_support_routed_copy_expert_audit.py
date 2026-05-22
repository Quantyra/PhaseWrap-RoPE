from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np

from .stage10_small_decoder_transformer import TASK_NAMES, TEST_LENGTHS, TRAIN_LENGTHS, VALIDATION_LENGTHS, Stage10Example, _expected_calibration_error, autograd_available, make_stage10_splits
from .stage45_matched_decoder_only_gate import METHOD_NAMES, _stage10_method_name
from .stage50_learned_pointer_generator_decoder_audit import _copy_indicator
from .stage52_two_block_decoder_feasibility_audit import CAPACITY_TRAIN_TOP1_THRESHOLD, DEFAULT_LEARNING_RATE, GENERALIZATION_TOP1_THRESHOLD, RETRIEVAL_TASKS, TINY_TEXT_TASK, _decision as base_decision, write_stage52_outputs
from .stage54_attention_supervised_two_block_audit import _aggregate
from .stage61_support_complete_two_block_audit import DEFAULT_AUDIT_SEEDS, DEFAULT_EXAMPLES_PER_LENGTH
from .stage61_support_complete_two_block_audit import _support_coverage
from .stage61_support_complete_two_block_audit import build_blocked_result as build_stage61_blocked_result
from .stage61_support_complete_two_block_audit import print_stage61_summary
from .stage64_two_block_pointer_generator_capacity_audit import _add_copy_gate_aggregates
from .stage84_support_auxiliary_pointer_generator_audit import DEFAULT_SUPPORT_AUX_WEIGHT, _add_support_accuracy_aggregates, _support_index
from .stage85_dual_auxiliary_pointer_generator_audit import (
    DEFAULT_EPOCHS,
    DEFAULT_TARGET_ATTENTION_AUX_WEIGHT,
    _row_outputs,
    train_dual_auxiliary_pointer_generator_decoder,
)


STAGE87_SCHEMA_VERSION = "qrope_stage87_in_decoder_support_routed_copy_expert_audit_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage87_in_decoder_support_routed_copy_expert_audit"
DEFAULT_SUPPORT_ROUTE_WEIGHT = 1.0


def _claim_boundary() -> dict[str, list[str]]:
    return {
        "supported": [
            "A no-credential support-complete two-block pointer-generator audit with an in-decoder support-routed copy expert.",
            "Evidence about whether the Stage85 decoder's learned support probabilities can drive held-out token selection when a structural routing expert is provided.",
            "Fair RoPE/ALiBI/sinusoidal/no-position/PhaseWrap comparisons with failed-run retention.",
        ],
        "excluded": [
            "production transformer superiority",
            "full transformer-scale validation",
            "a claim that PhaseWrap-RoPE replaces RoPE",
            "a claim that a structural support-routed copy expert is standard free decoder-only language modeling",
            "a claim that support-routed expert success is positional-method promotion evidence when no-position also solves",
            "broad quantum advantage",
        ],
    }


def build_blocked_result(*, reason: str = "missing_optional_autograd_dependency") -> dict[str, Any]:
    result = build_stage61_blocked_result(reason=reason)
    result.update(
        {
            "schema_version": STAGE87_SCHEMA_VERSION,
            "stage": "stage87_in_decoder_support_routed_copy_expert_audit",
            "source_stage": "stage86_dual_auxiliary_budget_sensitivity_audit",
            "training_tasks": list(TASK_NAMES),
            "epochs": DEFAULT_EPOCHS,
            "support_aux_weight": DEFAULT_SUPPORT_AUX_WEIGHT,
            "target_attention_aux_weight": DEFAULT_TARGET_ATTENTION_AUX_WEIGHT,
            "support_route_weight": DEFAULT_SUPPORT_ROUTE_WEIGHT,
            "claim_boundary": _claim_boundary(),
        }
    )
    return result


def _soft_support_routed_probabilities(row: Stage10Example, support_classes: tuple[int, ...], support_probabilities: Any) -> np.ndarray:
    indicator = np.asarray(_copy_indicator(row), dtype=float)
    probabilities = np.zeros(indicator.shape[1], dtype=float)
    support_probs = np.asarray(support_probabilities, dtype=float)
    for class_index, reference_delta in enumerate(support_classes):
        predicted_delta = int(reference_delta)
        candidate_deltas = [delta for delta in range(predicted_delta, row.query_pos, 24) if delta >= 3]
        selected_delta = int(candidate_deltas[-1]) if candidate_deltas else predicted_delta
        selected_position = int(row.query_pos - selected_delta)
        if 0 <= selected_position < row.query_pos:
            probabilities += float(support_probs[class_index]) * indicator[selected_position]
    total = float(np.sum(probabilities))
    if total <= 0.0:
        probabilities += 1.0 / float(len(probabilities))
    else:
        probabilities = probabilities / total
    return probabilities


def _mixed_probabilities(vector: Any, row: Stage10Example, method_name: str, support_classes: tuple[int, ...], support_route_weight: float) -> tuple[np.ndarray, float, np.ndarray, float]:
    decoder_probabilities, copy_gate, support_probabilities, attention_1, attention_2 = _row_outputs(vector, row, method_name, len(support_classes))
    decoder_probs = np.asarray(decoder_probabilities, dtype=float)
    support_probs = np.asarray(support_probabilities, dtype=float)
    if row.task == "phase_cued_retrieval":
        routed_probs = _soft_support_routed_probabilities(row, support_classes, support_probs)
        probabilities = support_route_weight * routed_probs + (1.0 - support_route_weight) * decoder_probs
    else:
        probabilities = decoder_probs
    total = float(np.sum(probabilities))
    if total > 0.0:
        probabilities = probabilities / total
    target_attention = 0.5 * (float(attention_1[row.target_pos]) + float(attention_2[row.target_pos]))
    return probabilities, float(copy_gate), support_probs, target_attention


def _predict(vector: Any, row: Stage10Example, method_name: str, support_classes: tuple[int, ...], support_route_weight: float) -> tuple[float, int, float, float, int | None, float]:
    probabilities, copy_gate, support_probabilities, target_attention = _mixed_probabilities(vector, row, method_name, support_classes, support_route_weight)
    sorted_indices = sorted(range(len(probabilities)), key=lambda index: (-float(probabilities[index]), index))
    predicted_support = int(np.argmax(support_probabilities)) if row.task == "phase_cued_retrieval" else None
    return (
        float(probabilities[row.label_token]),
        int(sorted_indices.index(row.label_token) + 1),
        float(probabilities[sorted_indices[0]]),
        copy_gate,
        predicted_support,
        target_attention,
    )


def evaluate_in_decoder_support_routed_copy_expert(
    rows: list[Stage10Example],
    method_name: str,
    vector: Any,
    support_classes: tuple[int, ...],
    *,
    support_route_weight: float = DEFAULT_SUPPORT_ROUTE_WEIGHT,
) -> dict[str, float]:
    losses: list[float] = []
    reciprocal_ranks: list[float] = []
    top1_hits: list[float] = []
    target_probs: list[float] = []
    top1_confidences: list[float] = []
    copy_gates: list[float] = []
    support_hits: list[float] = []
    target_attentions: list[float] = []
    for row in rows:
        target_probability, rank, top1_confidence, copy_gate, predicted_support, target_attention = _predict(
            vector,
            row,
            method_name,
            support_classes,
            support_route_weight,
        )
        losses.append(-math.log(max(target_probability, 1e-12)))
        reciprocal_ranks.append(1.0 / float(rank))
        top1_hits.append(1.0 if rank == 1 else 0.0)
        target_probs.append(target_probability)
        top1_confidences.append(top1_confidence)
        copy_gates.append(copy_gate)
        target_attentions.append(target_attention)
        if row.task == "phase_cued_retrieval" and predicted_support is not None:
            support_index = _support_index(row, support_classes)
            support_hits.append(1.0 if support_index >= 0 and predicted_support == support_index else 0.0)
    mean_loss = float(np.mean(losses))
    return {
        "row_count": len(rows),
        "loss": round(mean_loss, 6),
        "perplexity": round(float(math.exp(mean_loss)), 6),
        "top1_accuracy": round(float(np.mean(top1_hits)), 6),
        "mrr": round(float(np.mean(reciprocal_ranks)), 6),
        "mean_target_probability": round(float(np.mean(target_probs)), 6),
        "mean_top1_confidence": round(float(np.mean(top1_confidences)), 6),
        "expected_calibration_error": round(_expected_calibration_error(top1_confidences, top1_hits), 6),
        "mean_copy_gate": round(float(np.mean(copy_gates)), 6),
        "support_accuracy": round(float(np.mean(support_hits)), 6) if support_hits else 1.0,
        "mean_target_attention": round(float(np.mean(target_attentions)), 6),
    }


def _best_row(rows: list[dict[str, Any]], *, task_name: str) -> dict[str, Any]:
    return sorted(
        [row for row in rows if row["task"] == task_name],
        key=lambda row: (
            row["test_top1_accuracy_mean"],
            row["test_mrr_mean"],
            row["test_mean_target_probability_mean"],
            row["method"],
        ),
        reverse=True,
    )[0]


def _decision(result: dict[str, Any]) -> dict[str, Any]:
    if result["status"] != "completed":
        return {}
    base = base_decision(result["aggregate_table"])
    retrieval_best = {task: _best_row(result["aggregate_table"], task_name=task) for task in RETRIEVAL_TASKS}
    retrieval_solved = [task for task, row in retrieval_best.items() if row["test_top1_accuracy_mean"] >= GENERALIZATION_TOP1_THRESHOLD]
    no_position_solved = [
        task
        for task in RETRIEVAL_TASKS
        for row in result["aggregate_table"]
        if row["task"] == task and row["method"] == "no_position" and row["test_top1_accuracy_mean"] >= GENERALIZATION_TOP1_THRESHOLD
    ]
    if not base["capacity_established"]:
        decision = "IN_DECODER_SUPPORT_ROUTED_COPY_EXPERT_CAPACITY_NOT_ESTABLISHED"
        boundary = "The support-routed copy expert path does not establish train capacity."
    elif "phase_cued_retrieval" in retrieval_solved and "phase_cued_retrieval" in no_position_solved:
        decision = "IN_DECODER_SUPPORT_ROUTED_COPY_EXPERT_SOLVES_PHASE_CUED_NOT_PROMOTION"
        boundary = "A structural support-routed copy expert repairs phase-cued retrieval for no-position too; this is mechanism evidence, not positional-method promotion."
    elif retrieval_solved:
        decision = "IN_DECODER_SUPPORT_ROUTED_COPY_EXPERT_PARTIAL_RETRIEVAL"
        boundary = "A structural support-routed copy expert repairs at least one retrieval lane but not the full retrieval gate."
    else:
        decision = "IN_DECODER_SUPPORT_ROUTED_COPY_EXPERT_WITHOUT_RETRIEVAL_GENERALIZATION"
        boundary = "A structural support-routed copy expert still does not repair held-out retrieval."
    return {
        **base,
        "decision": decision,
        "claim_boundary": boundary,
        "training_tasks": list(TASK_NAMES),
        "retrieval_solved_tasks": retrieval_solved,
        "no_position_solved_retrieval_tasks": no_position_solved,
        "retrieval_best_methods": {task: row["method"] for task, row in retrieval_best.items()},
        "retrieval_best_top1": {task: row["test_top1_accuracy_mean"] for task, row in retrieval_best.items()},
        "retrieval_best_target_probability": {task: row["test_mean_target_probability_mean"] for task, row in retrieval_best.items()},
        "phase_cued_best_support_accuracy": max(row["test_support_accuracy_mean"] for row in result["aggregate_table"] if row["task"] == "phase_cued_retrieval"),
        "base_capacity_train_top1_threshold": CAPACITY_TRAIN_TOP1_THRESHOLD,
    }


def run_stage87_audit(
    *,
    seeds: tuple[int, ...] = DEFAULT_AUDIT_SEEDS,
    examples_per_length: int = DEFAULT_EXAMPLES_PER_LENGTH,
    epochs: int = DEFAULT_EPOCHS,
    learning_rate: float = DEFAULT_LEARNING_RATE,
    support_aux_weight: float = DEFAULT_SUPPORT_AUX_WEIGHT,
    target_attention_aux_weight: float = DEFAULT_TARGET_ATTENTION_AUX_WEIGHT,
    support_route_weight: float = DEFAULT_SUPPORT_ROUTE_WEIGHT,
    method_names: tuple[str, ...] = METHOD_NAMES,
) -> dict[str, Any]:
    if not autograd_available():
        return build_blocked_result()
    splits_by_task = make_stage10_splits(seeds=seeds, examples_per_length=examples_per_length)
    run_table: list[dict[str, Any]] = []
    failed_runs: list[dict[str, Any]] = []
    for seed in seeds:
        train_rows_by_task = {task_name: [row for row in splits_by_task[task_name]["train"] if row.seed == seed] for task_name in TASK_NAMES}
        multitask_train_rows = [row for task_name in TASK_NAMES for row in train_rows_by_task[task_name]]
        for method_name in method_names:
            try:
                stage10_method = _stage10_method_name(method_name)
                trained = train_dual_auxiliary_pointer_generator_decoder(
                    multitask_train_rows,
                    stage10_method,
                    seed=seed,
                    epochs=epochs,
                    learning_rate=learning_rate,
                    support_aux_weight=support_aux_weight,
                    target_attention_aux_weight=target_attention_aux_weight,
                )
                support_classes = tuple(trained["support_classes"])
                for task_name in TASK_NAMES:
                    task_train_rows = train_rows_by_task[task_name]
                    validation_rows = [row for row in splits_by_task[task_name]["validation"] if row.seed == seed]
                    test_rows = [row for row in splits_by_task[task_name]["test"] if row.seed == seed]
                    row: dict[str, Any] = {
                        "task": task_name,
                        "seed": seed,
                        "method": method_name,
                        "stage10_method_alias": stage10_method,
                        "epochs": epochs,
                        "learning_rate": learning_rate,
                        "support_aux_weight": support_aux_weight,
                        "target_attention_aux_weight": target_attention_aux_weight,
                        "support_route_weight": support_route_weight,
                        "optimizer": trained["optimizer"],
                        "training_tasks": list(TASK_NAMES),
                        "support_classes": list(support_classes),
                        "task_train_row_count": len(task_train_rows),
                        "multitask_train_row_count": len(multitask_train_rows),
                        "train_row_count": len(task_train_rows),
                        "validation_row_count": len(validation_rows),
                        "test_row_count": len(test_rows),
                        "final_training_loss": trained["final_training_loss"],
                        "learned_position_scale": trained["learned_position_scale"],
                        "learned_copy_gate": trained["learned_copy_gate"],
                        "training_history": trained["training_history"],
                    }
                    for split_name, split_rows in (("train", task_train_rows), ("validation", validation_rows), ("test", test_rows)):
                        metrics = evaluate_in_decoder_support_routed_copy_expert(
                            split_rows,
                            stage10_method,
                            trained["weights"],
                            support_classes,
                            support_route_weight=support_route_weight,
                        )
                        for metric_name, value in metrics.items():
                            if metric_name != "row_count":
                                row[f"{split_name}_{metric_name}"] = value
                    run_table.append(row)
            except Exception as exc:  # pragma: no cover
                for task_name in TASK_NAMES:
                    failed_runs.append({"task": task_name, "seed": seed, "method": method_name, "error": str(exc)})
    aggregate_table = _add_support_accuracy_aggregates(_add_copy_gate_aggregates(_aggregate(run_table, failed_runs), run_table), run_table)
    ranking_table = sorted(
        aggregate_table,
        key=lambda row: (
            row["task"],
            row["test_top1_accuracy_mean"],
            row["test_mrr_mean"],
            row["test_mean_target_probability_mean"],
            -row["test_loss_mean"],
            row["method"],
        ),
        reverse=True,
    )
    result = {
        "schema_version": STAGE87_SCHEMA_VERSION,
        "stage": "stage87_in_decoder_support_routed_copy_expert_audit",
        "status": "completed",
        "dataset": "synthetic_stage10_support_complete_rows_multitask_in_decoder_support_routed_copy_expert_v1",
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "source_rows": "stage10 original rows with support-complete same-seed multitask training",
        "source_stage": "stage86_dual_auxiliary_budget_sensitivity_audit",
        "method_names": list(method_names),
        "tasks": list(TASK_NAMES),
        "training_tasks": list(TASK_NAMES),
        "seeds": list(seeds),
        "train_lengths": list(TRAIN_LENGTHS),
        "validation_lengths": list(VALIDATION_LENGTHS),
        "test_lengths": list(TEST_LENGTHS),
        "examples_per_length": examples_per_length,
        "epochs": epochs,
        "learning_rate": learning_rate,
        "support_aux_weight": support_aux_weight,
        "target_attention_aux_weight": target_attention_aux_weight,
        "support_route_weight": support_route_weight,
        "support_coverage": _support_coverage(seeds, examples_per_length),
        "model": {
            "type": "two_block_pointer_generator_in_decoder_support_routed_copy_expert",
            "optimizer": "full_batch_adam_dual_auxiliary",
            "value_output_mode": "learned pointer-generator distribution mixed with a structural support-routed copied-token expert for phase-cued rows",
            "support_routing_policy": "evaluation uses decoder-predicted support probabilities, not gold support labels, target_pos, target_delta, or reference_delta",
            "promotion_limit": "the support-to-token routing rule is a structural expert and not standard free decoder-only language modeling",
            "original_retrieval_tasks": list(RETRIEVAL_TASKS),
        },
        "claim_boundary": _claim_boundary(),
        "failed_runs": failed_runs,
        "run_table": run_table,
        "aggregate_table": aggregate_table,
        "ranking_table": ranking_table,
    }
    result["decision"] = _decision(result)
    return result


def write_stage87_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    return write_stage52_outputs(result, output_dir)


def print_stage87_summary(result: dict[str, Any]) -> None:
    print_stage61_summary(result)
