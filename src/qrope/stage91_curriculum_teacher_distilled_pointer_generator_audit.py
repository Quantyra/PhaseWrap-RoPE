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
    _decision as base_decision,
    write_stage52_outputs,
)
from .stage54_attention_supervised_two_block_audit import _aggregate
from .stage61_support_complete_two_block_audit import DEFAULT_AUDIT_SEEDS, DEFAULT_EXAMPLES_PER_LENGTH
from .stage61_support_complete_two_block_audit import _support_coverage
from .stage61_support_complete_two_block_audit import build_blocked_result as build_stage61_blocked_result
from .stage61_support_complete_two_block_audit import print_stage61_summary
from .stage64_two_block_pointer_generator_capacity_audit import _add_copy_gate_aggregates, _attend
from .stage84_support_auxiliary_pointer_generator_audit import (
    DEFAULT_SUPPORT_AUX_WEIGHT,
    _add_support_accuracy_aggregates,
    _support_classes,
    _support_index,
)


STAGE91_SCHEMA_VERSION = "qrope_stage91_curriculum_teacher_distilled_pointer_generator_audit_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage91_curriculum_teacher_distilled_pointer_generator_audit"
DEFAULT_EPOCHS = 10
DEFAULT_TARGET_ATTENTION_AUX_WEIGHT = 0.6
DEFAULT_TEACHER_DISTILLATION_WEIGHT = 0.8


def _claim_boundary() -> dict[str, list[str]]:
    return {
        "supported": [
            "A no-credential support-complete length-curriculum three-block pointer-generator audit with training-only structural teacher distillation.",
            "Evidence about whether adding length-40 curriculum rows lets Stage88 structural retrieval routes distill into free evaluation without structural copy routing.",
            "Fair RoPE/ALiBI/sinusoidal/no-position/PhaseWrap comparisons with failed-run retention.",
        ],
        "excluded": [
            "production transformer superiority",
            "full transformer-scale validation",
            "a claim that PhaseWrap-RoPE replaces RoPE",
            "a claim that a length-curriculum toy pointer-generator is full transformer-scale validation",
            "a claim that training-time structural teachers are positional-method promotion evidence by themselves",
            "broad quantum advantage",
        ],
    }


def build_blocked_result(*, reason: str = "missing_optional_autograd_dependency") -> dict[str, Any]:
    result = build_stage61_blocked_result(reason=reason)
    result.update(
        {
            "schema_version": STAGE91_SCHEMA_VERSION,
            "stage": "stage91_curriculum_teacher_distilled_pointer_generator_audit",
            "source_stage": "stage90_three_block_teacher_distilled_pointer_generator_audit",
            "training_tasks": list(TASK_NAMES),
            "epochs": DEFAULT_EPOCHS,
            "support_aux_weight": DEFAULT_SUPPORT_AUX_WEIGHT,
            "target_attention_aux_weight": DEFAULT_TARGET_ATTENTION_AUX_WEIGHT,
            "teacher_distillation_weight": DEFAULT_TEACHER_DISTILLATION_WEIGHT,
            "claim_boundary": _claim_boundary(),
        }
    )
    return result


def _init_three_block_vector(seed: int, support_class_count: int) -> np.ndarray:
    rng = np.random.default_rng(seed + 90_000)
    matrix_size = MODEL_DIM * MODEL_DIM
    base_size = VOCAB_SIZE * MODEL_DIM + 12 * matrix_size + MODEL_DIM * VOCAB_SIZE + 2
    base = rng.normal(0.0, 0.035, size=base_size)
    base[-2] = 1.0
    base[-1] = 1.5
    support_head = rng.normal(0.0, 0.035, size=MODEL_DIM * support_class_count)
    return np.concatenate([base, support_head])


def _unpack_three_block(vector: Any, support_class_count: int):
    import autograd.numpy as anp

    index = 0
    emb_size = VOCAB_SIZE * MODEL_DIM
    emb = anp.reshape(vector[index : index + emb_size], (VOCAB_SIZE, MODEL_DIM))
    index += emb_size
    matrices = []
    matrix_size = MODEL_DIM * MODEL_DIM
    for _ in range(12):
        matrices.append(anp.reshape(vector[index : index + matrix_size], (MODEL_DIM, MODEL_DIM)))
        index += matrix_size
    output = anp.reshape(vector[index : index + MODEL_DIM * VOCAB_SIZE], (MODEL_DIM, VOCAB_SIZE))
    index += MODEL_DIM * VOCAB_SIZE
    pos_scale = vector[index]
    copy_logit = vector[index + 1]
    base_size = index + 2
    support_output = anp.reshape(vector[base_size : base_size + MODEL_DIM * support_class_count], (MODEL_DIM, support_class_count))
    return emb, matrices, output, pos_scale, copy_logit, support_output


def _row_outputs(vector: Any, row: Stage10Example, method_name: str, support_class_count: int):
    import autograd.numpy as anp

    emb, matrices, output, pos_scale, copy_logit, support_output = _unpack_three_block(vector, support_class_count)
    hidden = emb[anp.array(row.tokens[: row.query_pos])]
    query_hidden = emb[row.tokens[row.query_pos]]
    method_bias = anp.array(positional_bias(row, method_name))
    query_hidden, attention_1 = _attend(hidden, query_hidden, matrices, method_bias, pos_scale, 0)
    query_hidden, attention_2 = _attend(hidden, query_hidden, matrices, method_bias, pos_scale, 1)
    query_hidden, attention_3 = _attend(hidden, query_hidden, matrices, method_bias, pos_scale, 2)
    generator_probabilities = _softmax(anp.dot(query_hidden, output))
    copy_probabilities = anp.dot(attention_3, _copy_indicator(row))
    copy_gate = _sigmoid(copy_logit)
    support_probabilities = _softmax(anp.dot(query_hidden, support_output))
    return (
        copy_gate * copy_probabilities + (1.0 - copy_gate) * generator_probabilities,
        copy_gate,
        support_probabilities,
        attention_1,
        attention_2,
        attention_3,
    )


def _structural_teacher_distribution(row: Stage10Example, method_name: str) -> np.ndarray | None:
    if row.task == "phase_cued_retrieval":
        indicator = np.asarray(_copy_indicator(row), dtype=float)
        candidate_deltas = [delta for delta in range(row.reference_delta, row.query_pos, 24) if delta >= 3]
        selected_delta = int(candidate_deltas[-1]) if candidate_deltas else int(row.reference_delta)
        selected_position = int(row.query_pos - selected_delta)
        if 0 <= selected_position < row.query_pos:
            return indicator[selected_position]
        return None
    if row.task == "exact_offset_passkey":
        bias = np.asarray(positional_bias(row, method_name), dtype=float)
        if len(bias) != row.query_pos:
            raise ValueError(f"bias length {len(bias)} does not match prefix length {row.query_pos}")
        chosen_pos = int(np.argmax(bias))
        probabilities = np.zeros(VOCAB_SIZE, dtype=float)
        probabilities[int(row.tokens[chosen_pos])] = 1.0
        return probabilities
    return None


def _row_loss(
    vector: Any,
    row: Stage10Example,
    method_name: str,
    support_classes: tuple[int, ...],
    support_aux_weight: float,
    target_attention_aux_weight: float,
    teacher_distillation_weight: float,
):
    import autograd.numpy as anp

    probabilities, _, support_probabilities, attention_1, attention_2, attention_3 = _row_outputs(vector, row, method_name, len(support_classes))
    token_loss = -anp.log(probabilities[row.label_token] + 1e-12)
    losses = [token_loss]
    if row.task == "phase_cued_retrieval":
        support_index = _support_index(row, support_classes)
        if support_index >= 0:
            losses.append(support_aux_weight * -anp.log(support_probabilities[support_index] + 1e-12))
    if row.task in RETRIEVAL_TASKS:
        target_index = int(row.target_pos)
        target_attention_loss = -(anp.log(attention_1[target_index] + 1e-12) + anp.log(attention_2[target_index] + 1e-12) + anp.log(attention_3[target_index] + 1e-12)) / 3.0
        losses.append(target_attention_aux_weight * target_attention_loss)
        teacher = _structural_teacher_distribution(row, method_name)
        if teacher is not None:
            teacher_distribution = anp.array(teacher)
            teacher_loss = -anp.sum(teacher_distribution * anp.log(probabilities + 1e-12))
            losses.append(teacher_distillation_weight * teacher_loss)
    return anp.sum(anp.array(losses))


def _batch_loss(
    vector: Any,
    rows: list[Stage10Example],
    method_name: str,
    support_classes: tuple[int, ...],
    support_aux_weight: float,
    target_attention_aux_weight: float,
    teacher_distillation_weight: float,
):
    import autograd.numpy as anp

    return anp.mean(
        anp.array(
            [
                _row_loss(vector, row, method_name, support_classes, support_aux_weight, target_attention_aux_weight, teacher_distillation_weight)
                for row in rows
            ]
        )
    )


def train_three_block_teacher_distilled_pointer_generator_decoder(
    rows: list[Stage10Example],
    method_name: str,
    *,
    seed: int,
    epochs: int = DEFAULT_EPOCHS,
    learning_rate: float = DEFAULT_LEARNING_RATE,
    support_aux_weight: float = DEFAULT_SUPPORT_AUX_WEIGHT,
    target_attention_aux_weight: float = DEFAULT_TARGET_ATTENTION_AUX_WEIGHT,
    teacher_distillation_weight: float = DEFAULT_TEACHER_DISTILLATION_WEIGHT,
) -> dict[str, Any]:
    from autograd import grad

    support_classes = _support_classes(rows)
    vector = _init_three_block_vector(seed, len(support_classes))
    gradient = grad(
        lambda current: _batch_loss(
            current,
            rows,
            method_name,
            support_classes,
            support_aux_weight,
            target_attention_aux_weight,
            teacher_distillation_weight,
        )
    )
    moment = np.zeros_like(vector)
    velocity = np.zeros_like(vector)
    beta1 = 0.9
    beta2 = 0.999
    epsilon = 1e-8
    history: list[dict[str, float]] = []
    for epoch in range(1, epochs + 1):
        loss_value = float(
            _batch_loss(
                vector,
                rows,
                method_name,
                support_classes,
                support_aux_weight,
                target_attention_aux_weight,
                teacher_distillation_weight,
            )
        )
        grad_value = gradient(vector)
        moment = beta1 * moment + (1.0 - beta1) * grad_value
        velocity = beta2 * velocity + (1.0 - beta2) * (grad_value * grad_value)
        moment_hat = moment / (1.0 - beta1**epoch)
        velocity_hat = velocity / (1.0 - beta2**epoch)
        vector = vector - learning_rate * moment_hat / (np.sqrt(velocity_hat) + epsilon)
        if epoch in {1, epochs // 4, epochs // 2, (3 * epochs) // 4, epochs}:
            history.append({"epoch": epoch, "loss": round(loss_value, 6)})
    _, _, _, pos_scale, copy_logit, _ = _unpack_three_block(vector, len(support_classes))
    return {
        "weights": vector,
        "optimizer": "full_batch_adam_three_block_structural_teacher_distillation",
        "epochs": epochs,
        "learning_rate": learning_rate,
        "support_aux_weight": support_aux_weight,
        "target_attention_aux_weight": target_attention_aux_weight,
        "teacher_distillation_weight": teacher_distillation_weight,
        "support_classes": list(support_classes),
        "training_history": history,
        "final_training_loss": history[-1]["loss"],
        "learned_position_scale": round(float(pos_scale), 6),
        "learned_copy_gate": round(float(1.0 / (1.0 + math.exp(-float(copy_logit)))), 6),
    }


def _predict(vector: Any, row: Stage10Example, method_name: str, support_classes: tuple[int, ...]) -> tuple[float, int, float, float, int | None, float]:
    probabilities, copy_gate, support_probabilities, attention_1, attention_2, attention_3 = _row_outputs(vector, row, method_name, len(support_classes))
    probs = np.asarray(probabilities, dtype=float)
    sorted_indices = sorted(range(len(probs)), key=lambda index: (-float(probs[index]), index))
    predicted_support = int(np.argmax(np.asarray(support_probabilities, dtype=float))) if row.task == "phase_cued_retrieval" else None
    target_attention = (float(attention_1[row.target_pos]) + float(attention_2[row.target_pos]) + float(attention_3[row.target_pos])) / 3.0
    return (
        float(probs[row.label_token]),
        int(sorted_indices.index(row.label_token) + 1),
        float(probs[sorted_indices[0]]),
        float(copy_gate),
        predicted_support,
        target_attention,
    )


def evaluate_three_block_teacher_distilled_pointer_generator(rows: list[Stage10Example], method_name: str, vector: Any, support_classes: tuple[int, ...]) -> dict[str, float]:
    losses: list[float] = []
    reciprocal_ranks: list[float] = []
    top1_hits: list[float] = []
    target_probs: list[float] = []
    top1_confidences: list[float] = []
    copy_gates: list[float] = []
    support_hits: list[float] = []
    target_attentions: list[float] = []
    for row in rows:
        target_probability, rank, top1_confidence, copy_gate, predicted_support, target_attention = _predict(vector, row, method_name, support_classes)
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


def _decision(result: dict[str, Any]) -> dict[str, Any]:
    if result["status"] != "completed":
        return {}
    base = base_decision(result["aggregate_table"])
    retrieval_best_top1 = base["retrieval_best_top1"]
    generalized_retrieval = [task for task, value in retrieval_best_top1.items() if value >= GENERALIZATION_TOP1_THRESHOLD]
    attention_repaired = [
        task
        for task in RETRIEVAL_TASKS
        if max(row["test_mean_target_attention_mean"] for row in result["aggregate_table"] if row["task"] == task) >= GENERALIZATION_TOP1_THRESHOLD
    ]
    if not base["capacity_established"]:
        decision = "CURRICULUM_TEACHER_DISTILLED_POINTER_GENERATOR_CAPACITY_NOT_ESTABLISHED"
        boundary = "Length-curriculum structural teacher distillation does not establish train capacity."
    elif all(value >= GENERALIZATION_TOP1_THRESHOLD for value in retrieval_best_top1.values()):
        decision = "CURRICULUM_TEACHER_DISTILLED_POINTER_GENERATOR_RETRIEVAL_REVIEW_REQUIRED"
        boundary = "Length-curriculum training-time structural teacher distillation generalizes all retrieval lanes without evaluation-time structural routing; review method ordering before any claim update."
    elif generalized_retrieval:
        decision = "CURRICULUM_TEACHER_DISTILLED_POINTER_GENERATOR_PARTIAL_RETRIEVAL"
        boundary = "Length-curriculum training-time structural teacher distillation generalizes at least one retrieval lane but not the full retrieval gate."
    elif attention_repaired:
        decision = "CURRICULUM_TEACHER_DISTILLED_POINTER_GENERATOR_ATTENTION_REPAIRED_TOKEN_FAILED"
        boundary = "Length-curriculum structural teacher distillation repairs target attention for at least one retrieval lane, but free token retrieval remains below threshold."
    else:
        decision = "CURRICULUM_TEACHER_DISTILLED_POINTER_GENERATOR_WITHOUT_RETRIEVAL_GENERALIZATION"
        boundary = "Length-curriculum structural teacher distillation preserves capacity but does not repair free held-out retrieval generalization."
    return {
        **base,
        "decision": decision,
        "claim_boundary": boundary,
        "training_tasks": list(TASK_NAMES),
        "phase_cued_best_support_accuracy": max(row["test_support_accuracy_mean"] for row in result["aggregate_table"] if row["task"] == "phase_cued_retrieval"),
        "retrieval_attention_repaired_tasks": attention_repaired,
        "base_capacity_train_top1_threshold": CAPACITY_TRAIN_TOP1_THRESHOLD,
        "generalized_original_retrieval_tasks": generalized_retrieval,
    }


def run_stage91_audit(
    *,
    seeds: tuple[int, ...] = DEFAULT_AUDIT_SEEDS,
    examples_per_length: int = DEFAULT_EXAMPLES_PER_LENGTH,
    epochs: int = DEFAULT_EPOCHS,
    learning_rate: float = DEFAULT_LEARNING_RATE,
    support_aux_weight: float = DEFAULT_SUPPORT_AUX_WEIGHT,
    target_attention_aux_weight: float = DEFAULT_TARGET_ATTENTION_AUX_WEIGHT,
    teacher_distillation_weight: float = DEFAULT_TEACHER_DISTILLATION_WEIGHT,
    method_names: tuple[str, ...] = METHOD_NAMES,
) -> dict[str, Any]:
    if not autograd_available():
        return build_blocked_result()
    splits_by_task = make_stage10_splits(seeds=seeds, examples_per_length=examples_per_length)
    run_table: list[dict[str, Any]] = []
    failed_runs: list[dict[str, Any]] = []
    for seed in seeds:
        base_train_rows_by_task = {task_name: [row for row in splits_by_task[task_name]["train"] if row.seed == seed] for task_name in TASK_NAMES}
        curriculum_rows_by_task = {task_name: [row for row in splits_by_task[task_name]["validation"] if row.seed == seed] for task_name in TASK_NAMES}
        train_rows_by_task = {
            task_name: base_train_rows_by_task[task_name] + curriculum_rows_by_task[task_name]
            for task_name in TASK_NAMES
        }
        multitask_train_rows = [row for task_name in TASK_NAMES for row in train_rows_by_task[task_name]]
        for method_name in method_names:
            try:
                stage10_method = _stage10_method_name(method_name)
                trained = train_three_block_teacher_distilled_pointer_generator_decoder(
                    multitask_train_rows,
                    stage10_method,
                    seed=seed,
                    epochs=epochs,
                    learning_rate=learning_rate,
                    support_aux_weight=support_aux_weight,
                    target_attention_aux_weight=target_attention_aux_weight,
                    teacher_distillation_weight=teacher_distillation_weight,
                )
                support_classes = tuple(trained["support_classes"])
                for task_name in TASK_NAMES:
                    task_train_rows = train_rows_by_task[task_name]
                    validation_rows = curriculum_rows_by_task[task_name]
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
                        "teacher_distillation_weight": teacher_distillation_weight,
                        "optimizer": trained["optimizer"],
                        "training_tasks": list(TASK_NAMES),
                        "support_classes": list(support_classes),
                        "base_train_row_count": len(base_train_rows_by_task[task_name]),
                        "curriculum_row_count": len(curriculum_rows_by_task[task_name]),
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
                        metrics = evaluate_three_block_teacher_distilled_pointer_generator(split_rows, stage10_method, trained["weights"], support_classes)
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
        key=lambda row: (
            row["task"],
            row["test_top1_accuracy_mean"],
            row["test_mrr_mean"],
            row["test_mean_target_probability_mean"],
            row["test_mean_target_attention_mean"],
            -row["test_loss_mean"],
            row["method"],
        ),
        reverse=True,
    )
    result = {
        "schema_version": STAGE91_SCHEMA_VERSION,
        "stage": "stage91_curriculum_teacher_distilled_pointer_generator_audit",
        "status": "completed",
        "dataset": "synthetic_stage10_support_complete_rows_multitask_length40_curriculum_teacher_distilled_pointer_generator_v1",
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "source_rows": "stage10 original rows with support-complete same-seed multitask training plus length-40 curriculum rows",
        "source_stage": "stage90_three_block_teacher_distilled_pointer_generator_audit",
        "method_names": list(method_names),
        "tasks": list(TASK_NAMES),
        "training_tasks": list(TASK_NAMES),
        "seeds": list(seeds),
        "train_lengths": list(TRAIN_LENGTHS) + list(VALIDATION_LENGTHS),
        "base_train_lengths": list(TRAIN_LENGTHS),
        "curriculum_lengths": list(VALIDATION_LENGTHS),
        "validation_lengths": list(VALIDATION_LENGTHS),
        "test_lengths": list(TEST_LENGTHS),
        "examples_per_length": examples_per_length,
        "epochs": epochs,
        "learning_rate": learning_rate,
        "support_aux_weight": support_aux_weight,
        "target_attention_aux_weight": target_attention_aux_weight,
        "teacher_distillation_weight": teacher_distillation_weight,
        "support_coverage": _support_coverage(seeds, examples_per_length),
        "model": {
            "type": "three_block_pointer_generator_curriculum_teacher_distilled_decoder",
            "optimizer": "full_batch_adam_three_block_structural_teacher_distillation",
            "trained_parameters": "token embeddings, three q/k/v/o attention blocks, vocab output projection, positional scale, copy/vocab gate, support classifier from decoder query state",
            "value_output_mode": "learned mixture of vocab softmax and copied prefix-token mass",
            "support_supervision_policy": "support-class auxiliary loss is applied to phase-cued train rows only; evaluation does not receive support labels",
            "target_attention_supervision_policy": "target-position attention auxiliary loss is applied to retrieval train rows only; evaluation does not receive target_pos, target_delta, or reference_delta",
            "teacher_distillation_policy": "Stage88 structural copied-token teacher distributions are used on retrieval train rows only; validation and test evaluate the free learned pointer-generator distribution without structural routing",
            "row_policy": "train one same-seed model per method on all support-complete Stage10 task train rows plus length-40 curriculum rows; evaluate unchanged original test splits separately",
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


def write_stage91_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    return write_stage52_outputs(result, output_dir)


def print_stage91_summary(result: dict[str, Any]) -> None:
    print_stage61_summary(result)

