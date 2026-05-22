from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np

from .stage10_small_decoder_transformer import (
    MODEL_DIM,
    TASK_NAMES,
    TEST_LENGTHS,
    TRAIN_LENGTHS,
    VALIDATION_LENGTHS,
    VOCAB_SIZE,
    Stage10Example,
    _expected_calibration_error,
    _softmax,
    autograd_available,
    make_stage10_splits,
    positional_bias,
)
from .stage45_matched_decoder_only_gate import METHOD_NAMES, _stage10_method_name
from .stage50_learned_pointer_generator_decoder_audit import _copy_indicator, _sigmoid
from .stage52_two_block_decoder_feasibility_audit import (
    CAPACITY_TRAIN_TOP1_THRESHOLD,
    DEFAULT_LEARNING_RATE,
    GENERALIZATION_TOP1_THRESHOLD,
    RETRIEVAL_TASKS,
    _aggregate,
    _decision as base_decision,
    write_stage52_outputs,
)
from .stage61_support_complete_two_block_audit import DEFAULT_AUDIT_SEEDS, DEFAULT_EXAMPLES_PER_LENGTH
from .stage61_support_complete_two_block_audit import _support_coverage
from .stage61_support_complete_two_block_audit import build_blocked_result as build_stage61_blocked_result
from .stage61_support_complete_two_block_audit import print_stage61_summary
from .stage62_long_training_support_complete_audit import DEFAULT_EPOCHS
from .stage64_two_block_pointer_generator_capacity_audit import _add_copy_gate_aggregates, _attend, _init_vector, _unpack


STAGE84_SCHEMA_VERSION = "qrope_stage84_support_auxiliary_pointer_generator_audit_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage84_support_auxiliary_pointer_generator_audit"
DEFAULT_SUPPORT_AUX_WEIGHT = 0.7


def _claim_boundary() -> dict[str, list[str]]:
    return {
        "supported": [
            "A no-credential support-complete two-block pointer-generator audit with an in-decoder auxiliary support classifier.",
            "Evidence about whether explicit support supervision inside the decoder helps learn support-to-token routing.",
            "Fair RoPE/ALiBI/sinusoidal/no-position/PhaseWrap comparisons with failed-run retention.",
        ],
        "excluded": [
            "production transformer superiority",
            "full transformer-scale validation",
            "a claim that PhaseWrap-RoPE replaces RoPE",
            "a claim that auxiliary support supervision is standard free decoder-only language modeling",
            "a claim that support-supervised decoder diagnostics are positional-method promotion evidence by themselves",
            "broad quantum advantage",
        ],
    }


def build_blocked_result(*, reason: str = "missing_optional_autograd_dependency") -> dict[str, Any]:
    result = build_stage61_blocked_result(reason=reason)
    result.update(
        {
            "schema_version": STAGE84_SCHEMA_VERSION,
            "stage": "stage84_support_auxiliary_pointer_generator_audit",
            "source_stage": "stage83_nonlinear_support_routing_bridge_audit",
            "training_tasks": list(TASK_NAMES),
            "epochs": DEFAULT_EPOCHS,
            "support_aux_weight": DEFAULT_SUPPORT_AUX_WEIGHT,
            "claim_boundary": _claim_boundary(),
        }
    )
    return result


def _support_classes(rows: list[Stage10Example]) -> tuple[int, ...]:
    return tuple(sorted({int(row.reference_delta) for row in rows if row.task == "phase_cued_retrieval"}))


def _support_index(row: Stage10Example, support_classes: tuple[int, ...]) -> int:
    try:
        return support_classes.index(int(row.reference_delta))
    except ValueError:
        return -1


def _init_support_aux_vector(seed: int, support_class_count: int) -> np.ndarray:
    rng = np.random.default_rng(seed + 84_000)
    base = _init_vector(seed)
    support_head = rng.normal(0.0, 0.035, size=MODEL_DIM * support_class_count)
    return np.concatenate([base, support_head])


def _unpack_support_aux(vector: Any, support_class_count: int):
    import autograd.numpy as anp

    base_size = VOCAB_SIZE * MODEL_DIM + 8 * MODEL_DIM * MODEL_DIM + MODEL_DIM * VOCAB_SIZE + 2
    emb, matrices, output, pos_scale, copy_logit = _unpack(vector[:base_size])
    support_output = anp.reshape(vector[base_size : base_size + MODEL_DIM * support_class_count], (MODEL_DIM, support_class_count))
    return emb, matrices, output, pos_scale, copy_logit, support_output


def _row_outputs(vector: Any, row: Stage10Example, method_name: str, support_class_count: int):
    import autograd.numpy as anp

    emb, matrices, output, pos_scale, copy_logit, support_output = _unpack_support_aux(vector, support_class_count)
    hidden = emb[anp.array(row.tokens[: row.query_pos])]
    query_hidden = emb[row.tokens[row.query_pos]]
    method_bias = anp.array(positional_bias(row, method_name))
    query_hidden, _ = _attend(hidden, query_hidden, matrices, method_bias, pos_scale, 0)
    query_hidden, final_attention = _attend(hidden, query_hidden, matrices, method_bias, pos_scale, 1)
    generator_probabilities = _softmax(anp.dot(query_hidden, output))
    copy_probabilities = anp.dot(final_attention, _copy_indicator(row))
    copy_gate = _sigmoid(copy_logit)
    support_probabilities = _softmax(anp.dot(query_hidden, support_output))
    return copy_gate * copy_probabilities + (1.0 - copy_gate) * generator_probabilities, copy_gate, support_probabilities


def _row_loss(vector: Any, row: Stage10Example, method_name: str, support_classes: tuple[int, ...], support_aux_weight: float):
    import autograd.numpy as anp

    probabilities, _, support_probabilities = _row_outputs(vector, row, method_name, len(support_classes))
    token_loss = -anp.log(probabilities[row.label_token] + 1e-12)
    if row.task != "phase_cued_retrieval":
        return token_loss
    support_index = _support_index(row, support_classes)
    if support_index < 0:
        return token_loss
    support_loss = -anp.log(support_probabilities[support_index] + 1e-12)
    return token_loss + support_aux_weight * support_loss


def _batch_loss(vector: Any, rows: list[Stage10Example], method_name: str, support_classes: tuple[int, ...], support_aux_weight: float):
    import autograd.numpy as anp

    return anp.mean(anp.array([_row_loss(vector, row, method_name, support_classes, support_aux_weight) for row in rows]))


def train_support_auxiliary_pointer_generator_decoder(
    rows: list[Stage10Example],
    method_name: str,
    *,
    seed: int,
    epochs: int = DEFAULT_EPOCHS,
    learning_rate: float = DEFAULT_LEARNING_RATE,
    support_aux_weight: float = DEFAULT_SUPPORT_AUX_WEIGHT,
) -> dict[str, Any]:
    from autograd import grad

    support_classes = _support_classes(rows)
    vector = _init_support_aux_vector(seed, len(support_classes))
    gradient = grad(lambda current: _batch_loss(current, rows, method_name, support_classes, support_aux_weight))
    moment = np.zeros_like(vector)
    velocity = np.zeros_like(vector)
    beta1 = 0.9
    beta2 = 0.999
    epsilon = 1e-8
    history: list[dict[str, float]] = []
    for epoch in range(1, epochs + 1):
        loss_value = float(_batch_loss(vector, rows, method_name, support_classes, support_aux_weight))
        grad_value = gradient(vector)
        moment = beta1 * moment + (1.0 - beta1) * grad_value
        velocity = beta2 * velocity + (1.0 - beta2) * (grad_value * grad_value)
        moment_hat = moment / (1.0 - beta1**epoch)
        velocity_hat = velocity / (1.0 - beta2**epoch)
        vector = vector - learning_rate * moment_hat / (np.sqrt(velocity_hat) + epsilon)
        if epoch in {1, epochs // 4, epochs // 2, (3 * epochs) // 4, epochs}:
            history.append({"epoch": epoch, "loss": round(loss_value, 6)})
    _, _, _, pos_scale, copy_logit, _ = _unpack_support_aux(vector, len(support_classes))
    return {
        "weights": vector,
        "optimizer": "full_batch_adam_support_auxiliary",
        "epochs": epochs,
        "learning_rate": learning_rate,
        "support_aux_weight": support_aux_weight,
        "support_classes": list(support_classes),
        "training_history": history,
        "final_training_loss": history[-1]["loss"],
        "learned_position_scale": round(float(pos_scale), 6),
        "learned_copy_gate": round(float(1.0 / (1.0 + math.exp(-float(copy_logit)))), 6),
    }


def _predict(vector: Any, row: Stage10Example, method_name: str, support_classes: tuple[int, ...]) -> tuple[float, int, float, float, int | None]:
    probabilities, copy_gate, support_probabilities = _row_outputs(vector, row, method_name, len(support_classes))
    probs = np.asarray(probabilities, dtype=float)
    sorted_indices = sorted(range(len(probs)), key=lambda index: (-float(probs[index]), index))
    predicted_support = int(np.argmax(np.asarray(support_probabilities, dtype=float))) if row.task == "phase_cued_retrieval" else None
    return float(probs[row.label_token]), int(sorted_indices.index(row.label_token) + 1), float(probs[sorted_indices[0]]), float(copy_gate), predicted_support


def evaluate_support_auxiliary_pointer_generator(rows: list[Stage10Example], method_name: str, vector: Any, support_classes: tuple[int, ...]) -> dict[str, float]:
    losses: list[float] = []
    reciprocal_ranks: list[float] = []
    top1_hits: list[float] = []
    target_probs: list[float] = []
    top1_confidences: list[float] = []
    copy_gates: list[float] = []
    support_hits: list[float] = []
    for row in rows:
        target_probability, rank, top1_confidence, copy_gate, predicted_support = _predict(vector, row, method_name, support_classes)
        losses.append(-math.log(max(target_probability, 1e-12)))
        reciprocal_ranks.append(1.0 / float(rank))
        top1_hits.append(1.0 if rank == 1 else 0.0)
        target_probs.append(target_probability)
        top1_confidences.append(top1_confidence)
        copy_gates.append(copy_gate)
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
    }


def _add_support_accuracy_aggregates(aggregate_table: list[dict[str, Any]], run_table: list[dict[str, Any]]) -> list[dict[str, Any]]:
    for aggregate_row in aggregate_table:
        rows = [row for row in run_table if row["task"] == aggregate_row["task"] and row["method"] == aggregate_row["method"]]
        if not rows:
            continue
        for split_name in ("train", "validation", "test"):
            aggregate_row[f"{split_name}_support_accuracy_mean"] = round(float(np.mean([row[f"{split_name}_support_accuracy"] for row in rows])), 6)
    return aggregate_table


def _decision(result: dict[str, Any]) -> dict[str, Any]:
    if result["status"] != "completed":
        return {}
    base = base_decision(result["aggregate_table"])
    retrieval_best_top1 = base["retrieval_best_top1"]
    generalized_retrieval = [task for task, value in retrieval_best_top1.items() if value >= GENERALIZATION_TOP1_THRESHOLD]
    if not base["capacity_established"]:
        decision = "SUPPORT_AUXILIARY_POINTER_GENERATOR_CAPACITY_NOT_ESTABLISHED"
        boundary = "In-decoder support supervision does not establish train capacity."
    elif all(value >= GENERALIZATION_TOP1_THRESHOLD for value in retrieval_best_top1.values()):
        decision = "SUPPORT_AUXILIARY_POINTER_GENERATOR_RETRIEVAL_REVIEW_REQUIRED"
        boundary = "In-decoder support supervision generalizes all retrieval lanes; review method ordering before any claim update."
    elif generalized_retrieval:
        decision = "SUPPORT_AUXILIARY_POINTER_GENERATOR_PARTIAL_RETRIEVAL"
        boundary = "In-decoder support supervision generalizes at least one retrieval lane but not the full retrieval gate."
    else:
        decision = "SUPPORT_AUXILIARY_POINTER_GENERATOR_WITHOUT_RETRIEVAL_GENERALIZATION"
        boundary = "In-decoder support supervision preserves capacity but does not repair held-out retrieval generalization."
    return {
        **base,
        "decision": decision,
        "claim_boundary": boundary,
        "training_tasks": list(TASK_NAMES),
        "phase_cued_best_support_accuracy": max(row["test_support_accuracy_mean"] for row in result["aggregate_table"] if row["task"] == "phase_cued_retrieval"),
        "base_capacity_train_top1_threshold": CAPACITY_TRAIN_TOP1_THRESHOLD,
        "generalized_original_retrieval_tasks": generalized_retrieval,
    }


def run_stage84_audit(
    *,
    seeds: tuple[int, ...] = DEFAULT_AUDIT_SEEDS,
    examples_per_length: int = DEFAULT_EXAMPLES_PER_LENGTH,
    epochs: int = DEFAULT_EPOCHS,
    learning_rate: float = DEFAULT_LEARNING_RATE,
    support_aux_weight: float = DEFAULT_SUPPORT_AUX_WEIGHT,
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
                trained = train_support_auxiliary_pointer_generator_decoder(
                    multitask_train_rows,
                    stage10_method,
                    seed=seed,
                    epochs=epochs,
                    learning_rate=learning_rate,
                    support_aux_weight=support_aux_weight,
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
                        metrics = evaluate_support_auxiliary_pointer_generator(split_rows, stage10_method, trained["weights"], support_classes)
                        for metric_name, value in metrics.items():
                            if metric_name != "row_count":
                                row[f"{split_name}_{metric_name}"] = value
                    run_table.append(row)
            except Exception as exc:  # pragma: no cover - retained for artifact completeness.
                for task_name in TASK_NAMES:
                    failed_runs.append({"task": task_name, "seed": seed, "method": method_name, "error": str(exc)})
    aggregate_table = _add_support_accuracy_aggregates(_add_copy_gate_aggregates(_aggregate(run_table, failed_runs), run_table), run_table)
    ranking_table = sorted(
        aggregate_table,
        key=lambda row: (row["task"], row["test_top1_accuracy_mean"], row["test_mrr_mean"], row["test_mean_target_probability_mean"], -row["test_loss_mean"], row["method"]),
        reverse=True,
    )
    result = {
        "schema_version": STAGE84_SCHEMA_VERSION,
        "stage": "stage84_support_auxiliary_pointer_generator_audit",
        "status": "completed",
        "dataset": "synthetic_stage10_support_complete_rows_multitask_support_auxiliary_pointer_generator_v1",
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "source_rows": "stage10 original rows with support-complete same-seed multitask training",
        "source_stage": "stage83_nonlinear_support_routing_bridge_audit",
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
        "support_coverage": _support_coverage(seeds, examples_per_length),
        "model": {
            "type": "two_block_pointer_generator_support_auxiliary_decoder",
            "optimizer": "full_batch_adam_support_auxiliary",
            "trained_parameters": "token embeddings, two q/k/v/o attention blocks, vocab output projection, positional scale, copy/vocab gate, support classifier from decoder query state",
            "value_output_mode": "learned mixture of vocab softmax and copied prefix-token mass",
            "support_supervision_policy": "support-class auxiliary loss is applied to phase-cued train rows only; evaluation does not receive support labels",
            "row_policy": "train one same-seed model per method on all support-complete Stage10 task train rows; evaluate unchanged original task splits separately",
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


def write_stage84_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    return write_stage52_outputs(result, output_dir)


def print_stage84_summary(result: dict[str, Any]) -> None:
    print_stage61_summary(result)
