from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from .stage10_small_decoder_transformer import DEFAULT_SEEDS, TASK_NAMES, TEXT_TOKEN_IDS, VOCAB_SIZE, Stage10Example, make_stage10_splits, positional_bias
from .stage45_matched_decoder_only_gate import METHOD_NAMES, _stage10_method_name
from .stage52_two_block_decoder_feasibility_audit import GENERALIZATION_TOP1_THRESHOLD, RETRIEVAL_TASKS, TINY_TEXT_TASK
from .stage55_row_metadata_cue_copy_upper_bound_audit import (
    DEFAULT_CUE_SCALES,
    DEFAULT_DISTANCE_SCALES,
    DEFAULT_POSITION_SCALES,
    _aggregate,
    _best_row,
    _ranked_indices,
    _softmax,
)
from .stage56_standard_input_cue_copy_audit import DEFAULT_EXAMPLES_PER_LENGTH, write_stage56_outputs
from .stage57_support_aware_query_cue_audit import print_stage57_summary
from .stage58_pooled_train_query_support_audit import _query_mod


STAGE75_SCHEMA_VERSION = "qrope_stage75_learned_query_support_head_audit_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage75_learned_query_support_head_audit"
DEFAULT_AUDIT_SEEDS = DEFAULT_SEEDS
DEFAULT_SUPPORT_HEAD_EPOCHS = 450
DEFAULT_SUPPORT_HEAD_LEARNING_RATE = 0.35


def _claim_boundary() -> dict[str, list[str]]:
    return {
        "supported": [
            "A no-credential leave-one-seed learned visible query-support head over original Stage10 rows.",
            "Evidence about whether Stage74 deterministic query-support lookup can be replaced by a trained softmax support head.",
            "Fair RoPE/ALiBI/sinusoidal/no-position/PhaseWrap reporting with failed-run retention.",
        ],
        "excluded": [
            "production transformer superiority",
            "full transformer-scale validation",
            "a claim that PhaseWrap-RoPE replaces RoPE",
            "a claim that a standalone query-support head is a matched decoder-only transformer",
            "a claim that learned visible-cue recovery is positional-method promotion evidence when no-position solves too",
            "broad quantum advantage",
        ],
    }


def build_blocked_result(*, reason: str = "unexpected_preflight_block") -> dict[str, Any]:
    return {
        "schema_version": STAGE75_SCHEMA_VERSION,
        "stage": "stage75_learned_query_support_head_audit",
        "status": "blocked",
        "blocked_reason": reason,
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "method_names": list(METHOD_NAMES),
        "tasks": list(TASK_NAMES),
        "seeds": list(DEFAULT_AUDIT_SEEDS),
        "claim_boundary": _claim_boundary(),
    }


def _support_features(row: Stage10Example) -> np.ndarray:
    query_mod = _query_mod(row)
    features = np.zeros(17, dtype=float)
    features[query_mod] = 1.0
    features[-1] = 1.0
    return features


def _softmax_rows(logits: np.ndarray) -> np.ndarray:
    shifted = logits - np.max(logits, axis=1, keepdims=True)
    exp_values = np.exp(shifted)
    return exp_values / np.sum(exp_values, axis=1, keepdims=True)


def train_query_support_head(
    rows: list[Stage10Example],
    *,
    epochs: int = DEFAULT_SUPPORT_HEAD_EPOCHS,
    learning_rate: float = DEFAULT_SUPPORT_HEAD_LEARNING_RATE,
) -> dict[str, Any]:
    support_rows = [row for row in rows if row.task == "phase_cued_retrieval"]
    if not support_rows:
        raise ValueError("query support head requires phase_cued_retrieval train rows")
    classes = tuple(sorted({int(row.reference_delta) for row in support_rows}))
    class_to_index = {value: index for index, value in enumerate(classes)}
    features = np.vstack([_support_features(row) for row in support_rows])
    labels = np.array([class_to_index[int(row.reference_delta)] for row in support_rows], dtype=int)
    weights = np.zeros((features.shape[1], len(classes)), dtype=float)
    history: list[dict[str, float]] = []
    for epoch in range(1, epochs + 1):
        probabilities = _softmax_rows(features @ weights)
        loss = -float(np.mean(np.log(np.maximum(probabilities[np.arange(len(labels)), labels], 1e-12))))
        gradient = features.T @ (probabilities - np.eye(len(classes), dtype=float)[labels]) / float(len(labels))
        weights -= learning_rate * gradient
        if epoch in {1, epochs // 4, epochs // 2, (3 * epochs) // 4, epochs}:
            predictions = np.argmax(probabilities, axis=1)
            history.append(
                {
                    "epoch": epoch,
                    "loss": round(loss, 6),
                    "train_support_accuracy": round(float(np.mean(predictions == labels)), 6),
                }
            )
    final_probabilities = _softmax_rows(features @ weights)
    final_predictions = np.argmax(final_probabilities, axis=1)
    return {
        "weights": weights,
        "classes": classes,
        "optimizer": "full_batch_softmax_gradient_descent",
        "epochs": epochs,
        "learning_rate": learning_rate,
        "training_history": history,
        "final_training_loss": history[-1]["loss"],
        "final_train_support_accuracy": round(float(np.mean(final_predictions == labels)), 6),
    }


def _support_distribution(head: dict[str, Any], row: Stage10Example) -> dict[int, float]:
    weights = np.asarray(head["weights"], dtype=float)
    probabilities = _softmax_rows((_support_features(row)[None, :] @ weights))[0]
    return {int(delta): float(probabilities[index]) for index, delta in enumerate(head["classes"])}


def _support_head_accuracy(rows: list[Stage10Example], head: dict[str, Any]) -> dict[str, float]:
    support_rows = [row for row in rows if row.task == "phase_cued_retrieval"]
    if not support_rows:
        return {"row_count": 0.0, "accuracy": 0.0, "mean_true_delta_probability": 0.0, "mean_top_probability": 0.0}
    hits: list[float] = []
    true_probs: list[float] = []
    top_probs: list[float] = []
    for row in support_rows:
        distribution = _support_distribution(head, row)
        predicted_delta = sorted(distribution, key=lambda delta: (-distribution[delta], delta))[0]
        hits.append(1.0 if predicted_delta == int(row.reference_delta) else 0.0)
        true_probs.append(distribution.get(int(row.reference_delta), 0.0))
        top_probs.append(distribution[predicted_delta])
    return {
        "row_count": float(len(support_rows)),
        "accuracy": round(float(np.mean(hits)), 6),
        "mean_true_delta_probability": round(float(np.mean(true_probs)), 6),
        "mean_top_probability": round(float(np.mean(top_probs)), 6),
    }


def _learned_support_logits(row: Stage10Example, *, head: dict[str, Any], cue_scale: float, distance_scale: float) -> np.ndarray:
    distances = np.array([row.query_pos - index for index in range(row.query_pos)], dtype=float)
    logits = np.zeros(row.query_pos, dtype=float)
    if row.task == TINY_TEXT_TASK:
        query_tokens = row.tokens[max(0, row.query_pos - 4) : row.query_pos + 1]
        entity_ids = [token for token in query_tokens if 87 <= token < 96]
        if not entity_ids:
            return logits
        entity_id = int(entity_ids[0])
        for index in range(3, row.query_pos):
            if (
                row.tokens[index - 3] == TEXT_TOKEN_IDS["fact"]
                and row.tokens[index - 2] == entity_id
                and row.tokens[index - 1] == TEXT_TOKEN_IDS["is"]
            ):
                logits[index] += cue_scale
        return logits
    distribution = _support_distribution(head, row)
    support_scores = np.zeros(row.query_pos, dtype=float)
    for reference_delta, probability in distribution.items():
        exact_distance = (distances == float(reference_delta)).astype(float)
        phase_congruent = (((distances - float(reference_delta)) % 24.0) == 0.0).astype(float)
        support_scores += probability * (exact_distance + phase_congruent)
    farthest_prior = distances / max(1.0, float(row.query_pos))
    return cue_scale * support_scores + distance_scale * farthest_prior


def evaluate_learned_query_support_head(
    rows: list[Stage10Example],
    method_name: str,
    *,
    head: dict[str, Any],
    position_scale: float,
    cue_scale: float,
    distance_scale: float,
) -> dict[str, float]:
    from .stage49_copy_decoder_retrieval_repair_audit import _expected_calibration_error

    losses: list[float] = []
    reciprocal_ranks: list[float] = []
    top1_hits: list[float] = []
    target_probs: list[float] = []
    top1_confidences: list[float] = []
    for row in rows:
        logits = position_scale * np.asarray(positional_bias(row, _stage10_method_name(method_name)), dtype=float)
        logits = logits + _learned_support_logits(row, head=head, cue_scale=cue_scale, distance_scale=distance_scale)
        attention = _softmax(logits)
        values = np.zeros(VOCAB_SIZE, dtype=float)
        np.add.at(values, np.array(row.tokens[: row.query_pos], dtype=int), attention)
        ranked = _ranked_indices(values)
        rank = ranked.index(row.label_token) + 1
        target_probability = float(values[row.label_token])
        top1_token = ranked[0]
        top1_correct = 1.0 if top1_token == row.label_token else 0.0
        losses.append(-np.log(max(target_probability, 1e-12)))
        reciprocal_ranks.append(1.0 / float(rank))
        top1_hits.append(top1_correct)
        target_probs.append(target_probability)
        top1_confidences.append(float(values[top1_token]))
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


def _select_scales(
    validation_rows: list[Stage10Example],
    method_name: str,
    *,
    head: dict[str, Any],
    position_scales: tuple[float, ...],
    cue_scales: tuple[float, ...],
    distance_scales: tuple[float, ...],
) -> dict[str, Any]:
    scored: list[dict[str, Any]] = []
    for position_scale in position_scales:
        for cue_scale in cue_scales:
            for distance_scale in distance_scales:
                metrics = evaluate_learned_query_support_head(
                    validation_rows,
                    method_name,
                    head=head,
                    position_scale=position_scale,
                    cue_scale=cue_scale,
                    distance_scale=distance_scale,
                )
                scored.append({"position_scale": position_scale, "cue_scale": cue_scale, "distance_scale": distance_scale, "metrics": metrics})
    selected = sorted(
        scored,
        key=lambda item: (
            item["metrics"]["top1_accuracy"],
            item["metrics"]["mrr"],
            item["metrics"]["mean_target_probability"],
            -item["metrics"]["loss"],
            -abs(item["position_scale"]),
            -abs(item["cue_scale"]),
            -abs(item["distance_scale"]),
        ),
        reverse=True,
    )[0]
    return {
        "selected_position_scale": selected["position_scale"],
        "selected_cue_scale": selected["cue_scale"],
        "selected_distance_scale": selected["distance_scale"],
        "validation_selection_metrics": selected["metrics"],
    }


def _decision(aggregate_table: list[dict[str, Any]], *, support_head_summary: dict[str, dict[str, float]]) -> dict[str, Any]:
    retrieval_best = {task: _best_row(aggregate_table, task_name=task) for task in RETRIEVAL_TASKS}
    retrieval_solved = [task for task, row in retrieval_best.items() if row["test_top1_accuracy_mean"] >= GENERALIZATION_TOP1_THRESHOLD]
    no_position_solved = [
        task
        for task in RETRIEVAL_TASKS
        for row in aggregate_table
        if row["task"] == task and row["method"] == "no_position" and row["test_top1_accuracy_mean"] >= GENERALIZATION_TOP1_THRESHOLD
    ]
    phasewrap_best = [task for task, row in retrieval_best.items() if row["method"].startswith("phasewrap")]
    mean_support_accuracy = round(float(np.mean([row["test_accuracy"] for row in support_head_summary.values()])), 6)
    if "phase_cued_retrieval" in retrieval_solved and "phase_cued_retrieval" in no_position_solved:
        decision = "LEARNED_QUERY_SUPPORT_HEAD_SOLVES_PHASE_CUED_NOT_PROMOTION"
        boundary = "A learned visible query-support head solves phase-cued retrieval for no-position too; this is learned cue evidence, not positional-method promotion."
    elif retrieval_solved:
        decision = "LEARNED_QUERY_SUPPORT_HEAD_PARTIAL_RETRIEVAL"
        boundary = "A learned visible query-support head solves at least one retrieval lane but not the full retrieval set."
    else:
        decision = "LEARNED_QUERY_SUPPORT_HEAD_RETRIEVAL_FAILED"
        boundary = "A learned visible query-support head does not solve retrieval."
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
        "mean_phase_cued_test_support_head_accuracy": mean_support_accuracy,
        "claim_boundary": boundary,
    }


def _serializable_head(head: dict[str, Any]) -> dict[str, Any]:
    return {
        "classes": list(head["classes"]),
        "optimizer": head["optimizer"],
        "epochs": head["epochs"],
        "learning_rate": head["learning_rate"],
        "training_history": head["training_history"],
        "final_training_loss": head["final_training_loss"],
        "final_train_support_accuracy": head["final_train_support_accuracy"],
        "weights": np.asarray(head["weights"], dtype=float).round(8).tolist(),
    }


def run_stage75_audit(
    *,
    seeds: tuple[int, ...] = DEFAULT_AUDIT_SEEDS,
    examples_per_length: int = DEFAULT_EXAMPLES_PER_LENGTH,
    method_names: tuple[str, ...] = METHOD_NAMES,
    position_scales: tuple[float, ...] = DEFAULT_POSITION_SCALES,
    cue_scales: tuple[float, ...] = DEFAULT_CUE_SCALES,
    distance_scales: tuple[float, ...] = DEFAULT_DISTANCE_SCALES,
    support_head_epochs: int = DEFAULT_SUPPORT_HEAD_EPOCHS,
    support_head_learning_rate: float = DEFAULT_SUPPORT_HEAD_LEARNING_RATE,
) -> dict[str, Any]:
    splits_by_task = make_stage10_splits(seeds=seeds, examples_per_length=examples_per_length)
    run_table: list[dict[str, Any]] = []
    failed_runs: list[dict[str, Any]] = []
    support_heads: dict[str, dict[str, Any]] = {}
    support_head_summary: dict[str, dict[str, float]] = {}
    for held_out_seed in seeds:
        cross_seed_train_rows = [
            row
            for splits in splits_by_task.values()
            for row in splits["train"]
            if row.seed != held_out_seed
        ]
        head = train_query_support_head(
            cross_seed_train_rows,
            epochs=support_head_epochs,
            learning_rate=support_head_learning_rate,
        )
        support_heads[str(held_out_seed)] = _serializable_head(head)
        phase_test_rows = [
            row
            for row in splits_by_task["phase_cued_retrieval"]["test"]
            if row.seed == held_out_seed
        ]
        support_head_summary[str(held_out_seed)] = {
            "train_accuracy": head["final_train_support_accuracy"],
            "test_accuracy": _support_head_accuracy(phase_test_rows, head)["accuracy"],
            "test_mean_true_delta_probability": _support_head_accuracy(phase_test_rows, head)["mean_true_delta_probability"],
            "test_mean_top_probability": _support_head_accuracy(phase_test_rows, head)["mean_top_probability"],
        }
        for task_name, splits in splits_by_task.items():
            train_rows = [row for row in splits["train"] if row.seed == held_out_seed]
            validation_rows = [row for row in splits["validation"] if row.seed == held_out_seed]
            test_rows = [row for row in splits["test"] if row.seed == held_out_seed]
            for method_name in method_names:
                try:
                    selected = _select_scales(
                        validation_rows,
                        method_name,
                        head=head,
                        position_scales=position_scales,
                        cue_scales=cue_scales,
                        distance_scales=distance_scales,
                    )
                    row: dict[str, Any] = {
                        "task": task_name,
                        "seed": held_out_seed,
                        "method": method_name,
                        "stage10_method_alias": _stage10_method_name(method_name),
                        "train_row_count": len(train_rows),
                        "validation_row_count": len(validation_rows),
                        "test_row_count": len(test_rows),
                        "support_head_class_count": len(head["classes"]),
                        "support_head_train_accuracy": head["final_train_support_accuracy"],
                        "support_head_test_accuracy": (
                            support_head_summary[str(held_out_seed)]["test_accuracy"]
                            if task_name == "phase_cued_retrieval"
                            else 1.0
                        ),
                        **selected,
                    }
                    for split_name, split_rows in (("train", train_rows), ("validation", validation_rows), ("test", test_rows)):
                        metrics = evaluate_learned_query_support_head(
                            split_rows,
                            method_name,
                            head=head,
                            position_scale=selected["selected_position_scale"],
                            cue_scale=selected["selected_cue_scale"],
                            distance_scale=selected["selected_distance_scale"],
                        )
                        for metric_name, value in metrics.items():
                            if metric_name != "row_count":
                                row[f"{split_name}_{metric_name}"] = value
                    run_table.append(row)
                except Exception as exc:  # pragma: no cover
                    failed_runs.append({"task": task_name, "seed": held_out_seed, "method": method_name, "error": str(exc)})
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
        "schema_version": STAGE75_SCHEMA_VERSION,
        "stage": "stage75_learned_query_support_head_audit",
        "status": "completed",
        "dataset": "synthetic_stage10_original_rows_leave_one_seed_learned_query_support_v1",
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "source_stage": "stage74_leave_one_seed_query_support_audit",
        "method_names": list(method_names),
        "tasks": list(TASK_NAMES),
        "seeds": list(seeds),
        "examples_per_length": examples_per_length,
        "support_head_epochs": support_head_epochs,
        "support_head_learning_rate": support_head_learning_rate,
        "support_heads": support_heads,
        "support_head_summary": support_head_summary,
        "model": {
            "type": "leave_one_seed_softmax_query_support_head_plus_copy_readout",
            "value_output_mode": "deterministic copied prefix-token mass",
            "metadata_excluded": ["held-out seed train rows", "hard query-support lookup", "row.reference_delta exact value at evaluation", "row.target_pos", "row.target_delta"],
        },
        "claim_boundary": _claim_boundary(),
        "failed_runs": failed_runs,
        "run_table": run_table,
        "aggregate_table": aggregate_table,
        "ranking_table": ranking_table,
        "decision": _decision(aggregate_table, support_head_summary=support_head_summary),
    }


def write_stage75_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    return write_stage56_outputs(result, output_dir)


def print_stage75_summary(result: dict[str, Any]) -> None:
    print_stage57_summary(result)
