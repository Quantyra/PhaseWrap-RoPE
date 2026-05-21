from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from .stage10_small_decoder_transformer import DEFAULT_SEEDS, TASK_NAMES, Stage10Example, autograd_available, make_stage10_splits
from .stage45_matched_decoder_only_gate import METHOD_NAMES, _stage10_method_name
from .stage52_two_block_decoder_feasibility_audit import GENERALIZATION_TOP1_THRESHOLD, RETRIEVAL_TASKS, TINY_TEXT_TASK
from .stage55_row_metadata_cue_copy_upper_bound_audit import _aggregate, _best_row
from .stage56_standard_input_cue_copy_audit import DEFAULT_EXAMPLES_PER_LENGTH, write_stage56_outputs
from .stage57_support_aware_query_cue_audit import print_stage57_summary
from .stage76_integrated_support_copy_head_audit import (
    DEFAULT_EPOCHS,
    DEFAULT_LEARNING_RATE,
    _init_vector,
    _row_loss,
    _row_probabilities,
    _serializable_model,
    _softmax,
    _support_classes,
    _support_features,
    _support_head_accuracy,
    _unpack,
    evaluate_integrated_support_copy_head,
)


STAGE77_SCHEMA_VERSION = "qrope_stage77_auxiliary_support_copy_head_audit_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage77_auxiliary_support_copy_head_audit"
DEFAULT_AUDIT_SEEDS = DEFAULT_SEEDS
DEFAULT_SUPPORT_AUX_WEIGHT = 1.0


def _claim_boundary() -> dict[str, list[str]]:
    return {
        "supported": [
            "A no-credential same-seed auxiliary-support integrated copy-head audit over original Stage10 rows.",
            "Evidence about whether explicit support supervision preserves the Stage75 visible-cue recovery inside the integrated copy objective.",
            "Fair RoPE/ALiBI/sinusoidal/no-position/PhaseWrap reporting with failed-run retention.",
        ],
        "excluded": [
            "production transformer superiority",
            "full transformer-scale validation",
            "a claim that PhaseWrap-RoPE replaces RoPE",
            "a claim that this compact auxiliary copy-head is a matched decoder-only transformer",
            "a claim that support-supervised recovery is positional-method promotion evidence when no-position solves too",
            "broad quantum advantage",
        ],
    }


def build_blocked_result(*, reason: str = "missing_optional_autograd_dependency") -> dict[str, Any]:
    return {
        "schema_version": STAGE77_SCHEMA_VERSION,
        "stage": "stage77_auxiliary_support_copy_head_audit",
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


def _support_loss(vector: Any, row: Stage10Example, classes: tuple[int, ...]):
    import autograd.numpy as anp

    support_weights, _, _, _ = _unpack(vector, len(classes))
    class_index = classes.index(int(row.reference_delta))
    probabilities = _softmax(anp.dot(anp.array(_support_features(row)), support_weights))
    return -anp.log(probabilities[class_index] + 1e-12)


def _batch_loss(
    vector: Any,
    rows: list[Stage10Example],
    method_name: str,
    classes: tuple[int, ...],
    *,
    support_aux_weight: float,
):
    import autograd.numpy as anp

    copy_losses = [_row_loss(vector, row, method_name, classes) for row in rows]
    support_rows = [row for row in rows if row.task == "phase_cued_retrieval"]
    if support_rows:
        support_losses = [_support_loss(vector, row, classes) for row in support_rows]
        return anp.mean(anp.array(copy_losses)) + support_aux_weight * anp.mean(anp.array(support_losses))
    return anp.mean(anp.array(copy_losses))


def train_auxiliary_support_copy_head(
    rows: list[Stage10Example],
    method_name: str,
    *,
    epochs: int = DEFAULT_EPOCHS,
    learning_rate: float = DEFAULT_LEARNING_RATE,
    support_aux_weight: float = DEFAULT_SUPPORT_AUX_WEIGHT,
) -> dict[str, Any]:
    from autograd import grad

    classes = _support_classes(rows)
    vector = _init_vector(classes)
    gradient = grad(lambda current: _batch_loss(current, rows, method_name, classes, support_aux_weight=support_aux_weight))
    moment = np.zeros_like(vector)
    velocity = np.zeros_like(vector)
    beta1 = 0.9
    beta2 = 0.999
    epsilon = 1e-8
    history: list[dict[str, float]] = []
    for epoch in range(1, epochs + 1):
        total_loss = float(_batch_loss(vector, rows, method_name, classes, support_aux_weight=support_aux_weight))
        copy_loss = float(np.mean([float(_row_loss(vector, row, method_name, classes)) for row in rows]))
        support_rows = [row for row in rows if row.task == "phase_cued_retrieval"]
        support_loss = float(np.mean([float(_support_loss(vector, row, classes)) for row in support_rows])) if support_rows else 0.0
        grad_value = gradient(vector)
        moment = beta1 * moment + (1.0 - beta1) * grad_value
        velocity = beta2 * velocity + (1.0 - beta2) * (grad_value * grad_value)
        moment_hat = moment / (1.0 - beta1**epoch)
        velocity_hat = velocity / (1.0 - beta2**epoch)
        vector = vector - learning_rate * moment_hat / (np.sqrt(velocity_hat) + epsilon)
        if epoch in {1, epochs // 4, epochs // 2, (3 * epochs) // 4, epochs}:
            history.append({"epoch": epoch, "loss": round(total_loss, 6), "copy_loss": round(copy_loss, 6), "support_loss": round(support_loss, 6)})
    support_weights, position_scale, cue_scale, distance_scale = _unpack(vector, len(classes))
    return {
        "weights": vector,
        "classes": classes,
        "optimizer": "full_batch_adam_with_support_auxiliary_loss",
        "epochs": epochs,
        "learning_rate": learning_rate,
        "support_aux_weight": support_aux_weight,
        "training_history": history,
        "final_training_loss": history[-1]["loss"],
        "learned_position_scale": round(float(position_scale), 6),
        "learned_cue_scale": round(float(cue_scale), 6),
        "learned_distance_scale": round(float(distance_scale), 6),
        "support_weight_norm": round(float(np.linalg.norm(np.asarray(support_weights, dtype=float))), 6),
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
        decision = "AUXILIARY_SUPPORT_COPY_HEAD_SOLVES_PHASE_CUED_NOT_PROMOTION"
        boundary = "Auxiliary support supervision preserves phase-cued retrieval for no-position too; this is not positional-method promotion."
    elif retrieval_solved:
        decision = "AUXILIARY_SUPPORT_COPY_HEAD_PARTIAL_RETRIEVAL"
        boundary = "Auxiliary support supervision solves at least one retrieval lane but not the full retrieval set."
    else:
        decision = "AUXILIARY_SUPPORT_COPY_HEAD_RETRIEVAL_FAILED"
        boundary = "Auxiliary support supervision does not solve retrieval."
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


def _serializable_aux_model(model: dict[str, Any]) -> dict[str, Any]:
    record = _serializable_model(model)
    record["support_aux_weight"] = model["support_aux_weight"]
    return record


def run_stage77_audit(
    *,
    seeds: tuple[int, ...] = DEFAULT_AUDIT_SEEDS,
    examples_per_length: int = DEFAULT_EXAMPLES_PER_LENGTH,
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
                        metrics = evaluate_integrated_support_copy_head(split_rows, _stage10_method_name(method_name), model)
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
        "schema_version": STAGE77_SCHEMA_VERSION,
        "stage": "stage77_auxiliary_support_copy_head_audit",
        "status": "completed",
        "dataset": "synthetic_stage10_original_rows_same_seed_auxiliary_support_copy_v1",
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "source_stage": "stage76_integrated_support_copy_head_audit",
        "method_names": list(method_names),
        "tasks": list(TASK_NAMES),
        "seeds": list(seeds),
        "examples_per_length": examples_per_length,
        "epochs": epochs,
        "learning_rate": learning_rate,
        "support_aux_weight": support_aux_weight,
        "models": models,
        "support_summary": support_summary,
        "model": {
            "type": "same_seed_auxiliary_support_copy_head",
            "value_output_mode": "deterministic copied prefix-token mass",
            "metadata_excluded": ["hard query-support lookup", "standalone pretrained support head", "row.reference_delta exact value at evaluation", "row.target_pos", "row.target_delta"],
        },
        "claim_boundary": _claim_boundary(),
        "failed_runs": failed_runs,
        "run_table": run_table,
        "aggregate_table": aggregate_table,
        "ranking_table": ranking_table,
        "decision": _decision(aggregate_table, support_summary=support_summary),
    }


def write_stage77_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    return write_stage56_outputs(result, output_dir)


def print_stage77_summary(result: dict[str, Any]) -> None:
    print_stage57_summary(result)
