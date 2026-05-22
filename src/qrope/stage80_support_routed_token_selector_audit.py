from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np

from .stage10_small_decoder_transformer import DEFAULT_SEEDS, TASK_NAMES, Stage10Example, autograd_available, make_stage10_splits
from .stage45_matched_decoder_only_gate import METHOD_NAMES, _stage10_method_name
from .stage52_two_block_decoder_feasibility_audit import GENERALIZATION_TOP1_THRESHOLD, RETRIEVAL_TASKS, TINY_TEXT_TASK
from .stage55_row_metadata_cue_copy_upper_bound_audit import _aggregate, _best_row
from .stage56_standard_input_cue_copy_audit import write_stage56_outputs
from .stage57_support_aware_query_cue_audit import print_stage57_summary
from .stage76_integrated_support_copy_head_audit import (
    _copy_indicator,
    _row_probabilities,
    _softmax,
    _support_features,
    _support_head_accuracy,
    _unpack,
)
from .stage77_auxiliary_support_copy_head_audit import (
    DEFAULT_LEARNING_RATE,
    DEFAULT_SUPPORT_AUX_WEIGHT,
    _serializable_aux_model,
    train_auxiliary_support_copy_head,
)
from .stage79_support_complete_auxiliary_copy_head_audit import (
    DEFAULT_EPOCHS,
    DEFAULT_SUPPORT_COMPLETE_EXAMPLES_PER_LENGTH,
    _support_coverage,
)


STAGE80_SCHEMA_VERSION = "qrope_stage80_support_routed_token_selector_audit_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage80_support_routed_token_selector_audit"
DEFAULT_AUDIT_SEEDS = DEFAULT_SEEDS


def _claim_boundary() -> dict[str, list[str]]:
    return {
        "supported": [
            "A no-credential same-seed support-complete audit that routes recovered support predictions into token selection.",
            "Evidence about whether Stage79's remaining failure is support-to-token coupling rather than support-label recovery.",
            "Fair RoPE/ALiBI/sinusoidal/no-position/PhaseWrap reporting with failed-run retention.",
        ],
        "excluded": [
            "production transformer superiority",
            "full transformer-scale validation",
            "a claim that PhaseWrap-RoPE replaces RoPE",
            "a claim that this support-routed selector is a matched decoder-only transformer",
            "a claim that support-routed retrieval is positional-method promotion evidence when no-position solves too",
            "broad quantum advantage",
        ],
    }


def build_blocked_result(*, reason: str = "missing_optional_autograd_dependency") -> dict[str, Any]:
    return {
        "schema_version": STAGE80_SCHEMA_VERSION,
        "stage": "stage80_support_routed_token_selector_audit",
        "status": "blocked",
        "blocked_reason": reason,
        "install_command": "python -m pip install -e \".[transformer]\"",
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "source_stage": "stage79_support_complete_auxiliary_copy_head_audit",
        "method_names": list(METHOD_NAMES),
        "tasks": list(TASK_NAMES),
        "seeds": list(DEFAULT_AUDIT_SEEDS),
        "claim_boundary": _claim_boundary(),
    }


def _predicted_support_delta(row: Stage10Example, model: dict[str, Any]) -> int:
    support_weights, _, _, _ = _unpack(model["weights"], len(model["classes"]))
    probabilities = np.asarray(_softmax(np.dot(_support_features(row), np.asarray(support_weights, dtype=float))), dtype=float)
    return int(model["classes"][int(np.argmax(probabilities))])


def _support_routed_probabilities(row: Stage10Example, model: dict[str, Any]) -> np.ndarray:
    indicator = np.asarray(_copy_indicator(row), dtype=float)
    probabilities = np.zeros(indicator.shape[1], dtype=float)
    predicted_delta = _predicted_support_delta(row, model)
    candidate_deltas = [delta for delta in range(predicted_delta, row.query_pos, 24) if delta >= 3]
    selected_delta = int(candidate_deltas[-1]) if candidate_deltas else predicted_delta
    selected_position = int(row.query_pos - selected_delta)
    if 0 <= selected_position < row.query_pos:
        probabilities += indicator[selected_position]
    else:
        probabilities += 1.0 / float(len(probabilities))
    total = float(np.sum(probabilities))
    if total <= 0.0:
        probabilities += 1.0 / float(len(probabilities))
    else:
        probabilities = probabilities / total
    return probabilities


def _routed_row_probabilities(row: Stage10Example, method_name: str, model: dict[str, Any]) -> np.ndarray:
    if row.task == "phase_cued_retrieval":
        return _support_routed_probabilities(row, model)
    return np.asarray(_row_probabilities(model["weights"], row, method_name, model["classes"]), dtype=float)


def _predict(row: Stage10Example, method_name: str, model: dict[str, Any]) -> tuple[float, int, float]:
    probabilities = _routed_row_probabilities(row, method_name, model)
    sorted_indices = sorted(range(len(probabilities)), key=lambda index: (-float(probabilities[index]), index))
    return float(probabilities[row.label_token]), int(sorted_indices.index(row.label_token) + 1), float(probabilities[sorted_indices[0]])


def evaluate_support_routed_token_selector(rows: list[Stage10Example], method_name: str, model: dict[str, Any]) -> dict[str, float]:
    from .stage49_copy_decoder_retrieval_repair_audit import _expected_calibration_error

    losses: list[float] = []
    reciprocal_ranks: list[float] = []
    top1_hits: list[float] = []
    target_probs: list[float] = []
    top1_confidences: list[float] = []
    for row in rows:
        target_probability, rank, top1_confidence = _predict(row, method_name, model)
        losses.append(-math.log(max(target_probability, 1e-12)))
        reciprocal_ranks.append(1.0 / float(rank))
        top1_hits.append(1.0 if rank == 1 else 0.0)
        target_probs.append(target_probability)
        top1_confidences.append(top1_confidence)
    mean_loss = float(np.mean(losses))
    return {
        "row_count": float(len(rows)),
        "loss": round(mean_loss, 6),
        "perplexity": round(float(np.exp(mean_loss)), 6),
        "top1_accuracy": round(float(np.mean(top1_hits)), 6),
        "mrr": round(float(np.mean(reciprocal_ranks)), 6),
        "mean_target_probability": round(float(np.mean(target_probs)), 6),
        "mean_top1_confidence": round(float(np.mean(top1_confidences)), 6),
        "expected_calibration_error": round(_expected_calibration_error(top1_confidences, top1_hits), 6),
    }


def _decision(aggregate_table: list[dict[str, Any]], *, support_summary: dict[str, dict[str, float]]) -> dict[str, Any]:
    retrieval_best = {task: _best_row(aggregate_table, task_name=task) for task in RETRIEVAL_TASKS}
    retrieval_solved = [task for task, row in retrieval_best.items() if row["test_top1_accuracy_mean"] >= GENERALIZATION_TOP1_THRESHOLD]
    no_position_solved = [
        task
        for task in RETRIEVAL_TASKS
        for row in aggregate_table
        if row["task"] == task and row["method"] == "no_position" and row["test_top1_accuracy_mean"] >= GENERALIZATION_TOP1_THRESHOLD
    ]
    phasewrap_best = [task for task, row in retrieval_best.items() if row["method"].startswith("phasewrap")]
    mean_support_accuracy = round(float(np.mean([row["phase_cued_test_support_accuracy"] for row in support_summary.values()])), 6)
    if "phase_cued_retrieval" in retrieval_solved and "phase_cued_retrieval" in no_position_solved:
        decision = "SUPPORT_ROUTED_TOKEN_SELECTOR_SOLVES_PHASE_CUED_NOT_PROMOTION"
        boundary = "Routing recovered support into token selection repairs phase-cued retrieval for no-position too; this is a coupling diagnostic, not positional-method promotion."
    elif "phase_cued_retrieval" in retrieval_solved:
        decision = "SUPPORT_ROUTED_TOKEN_SELECTOR_PHASE_CUED_REVIEW_REQUIRED"
        boundary = "Routing recovered support into token selection repairs phase-cued retrieval without no-position crossing threshold; review method ordering before any claim update."
    elif mean_support_accuracy >= 1.0:
        decision = "SUPPORT_ROUTED_TOKEN_SELECTOR_SUPPORT_RECOVERED_RETRIEVAL_FAILED"
        boundary = "Support labels are recovered, but explicit support-to-token routing still does not repair phase-cued retrieval."
    else:
        decision = "SUPPORT_ROUTED_TOKEN_SELECTOR_SUPPORT_NOT_RECOVERED"
        boundary = "Support labels are not fully recovered under the support-routed selector audit."
    tiny_best = _best_row(aggregate_table, task_name=TINY_TEXT_TASK)
    return {
        "decision": decision,
        "generalization_top1_threshold": GENERALIZATION_TOP1_THRESHOLD,
        "retrieval_solved_tasks": retrieval_solved,
        "no_position_solved_retrieval_tasks": no_position_solved,
        "phasewrap_best_retrieval_tasks": phasewrap_best,
        "retrieval_best_methods": {task: row["method"] for task, row in retrieval_best.items()},
        "retrieval_best_top1": {task: row["test_top1_accuracy_mean"] for task, row in retrieval_best.items()},
        "retrieval_best_target_probability": {task: row["test_mean_target_probability_mean"] for task, row in retrieval_best.items()},
        "tiny_text_best_method": tiny_best["method"],
        "tiny_text_best_top1": tiny_best["test_top1_accuracy_mean"],
        "mean_phase_cued_test_support_accuracy": mean_support_accuracy,
        "claim_boundary": boundary,
    }


def run_stage80_audit(
    *,
    seeds: tuple[int, ...] = DEFAULT_AUDIT_SEEDS,
    examples_per_length: int = DEFAULT_SUPPORT_COMPLETE_EXAMPLES_PER_LENGTH,
    method_names: tuple[str, ...] = METHOD_NAMES,
    epochs: int = DEFAULT_EPOCHS,
    learning_rate: float = DEFAULT_LEARNING_RATE,
    support_aux_weight: float = DEFAULT_SUPPORT_AUX_WEIGHT,
) -> dict[str, Any]:
    if not autograd_available():
        return build_blocked_result()
    splits_by_task = make_stage10_splits(seeds=seeds, examples_per_length=examples_per_length)
    run_table: list[dict[str, Any]] = []
    failed_runs: list[dict[str, Any]] = []
    models: dict[str, dict[str, Any]] = {}
    support_summary: dict[str, dict[str, float]] = {}
    for seed in seeds:
        train_rows_all = [row for splits in splits_by_task.values() for row in splits["train"] if row.seed == seed]
        phase_test_rows = [row for row in splits_by_task["phase_cued_retrieval"]["test"] if row.seed == seed]
        for method_name in method_names:
            try:
                model = train_auxiliary_support_copy_head(
                    train_rows_all,
                    _stage10_method_name(method_name),
                    epochs=epochs,
                    learning_rate=learning_rate,
                    support_aux_weight=support_aux_weight,
                )
                model_key = f"{seed}:{method_name}"
                models[model_key] = _serializable_aux_model(model)
                support_summary[model_key] = {
                    "phase_cued_test_support_accuracy": _support_head_accuracy(phase_test_rows, model)["accuracy"],
                    "final_training_loss": model["final_training_loss"],
                }
                for task_name, splits in splits_by_task.items():
                    train_rows = [row for row in splits["train"] if row.seed == seed]
                    validation_rows = [row for row in splits["validation"] if row.seed == seed]
                    test_rows = [row for row in splits["test"] if row.seed == seed]
                    run: dict[str, Any] = {
                        "task": task_name,
                        "seed": seed,
                        "method": method_name,
                        "stage10_method_alias": _stage10_method_name(method_name),
                        "train_row_count": len(train_rows),
                        "validation_row_count": len(validation_rows),
                        "test_row_count": len(test_rows),
                        "support_class_count": len(model["classes"]),
                        "support_head_test_accuracy": support_summary[model_key]["phase_cued_test_support_accuracy"] if task_name == "phase_cued_retrieval" else 1.0,
                        "selected_position_scale": model["learned_position_scale"],
                        "selected_cue_scale": model["learned_cue_scale"],
                        "selected_distance_scale": model["learned_distance_scale"],
                    }
                    for split_name, split_rows in (("train", train_rows), ("validation", validation_rows), ("test", test_rows)):
                        metrics = evaluate_support_routed_token_selector(split_rows, _stage10_method_name(method_name), model)
                        for metric_name, value in metrics.items():
                            if metric_name != "row_count":
                                run[f"{split_name}_{metric_name}"] = value
                    run_table.append(run)
            except Exception as exc:  # pragma: no cover
                for task_name in TASK_NAMES:
                    failed_runs.append({"task": task_name, "seed": seed, "method": method_name, "error": str(exc)})
    aggregate_table = _aggregate(run_table, failed_runs)
    ranking_table = sorted(
        aggregate_table,
        key=lambda row: (
            row["task"],
            row["test_top1_accuracy_mean"],
            row["test_mrr_mean"],
            row["test_mean_target_probability_mean"],
            row["method"],
        ),
        reverse=True,
    )
    return {
        "schema_version": STAGE80_SCHEMA_VERSION,
        "stage": "stage80_support_routed_token_selector_audit",
        "status": "completed",
        "dataset": "synthetic_stage10_original_rows_same_seed_support_complete_routed_selector_v1",
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "source_stage": "stage79_support_complete_auxiliary_copy_head_audit",
        "method_names": list(method_names),
        "tasks": list(TASK_NAMES),
        "seeds": list(seeds),
        "examples_per_length": examples_per_length,
        "epochs": epochs,
        "learning_rate": learning_rate,
        "support_aux_weight": support_aux_weight,
        "support_complete_policy": "examples_per_length=6 restores same-seed phase-cued query-support coverage for held-out rows",
        "support_coverage": _support_coverage(seeds, examples_per_length),
        "models": models,
        "support_summary": support_summary,
        "model": {
            "type": "same_seed_support_complete_support_routed_token_selector",
            "value_output_mode": "deterministic copied prefix-token mass with support-predicted phase class routed to farthest congruent token selection for phase-cued rows",
            "metadata_excluded": ["hard query-support lookup", "standalone pretrained support head", "row.reference_delta exact value at evaluation", "row.target_pos", "row.target_delta"],
        },
        "claim_boundary": _claim_boundary(),
        "failed_runs": failed_runs,
        "run_table": run_table,
        "aggregate_table": aggregate_table,
        "ranking_table": ranking_table,
        "decision": _decision(aggregate_table, support_summary=support_summary),
    }


def write_stage80_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    return write_stage56_outputs(result, output_dir)


def print_stage80_summary(result: dict[str, Any]) -> None:
    print_stage57_summary(result)
