from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np

from .stage10_small_decoder_transformer import DEFAULT_SEEDS, TASK_NAMES, Stage10Example, autograd_available, make_stage10_splits, positional_bias
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


STAGE82_SCHEMA_VERSION = "qrope_stage82_learned_support_routing_head_audit_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage82_learned_support_routing_head_audit"
DEFAULT_AUDIT_SEEDS = DEFAULT_SEEDS
DEFAULT_ROUTING_EPOCHS = 120
DEFAULT_ROUTING_LEARNING_RATE = 0.15


def _claim_boundary() -> dict[str, list[str]]:
    return {
        "supported": [
            "A no-credential same-seed support-complete audit that trains a small routing head over learned support probabilities.",
            "Evidence about whether Stage81's hard farthest-congruent routing rule can be replaced by learned routing scales.",
            "Fair RoPE/ALiBI/sinusoidal/no-position/PhaseWrap reporting with failed-run retention.",
        ],
        "excluded": [
            "production transformer superiority",
            "full transformer-scale validation",
            "a claim that PhaseWrap-RoPE replaces RoPE",
            "a claim that this compact learned routing head is a matched decoder-only transformer",
            "a claim that learned support routing is positional-method promotion evidence when no-position solves too",
            "broad quantum advantage",
        ],
    }


def build_blocked_result(*, reason: str = "missing_optional_autograd_dependency") -> dict[str, Any]:
    return {
        "schema_version": STAGE82_SCHEMA_VERSION,
        "stage": "stage82_learned_support_routing_head_audit",
        "status": "blocked",
        "blocked_reason": reason,
        "install_command": "python -m pip install -e \".[transformer]\"",
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "source_stage": "stage81_soft_support_routed_token_selector_audit",
        "method_names": list(METHOD_NAMES),
        "tasks": list(TASK_NAMES),
        "seeds": list(DEFAULT_AUDIT_SEEDS),
        "claim_boundary": _claim_boundary(),
    }


def _support_distribution(row: Stage10Example, model: dict[str, Any]) -> np.ndarray:
    support_weights, _, _, _ = _unpack(model["weights"], len(model["classes"]))
    return np.asarray(_softmax(np.dot(_support_features(row), np.asarray(support_weights, dtype=float))), dtype=float)


def _support_scores(row: Stage10Example, model: dict[str, Any]):
    import autograd.numpy as anp

    distances = np.array([row.query_pos - index for index in range(row.query_pos)], dtype=float)
    support_probabilities = _support_distribution(row, model)
    scores = np.zeros(row.query_pos, dtype=float)
    for class_index, reference_delta in enumerate(model["classes"]):
        exact_distance = (distances == float(reference_delta)).astype(float)
        phase_congruent = (((distances - float(reference_delta)) % 24.0) == 0.0).astype(float)
        scores += float(support_probabilities[class_index]) * (exact_distance + phase_congruent)
    return anp.array(scores)


def _routing_attention(route_vector: Any, row: Stage10Example, method_name: str, model: dict[str, Any]):
    import autograd.numpy as anp

    position_scale, support_scale, distance_scale = route_vector
    distances = anp.array([row.query_pos - index for index in range(row.query_pos)], dtype=float)
    logits = position_scale * anp.array(positional_bias(row, method_name))
    logits = logits + support_scale * _support_scores(row, model)
    logits = logits + distance_scale * distances / max(1.0, float(row.query_pos))
    return _softmax(logits)


def _routing_row_probabilities(route_vector: Any, row: Stage10Example, method_name: str, model: dict[str, Any]):
    import autograd.numpy as anp

    attention = _routing_attention(route_vector, row, method_name, model)
    return anp.dot(attention, _copy_indicator(row))


def _routing_loss(route_vector: Any, rows: list[Stage10Example], method_name: str, model: dict[str, Any]):
    import autograd.numpy as anp

    losses = []
    for row in rows:
        probabilities = _routing_row_probabilities(route_vector, row, method_name, model)
        losses.append(-anp.log(probabilities[row.label_token] + 1e-12))
    return anp.mean(anp.array(losses))


def train_support_routing_head(
    rows: list[Stage10Example],
    method_name: str,
    model: dict[str, Any],
    *,
    epochs: int = DEFAULT_ROUTING_EPOCHS,
    learning_rate: float = DEFAULT_ROUTING_LEARNING_RATE,
) -> dict[str, Any]:
    from autograd import grad

    route_rows = [row for row in rows if row.task == "phase_cued_retrieval"]
    vector = np.array([0.0, 1.0, 0.0], dtype=float)
    gradient = grad(lambda current: _routing_loss(current, route_rows, method_name, model))
    moment = np.zeros_like(vector)
    velocity = np.zeros_like(vector)
    beta1 = 0.9
    beta2 = 0.999
    epsilon = 1e-8
    history: list[dict[str, float]] = []
    for epoch in range(1, epochs + 1):
        loss_value = float(_routing_loss(vector, route_rows, method_name, model))
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
        "optimizer": "full_batch_adam_route_scales",
        "epochs": epochs,
        "learning_rate": learning_rate,
        "training_history": history,
        "final_training_loss": history[-1]["loss"],
        "learned_position_scale": round(float(vector[0]), 6),
        "learned_support_scale": round(float(vector[1]), 6),
        "learned_distance_scale": round(float(vector[2]), 6),
    }


def _routed_row_probabilities(row: Stage10Example, method_name: str, model: dict[str, Any], routing_head: dict[str, Any]) -> np.ndarray:
    if row.task == "phase_cued_retrieval":
        return np.asarray(_routing_row_probabilities(routing_head["weights"], row, method_name, model), dtype=float)
    return np.asarray(_row_probabilities(model["weights"], row, method_name, model["classes"]), dtype=float)


def _predict(row: Stage10Example, method_name: str, model: dict[str, Any], routing_head: dict[str, Any]) -> tuple[float, int, float]:
    probabilities = _routed_row_probabilities(row, method_name, model, routing_head)
    sorted_indices = sorted(range(len(probabilities)), key=lambda index: (-float(probabilities[index]), index))
    return float(probabilities[row.label_token]), int(sorted_indices.index(row.label_token) + 1), float(probabilities[sorted_indices[0]])


def evaluate_learned_support_routing_head(rows: list[Stage10Example], method_name: str, model: dict[str, Any], routing_head: dict[str, Any]) -> dict[str, float]:
    from .stage49_copy_decoder_retrieval_repair_audit import _expected_calibration_error

    losses: list[float] = []
    reciprocal_ranks: list[float] = []
    top1_hits: list[float] = []
    target_probs: list[float] = []
    top1_confidences: list[float] = []
    for row in rows:
        target_probability, rank, top1_confidence = _predict(row, method_name, model, routing_head)
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
        decision = "LEARNED_SUPPORT_ROUTING_HEAD_SOLVES_PHASE_CUED_NOT_PROMOTION"
        boundary = "A learned support-to-token routing head repairs phase-cued retrieval for no-position too; this is a learned coupling diagnostic, not positional-method promotion."
    elif "phase_cued_retrieval" in retrieval_solved:
        decision = "LEARNED_SUPPORT_ROUTING_HEAD_PHASE_CUED_REVIEW_REQUIRED"
        boundary = "A learned support-to-token routing head repairs phase-cued retrieval without no-position crossing threshold; review method ordering before any claim update."
    elif mean_support_accuracy >= 1.0:
        decision = "LEARNED_SUPPORT_ROUTING_HEAD_SUPPORT_RECOVERED_RETRIEVAL_FAILED"
        boundary = "Support labels are recovered, but learned support-to-token routing still does not repair phase-cued retrieval."
    else:
        decision = "LEARNED_SUPPORT_ROUTING_HEAD_SUPPORT_NOT_RECOVERED"
        boundary = "Support labels are not fully recovered under the learned support-routing audit."
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


def _serializable_routing_head(head: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in head.items()
        if key != "weights"
    } | {"weights": np.asarray(head["weights"], dtype=float).round(8).tolist()}


def run_stage82_audit(
    *,
    seeds: tuple[int, ...] = DEFAULT_AUDIT_SEEDS,
    examples_per_length: int = DEFAULT_SUPPORT_COMPLETE_EXAMPLES_PER_LENGTH,
    method_names: tuple[str, ...] = METHOD_NAMES,
    epochs: int = DEFAULT_EPOCHS,
    learning_rate: float = DEFAULT_LEARNING_RATE,
    support_aux_weight: float = DEFAULT_SUPPORT_AUX_WEIGHT,
    routing_epochs: int = DEFAULT_ROUTING_EPOCHS,
    routing_learning_rate: float = DEFAULT_ROUTING_LEARNING_RATE,
) -> dict[str, Any]:
    if not autograd_available():
        return build_blocked_result()
    splits_by_task = make_stage10_splits(seeds=seeds, examples_per_length=examples_per_length)
    run_table: list[dict[str, Any]] = []
    failed_runs: list[dict[str, Any]] = []
    models: dict[str, dict[str, Any]] = {}
    routing_heads: dict[str, dict[str, Any]] = {}
    support_summary: dict[str, dict[str, float]] = {}
    for seed in seeds:
        train_rows_all = [row for splits in splits_by_task.values() for row in splits["train"] if row.seed == seed]
        phase_test_rows = [row for row in splits_by_task["phase_cued_retrieval"]["test"] if row.seed == seed]
        for method_name in method_names:
            try:
                stage10_method = _stage10_method_name(method_name)
                model = train_auxiliary_support_copy_head(
                    train_rows_all,
                    stage10_method,
                    epochs=epochs,
                    learning_rate=learning_rate,
                    support_aux_weight=support_aux_weight,
                )
                routing_head = train_support_routing_head(
                    train_rows_all,
                    stage10_method,
                    model,
                    epochs=routing_epochs,
                    learning_rate=routing_learning_rate,
                )
                model_key = f"{seed}:{method_name}"
                models[model_key] = _serializable_aux_model(model)
                routing_heads[model_key] = _serializable_routing_head(routing_head)
                support_summary[model_key] = {
                    "phase_cued_test_support_accuracy": _support_head_accuracy(phase_test_rows, model)["accuracy"],
                    "final_training_loss": model["final_training_loss"],
                    "routing_final_training_loss": routing_head["final_training_loss"],
                }
                for task_name, splits in splits_by_task.items():
                    train_rows = [row for row in splits["train"] if row.seed == seed]
                    validation_rows = [row for row in splits["validation"] if row.seed == seed]
                    test_rows = [row for row in splits["test"] if row.seed == seed]
                    run: dict[str, Any] = {
                        "task": task_name,
                        "seed": seed,
                        "method": method_name,
                        "stage10_method_alias": stage10_method,
                        "train_row_count": len(train_rows),
                        "validation_row_count": len(validation_rows),
                        "test_row_count": len(test_rows),
                        "support_class_count": len(model["classes"]),
                        "support_head_test_accuracy": support_summary[model_key]["phase_cued_test_support_accuracy"] if task_name == "phase_cued_retrieval" else 1.0,
                        "selected_position_scale": routing_head["learned_position_scale"],
                        "selected_cue_scale": routing_head["learned_support_scale"],
                        "selected_distance_scale": routing_head["learned_distance_scale"],
                        "routing_position_scale": routing_head["learned_position_scale"],
                        "routing_support_scale": routing_head["learned_support_scale"],
                        "routing_distance_scale": routing_head["learned_distance_scale"],
                    }
                    for split_name, split_rows in (("train", train_rows), ("validation", validation_rows), ("test", test_rows)):
                        metrics = evaluate_learned_support_routing_head(split_rows, stage10_method, model, routing_head)
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
        "schema_version": STAGE82_SCHEMA_VERSION,
        "stage": "stage82_learned_support_routing_head_audit",
        "status": "completed",
        "dataset": "synthetic_stage10_original_rows_same_seed_support_complete_learned_routing_v1",
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "source_stage": "stage81_soft_support_routed_token_selector_audit",
        "method_names": list(method_names),
        "tasks": list(TASK_NAMES),
        "seeds": list(seeds),
        "examples_per_length": examples_per_length,
        "epochs": epochs,
        "learning_rate": learning_rate,
        "support_aux_weight": support_aux_weight,
        "routing_epochs": routing_epochs,
        "routing_learning_rate": routing_learning_rate,
        "support_complete_policy": "examples_per_length=6 restores same-seed phase-cued query-support coverage for held-out rows",
        "support_coverage": _support_coverage(seeds, examples_per_length),
        "models": models,
        "routing_heads": routing_heads,
        "support_summary": support_summary,
        "model": {
            "type": "same_seed_support_complete_learned_support_routing_head",
            "value_output_mode": "deterministic copied prefix-token mass with learned support-congruence, positional-bias, and distance routing scales for phase-cued rows",
            "metadata_excluded": ["hard query-support lookup", "hard support argmax", "hard farthest-congruent selector", "standalone pretrained support head", "row.reference_delta exact value at evaluation", "row.target_pos", "row.target_delta"],
        },
        "claim_boundary": _claim_boundary(),
        "failed_runs": failed_runs,
        "run_table": run_table,
        "aggregate_table": aggregate_table,
        "ranking_table": ranking_table,
        "decision": _decision(aggregate_table, support_summary=support_summary),
    }


def write_stage82_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    return write_stage56_outputs(result, output_dir)


def print_stage82_summary(result: dict[str, Any]) -> None:
    print_stage57_summary(result)
