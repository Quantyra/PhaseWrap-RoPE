from __future__ import annotations

import math
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np

from .stage10_small_decoder_transformer import MODEL_DIM, TASK_NAMES, VOCAB_SIZE, Stage10Example, _softmax, autograd_available
from .stage45_matched_decoder_only_gate import METHOD_NAMES, _stage10_method_name
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
from .stage10_small_decoder_transformer import make_stage10_splits, positional_bias


STAGE63_SCHEMA_VERSION = "qrope_stage63_two_block_copy_output_capacity_audit_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage63_two_block_copy_output_capacity_audit"


def _claim_boundary() -> dict[str, list[str]]:
    return {
        "supported": [
            "A no-credential two-block copy-output capacity audit over the support-complete row family.",
            "Evidence about whether replacing learned vocab softmax with copied prefix-token mass repairs train capacity.",
            "Fair RoPE/ALiBI/sinusoidal/no-position/PhaseWrap comparisons with failed-run retention.",
        ],
        "excluded": [
            "production transformer superiority",
            "full transformer-scale validation",
            "a claim that PhaseWrap-RoPE replaces RoPE",
            "a claim that copy-output repair is equivalent to free learned value generation",
            "a claim that output-path capacity evidence is positional-method promotion evidence",
            "broad quantum advantage",
        ],
    }


def build_blocked_result(*, reason: str = "missing_optional_autograd_dependency") -> dict[str, Any]:
    result = build_stage61_blocked_result(reason=reason)
    result.update(
        {
            "schema_version": STAGE63_SCHEMA_VERSION,
            "stage": "stage63_two_block_copy_output_capacity_audit",
            "source_stage": "stage62_long_training_support_complete_audit",
            "epochs": DEFAULT_EPOCHS,
            "claim_boundary": _claim_boundary(),
        }
    )
    return result


def _init_vector(seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    matrix_size = MODEL_DIM * MODEL_DIM
    size = VOCAB_SIZE * MODEL_DIM + 8 * matrix_size + 1
    vector = rng.normal(0.0, 0.035, size=size)
    vector[-1] = 1.0
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
    return emb, matrices, vector[index]


def _attend(hidden: Any, query_hidden: Any, matrices: list[Any], method_bias: Any, pos_scale: Any, block_index: int):
    import autograd.numpy as anp

    offset = block_index * 4
    wq, wk, wv, wo = matrices[offset : offset + 4]
    query = anp.dot(query_hidden, wq)
    keys = anp.dot(hidden, wk)
    values = anp.dot(hidden, wv)
    logits = anp.dot(keys, query) / math.sqrt(float(MODEL_DIM))
    logits = logits + pos_scale * method_bias
    attention = _softmax(logits)
    context = anp.dot(attention, values)
    return anp.tanh(query_hidden + anp.dot(context, wo)), attention


@lru_cache(maxsize=None)
def _copy_indicator_array(tokens: tuple[int, ...], query_pos: int) -> np.ndarray:
    return np.array([[1.0 if token_id == vocab_id else 0.0 for vocab_id in range(VOCAB_SIZE)] for token_id in tokens[:query_pos]], dtype=float)


def _copy_indicator(row: Stage10Example):
    import autograd.numpy as anp

    return anp.array(_copy_indicator_array(row.tokens, row.query_pos))


def _row_probabilities(vector: Any, row: Stage10Example, method_name: str):
    import autograd.numpy as anp

    emb, matrices, pos_scale = _unpack(vector)
    hidden = emb[anp.array(row.tokens[: row.query_pos])]
    query_hidden = emb[row.tokens[row.query_pos]]
    method_bias = anp.array(positional_bias(row, method_name))
    query_hidden, _ = _attend(hidden, query_hidden, matrices, method_bias, pos_scale, 0)
    _, final_attention = _attend(hidden, query_hidden, matrices, method_bias, pos_scale, 1)
    return anp.dot(final_attention, _copy_indicator(row))


def _row_loss(vector: Any, row: Stage10Example, method_name: str):
    import autograd.numpy as anp

    probabilities = _row_probabilities(vector, row, method_name)
    return -anp.log(probabilities[row.label_token] + 1e-12)


def _batch_loss(vector: Any, rows: list[Stage10Example], method_name: str):
    import autograd.numpy as anp

    return anp.mean(anp.array([_row_loss(vector, row, method_name) for row in rows]))


def train_two_block_copy_decoder(
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
    _, _, pos_scale = _unpack(vector)
    return {
        "weights": vector,
        "optimizer": "full_batch_adam",
        "epochs": epochs,
        "learning_rate": learning_rate,
        "training_history": history,
        "final_training_loss": history[-1]["loss"],
        "learned_position_scale": round(float(pos_scale), 6),
    }


def _predict(vector: Any, row: Stage10Example, method_name: str) -> tuple[float, int, float]:
    probabilities = np.asarray(_row_probabilities(vector, row, method_name), dtype=float)
    sorted_indices = sorted(range(len(probabilities)), key=lambda index: (-float(probabilities[index]), index))
    return float(probabilities[row.label_token]), int(sorted_indices.index(row.label_token) + 1), float(probabilities[sorted_indices[0]])


def evaluate_two_block_copy_decoder(rows: list[Stage10Example], method_name: str, vector: Any) -> dict[str, float]:
    losses: list[float] = []
    reciprocal_ranks: list[float] = []
    top1_hits: list[float] = []
    target_probs: list[float] = []
    top1_confidences: list[float] = []
    for row in rows:
        target_probability, rank, top1_confidence = _predict(vector, row, method_name)
        losses.append(-math.log(max(target_probability, 1e-12)))
        reciprocal_ranks.append(1.0 / float(rank))
        top1_hits.append(1.0 if rank == 1 else 0.0)
        target_probs.append(target_probability)
        top1_confidences.append(top1_confidence)
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
    }


def _decision(result: dict[str, Any]) -> dict[str, Any]:
    if result["status"] != "completed":
        return {}
    base = base_decision(result["aggregate_table"])
    if not base["capacity_established"]:
        decision = "TWO_BLOCK_COPY_OUTPUT_CAPACITY_NOT_ESTABLISHED"
        boundary = "Copy output improves the output path but still does not establish learned two-block capacity."
    elif all(value >= GENERALIZATION_TOP1_THRESHOLD for value in base["retrieval_best_top1"].values()):
        decision = "TWO_BLOCK_COPY_OUTPUT_RETRIEVAL_REVIEW_REQUIRED"
        boundary = "Copy output establishes retrieval generalization; review method ordering before any claim update."
    else:
        decision = "TWO_BLOCK_COPY_OUTPUT_CAPACITY_WITHOUT_RETRIEVAL_GENERALIZATION"
        boundary = "Copy output establishes train capacity but does not generalize all retrieval lanes."
    return {
        **base,
        "decision": decision,
        "claim_boundary": boundary,
        "base_capacity_train_top1_threshold": CAPACITY_TRAIN_TOP1_THRESHOLD,
    }


def run_stage63_audit(
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
                    trained = train_two_block_copy_decoder(
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
                        "training_history": trained["training_history"],
                    }
                    for split_name, split_rows in (("train", train_rows), ("validation", validation_rows), ("test", test_rows)):
                        metrics = evaluate_two_block_copy_decoder(split_rows, stage10_method, trained["weights"])
                        for metric_name, value in metrics.items():
                            if metric_name != "row_count":
                                row[f"{split_name}_{metric_name}"] = value
                    run_table.append(row)
                except Exception as exc:  # pragma: no cover - retained for artifact completeness.
                    failed_runs.append({"task": task_name, "seed": seed, "method": method_name, "error": str(exc)})
    aggregate_table = _aggregate(run_table, failed_runs)
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
        "schema_version": STAGE63_SCHEMA_VERSION,
        "stage": "stage63_two_block_copy_output_capacity_audit",
        "status": "completed",
        "dataset": "synthetic_small_decoder_train_short_test_long_v1",
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "source_rows": "stage10/stage45 matched decoder-only rows",
        "source_stage": "stage62_long_training_support_complete_audit",
        "method_names": list(method_names),
        "tasks": list(TASK_NAMES),
        "seeds": list(seeds),
        "examples_per_length": examples_per_length,
        "epochs": epochs,
        "learning_rate": learning_rate,
        "support_coverage": _support_coverage(seeds, examples_per_length),
        "model": {
            "type": "support_complete_two_block_copy_output_decoder",
            "model_dim": MODEL_DIM,
            "vocab_size": VOCAB_SIZE,
            "optimizer": "full_batch_adam",
            "trained_parameters": "token embeddings, two q/k/v/o attention blocks, positional scale",
            "value_output_mode": "copied prefix-token mass from learned second-block attention, no vocab softmax projection",
        },
        "claim_boundary": _claim_boundary(),
        "failed_runs": failed_runs,
        "run_table": run_table,
        "aggregate_table": aggregate_table,
        "ranking_table": ranking_table,
    }
    result["decision"] = _decision(result)
    return result


def write_stage63_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    return write_stage52_outputs(result, output_dir)


def print_stage63_summary(result: dict[str, Any]) -> None:
    print_stage61_summary(result)
