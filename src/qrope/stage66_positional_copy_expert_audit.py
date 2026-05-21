from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np

from .stage10_small_decoder_transformer import MODEL_DIM, TASK_NAMES, VOCAB_SIZE, Stage10Example, _softmax, autograd_available
from .stage10_small_decoder_transformer import make_stage10_splits, positional_bias
from .stage45_matched_decoder_only_gate import METHOD_NAMES, _stage10_method_name
from .stage50_learned_pointer_generator_decoder_audit import _copy_indicator, _sigmoid
from .stage52_two_block_decoder_feasibility_audit import (
    CAPACITY_TRAIN_TOP1_THRESHOLD,
    DEFAULT_LEARNING_RATE,
    GENERALIZATION_TOP1_THRESHOLD,
    _aggregate,
    _decision as base_decision,
    write_stage52_outputs,
)
from .stage61_support_complete_two_block_audit import (
    DEFAULT_AUDIT_SEEDS,
    DEFAULT_EXAMPLES_PER_LENGTH,
    _support_coverage,
    build_blocked_result as build_stage61_blocked_result,
    print_stage61_summary,
)
from .stage62_long_training_support_complete_audit import DEFAULT_EPOCHS
from .stage64_two_block_pointer_generator_capacity_audit import _add_copy_gate_aggregates, _attend


STAGE66_SCHEMA_VERSION = "qrope_stage66_positional_copy_expert_audit_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage66_positional_copy_expert_audit"


def _claim_boundary() -> dict[str, list[str]]:
    return {
        "supported": [
            "A no-credential positional-copy expert audit for the two-block learned pointer-generator path.",
            "Evidence about whether a direct method-bias copy expert repairs held-out 48/64 retrieval generalization.",
            "Fair RoPE/ALiBI/sinusoidal/no-position/PhaseWrap comparisons with failed-run retention.",
        ],
        "excluded": [
            "production transformer superiority",
            "full transformer-scale validation",
            "a claim that PhaseWrap-RoPE replaces RoPE",
            "a claim that a direct positional-copy expert is full decoder-only language-model validation",
            "a claim that output-path expert diagnostics are positional-method promotion evidence",
            "broad quantum advantage",
        ],
    }


def build_blocked_result(*, reason: str = "missing_optional_autograd_dependency") -> dict[str, Any]:
    result = build_stage61_blocked_result(reason=reason)
    result.update(
        {
            "schema_version": STAGE66_SCHEMA_VERSION,
            "stage": "stage66_positional_copy_expert_audit",
            "source_stage": "stage64_two_block_pointer_generator_capacity_audit",
            "epochs": DEFAULT_EPOCHS,
            "claim_boundary": _claim_boundary(),
        }
    )
    return result


def _init_vector(seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    matrix_size = MODEL_DIM * MODEL_DIM
    size = VOCAB_SIZE * MODEL_DIM + 8 * matrix_size + MODEL_DIM * VOCAB_SIZE + 4
    vector = rng.normal(0.0, 0.035, size=size)
    vector[-4] = 1.0
    vector[-3] = 1.5
    vector[-2] = 1.5
    vector[-1] = 0.0
    return vector


def _unpack(vector: Any):
    import autograd.numpy as anp

    index = 0
    emb_size = VOCAB_SIZE * MODEL_DIM
    emb = anp.reshape(vector[index : index + emb_size], (VOCAB_SIZE, MODEL_DIM))
    index += emb_size
    matrices = []
    matrix_size = MODEL_DIM * MODEL_DIM
    for _ in range(8):
        matrices.append(anp.reshape(vector[index : index + matrix_size], (MODEL_DIM, MODEL_DIM)))
        index += matrix_size
    output = anp.reshape(vector[index : index + MODEL_DIM * VOCAB_SIZE], (MODEL_DIM, VOCAB_SIZE))
    index += MODEL_DIM * VOCAB_SIZE
    return emb, matrices, output, vector[index], vector[index + 1], vector[index + 2], vector[index + 3]


def _expert_copy_probabilities(row: Stage10Example, method_name: str, expert_scale: Any):
    import autograd.numpy as anp

    expert_attention = _softmax(expert_scale * anp.array(positional_bias(row, method_name)))
    return anp.dot(expert_attention, _copy_indicator(row))


def _row_probabilities(vector: Any, row: Stage10Example, method_name: str):
    import autograd.numpy as anp

    emb, matrices, output, pos_scale, copy_logit, expert_scale, expert_logit = _unpack(vector)
    hidden = emb[anp.array(row.tokens[: row.query_pos])]
    query_hidden = emb[row.tokens[row.query_pos]]
    method_bias = anp.array(positional_bias(row, method_name))
    query_hidden, _ = _attend(hidden, query_hidden, matrices, method_bias, pos_scale, 0)
    query_hidden, final_attention = _attend(hidden, query_hidden, matrices, method_bias, pos_scale, 1)
    generator_probabilities = _softmax(anp.dot(query_hidden, output))
    learned_copy_probabilities = anp.dot(final_attention, _copy_indicator(row))
    copy_gate = _sigmoid(copy_logit)
    pointer_probabilities = copy_gate * learned_copy_probabilities + (1.0 - copy_gate) * generator_probabilities
    expert_probabilities = _expert_copy_probabilities(row, method_name, expert_scale)
    expert_gate = _sigmoid(expert_logit)
    return expert_gate * expert_probabilities + (1.0 - expert_gate) * pointer_probabilities, copy_gate, expert_gate, expert_scale


def _row_loss(vector: Any, row: Stage10Example, method_name: str):
    import autograd.numpy as anp

    probabilities, _, _, _ = _row_probabilities(vector, row, method_name)
    return -anp.log(probabilities[row.label_token] + 1e-12)


def _batch_loss(vector: Any, rows: list[Stage10Example], method_name: str):
    import autograd.numpy as anp

    return anp.mean(anp.array([_row_loss(vector, row, method_name) for row in rows]))


def train_positional_copy_expert_decoder(
    rows: list[Stage10Example],
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
    _, _, _, pos_scale, copy_logit, expert_scale, expert_logit = _unpack(vector)
    return {
        "weights": vector,
        "optimizer": "full_batch_adam",
        "epochs": epochs,
        "learning_rate": learning_rate,
        "training_history": history,
        "final_training_loss": history[-1]["loss"],
        "learned_position_scale": round(float(pos_scale), 6),
        "learned_copy_gate": round(float(1.0 / (1.0 + math.exp(-float(copy_logit)))), 6),
        "learned_expert_scale": round(float(expert_scale), 6),
        "learned_expert_gate": round(float(1.0 / (1.0 + math.exp(-float(expert_logit)))), 6),
    }


def _predict(vector: Any, row: Stage10Example, method_name: str) -> tuple[float, int, float, float, float, float]:
    import autograd.numpy as anp

    probabilities, copy_gate, expert_gate, expert_scale = _row_probabilities(vector, row, method_name)
    probs = np.asarray(probabilities, dtype=float)
    sorted_indices = sorted(range(len(probs)), key=lambda index: (-float(probs[index]), index))
    return (
        float(probs[row.label_token]),
        int(sorted_indices.index(row.label_token) + 1),
        float(probs[sorted_indices[0]]),
        float(anp.asarray(copy_gate)),
        float(anp.asarray(expert_gate)),
        float(anp.asarray(expert_scale)),
    )


def evaluate_positional_copy_expert_decoder(rows: list[Stage10Example], method_name: str, vector: Any) -> dict[str, float]:
    losses: list[float] = []
    reciprocal_ranks: list[float] = []
    top1_hits: list[float] = []
    target_probs: list[float] = []
    top1_confidences: list[float] = []
    copy_gates: list[float] = []
    expert_gates: list[float] = []
    expert_scales: list[float] = []
    for row in rows:
        target_probability, rank, top1_confidence, copy_gate, expert_gate, expert_scale = _predict(vector, row, method_name)
        losses.append(-math.log(max(target_probability, 1e-12)))
        reciprocal_ranks.append(1.0 / float(rank))
        top1_hits.append(1.0 if rank == 1 else 0.0)
        target_probs.append(target_probability)
        top1_confidences.append(top1_confidence)
        copy_gates.append(copy_gate)
        expert_gates.append(expert_gate)
        expert_scales.append(expert_scale)
    mean_loss = float(np.mean(losses))
    from .stage10_small_decoder_transformer import _expected_calibration_error

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
        "mean_expert_gate": round(float(np.mean(expert_gates)), 6),
        "mean_expert_scale": round(float(np.mean(expert_scales)), 6),
    }


def _decision(result: dict[str, Any]) -> dict[str, Any]:
    if result["status"] != "completed":
        return {}
    base = base_decision(result["aggregate_table"])
    if not base["capacity_established"]:
        decision = "POSITIONAL_COPY_EXPERT_CAPACITY_NOT_ESTABLISHED"
        boundary = "The positional-copy expert mixture does not preserve train capacity."
    elif all(value >= GENERALIZATION_TOP1_THRESHOLD for value in base["retrieval_best_top1"].values()):
        decision = "POSITIONAL_COPY_EXPERT_RETRIEVAL_REVIEW_REQUIRED"
        boundary = "The positional-copy expert mixture generalizes retrieval; review method ordering before any claim update."
    elif base["retrieval_generalized_tasks"]:
        decision = "POSITIONAL_COPY_EXPERT_PARTIAL_RETRIEVAL_GENERALIZATION"
        boundary = "The positional-copy expert mixture repairs at least one retrieval lane but not the full retrieval set."
    else:
        decision = "POSITIONAL_COPY_EXPERT_WITHOUT_RETRIEVAL_GENERALIZATION"
        boundary = "The positional-copy expert mixture preserves capacity but does not generalize retrieval."
    return {
        **base,
        "decision": decision,
        "claim_boundary": boundary,
        "base_capacity_train_top1_threshold": CAPACITY_TRAIN_TOP1_THRESHOLD,
    }


def _add_expert_aggregates(aggregate_table: list[dict[str, Any]], run_table: list[dict[str, Any]]) -> list[dict[str, Any]]:
    aggregate_table = _add_copy_gate_aggregates(aggregate_table, run_table)
    for aggregate_row in aggregate_table:
        rows = [row for row in run_table if row["task"] == aggregate_row["task"] and row["method"] == aggregate_row["method"]]
        if not rows:
            continue
        aggregate_row["learned_expert_gate_mean"] = round(float(np.mean([row["learned_expert_gate"] for row in rows])), 6)
        aggregate_row["learned_expert_scale_mean"] = round(float(np.mean([row["learned_expert_scale"] for row in rows])), 6)
        for split_name in ("train", "validation", "test"):
            aggregate_row[f"{split_name}_mean_expert_gate_mean"] = round(
                float(np.mean([row[f"{split_name}_mean_expert_gate"] for row in rows])),
                6,
            )
            aggregate_row[f"{split_name}_mean_expert_scale_mean"] = round(
                float(np.mean([row[f"{split_name}_mean_expert_scale"] for row in rows])),
                6,
            )
    return aggregate_table


def run_stage66_audit(
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
                    trained = train_positional_copy_expert_decoder(
                        train_rows,
                        stage10_method,
                        seed=seed,
                        epochs=epochs,
                        learning_rate=learning_rate,
                    )
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
                        "learned_position_scale": trained["learned_position_scale"],
                        "learned_copy_gate": trained["learned_copy_gate"],
                        "learned_expert_gate": trained["learned_expert_gate"],
                        "learned_expert_scale": trained["learned_expert_scale"],
                        "training_history": trained["training_history"],
                    }
                    for split_name, split_rows in (("train", train_rows), ("validation", validation_rows), ("test", test_rows)):
                        metrics = evaluate_positional_copy_expert_decoder(split_rows, stage10_method, trained["weights"])
                        for metric_name, value in metrics.items():
                            if metric_name != "row_count":
                                row[f"{split_name}_{metric_name}"] = value
                    run_table.append(row)
                except Exception as exc:  # pragma: no cover - retained for artifact completeness.
                    failed_runs.append({"task": task_name, "seed": seed, "method": method_name, "error": str(exc)})
    aggregate_table = _add_expert_aggregates(_aggregate(run_table, failed_runs), run_table)
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
        "schema_version": STAGE66_SCHEMA_VERSION,
        "stage": "stage66_positional_copy_expert_audit",
        "status": "completed",
        "dataset": "synthetic_small_decoder_train_short_test_long_v1",
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "source_rows": "stage10/stage45 matched decoder-only rows",
        "source_stage": "stage64_two_block_pointer_generator_capacity_audit",
        "method_names": list(method_names),
        "tasks": list(TASK_NAMES),
        "seeds": list(seeds),
        "examples_per_length": examples_per_length,
        "epochs": epochs,
        "learning_rate": learning_rate,
        "support_coverage": _support_coverage(seeds, examples_per_length),
        "model": {
            "type": "two_block_pointer_generator_with_learned_positional_copy_expert",
            "model_dim": MODEL_DIM,
            "vocab_size": VOCAB_SIZE,
            "optimizer": "full_batch_adam",
            "trained_parameters": "token embeddings, two q/k/v/o attention blocks, vocab output projection, positional scale, copy/vocab gate, positional expert scale, pointer/expert gate",
            "value_output_mode": "learned mixture of vocab softmax, learned attention copy, and direct method-bias positional copy",
            "expert_policy": "direct copy distribution is computed from the same positional bias available to the tested method",
        },
        "claim_boundary": _claim_boundary(),
        "failed_runs": failed_runs,
        "run_table": run_table,
        "aggregate_table": aggregate_table,
        "ranking_table": ranking_table,
    }
    result["decision"] = _decision(result)
    return result


def write_stage66_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    return write_stage52_outputs(result, output_dir)


def print_stage66_summary(result: dict[str, Any]) -> None:
    print_stage61_summary(result)
