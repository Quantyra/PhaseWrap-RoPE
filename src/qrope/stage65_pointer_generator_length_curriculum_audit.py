from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from .stage10_small_decoder_transformer import TASK_NAMES, TEST_LENGTHS, TRAIN_LENGTHS, VALIDATION_LENGTHS, autograd_available, make_stage10_splits
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
from .stage64_two_block_pointer_generator_capacity_audit import (
    _add_copy_gate_aggregates,
    evaluate_two_block_pointer_generator_decoder,
    train_two_block_pointer_generator_decoder,
)


STAGE65_SCHEMA_VERSION = "qrope_stage65_pointer_generator_length_curriculum_audit_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage65_pointer_generator_length_curriculum_audit"


def _claim_boundary() -> dict[str, list[str]]:
    return {
        "supported": [
            "A no-credential length-curriculum audit for the two-block learned pointer-generator path.",
            "Evidence about whether adding the intermediate length-40 rows repairs held-out 48/64 retrieval generalization.",
            "Fair RoPE/ALiBI/sinusoidal/no-position/PhaseWrap comparisons with failed-run retention.",
        ],
        "excluded": [
            "production transformer superiority",
            "full transformer-scale validation",
            "a claim that PhaseWrap-RoPE replaces RoPE",
            "a claim that validation-length curriculum training is the same as the original train-short/test-long gate",
            "a claim that output-path or curriculum diagnostics are positional-method promotion evidence",
            "broad quantum advantage",
        ],
    }


def build_blocked_result(*, reason: str = "missing_optional_autograd_dependency") -> dict[str, Any]:
    result = build_stage61_blocked_result(reason=reason)
    result.update(
        {
            "schema_version": STAGE65_SCHEMA_VERSION,
            "stage": "stage65_pointer_generator_length_curriculum_audit",
            "source_stage": "stage64_two_block_pointer_generator_capacity_audit",
            "epochs": DEFAULT_EPOCHS,
            "claim_boundary": _claim_boundary(),
        }
    )
    return result


def _decision(result: dict[str, Any]) -> dict[str, Any]:
    if result["status"] != "completed":
        return {}
    base = base_decision(result["aggregate_table"])
    if not base["capacity_established"]:
        decision = "POINTER_GENERATOR_LENGTH_CURRICULUM_CAPACITY_NOT_ESTABLISHED"
        boundary = "Adding length-40 rows does not preserve learned pointer-generator capacity."
    elif all(value >= GENERALIZATION_TOP1_THRESHOLD for value in base["retrieval_best_top1"].values()):
        decision = "POINTER_GENERATOR_LENGTH_CURRICULUM_RETRIEVAL_REVIEW_REQUIRED"
        boundary = "Adding length-40 rows generalizes retrieval; review method ordering before any claim update."
    else:
        decision = "POINTER_GENERATOR_LENGTH_CURRICULUM_WITHOUT_RETRIEVAL_GENERALIZATION"
        boundary = "Adding length-40 rows preserves capacity but does not generalize all retrieval lanes."
    return {
        **base,
        "decision": decision,
        "claim_boundary": boundary,
        "base_capacity_train_top1_threshold": CAPACITY_TRAIN_TOP1_THRESHOLD,
    }


def run_stage65_audit(
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
            base_train_rows = [row for row in splits["train"] if row.seed == seed]
            curriculum_rows = [row for row in splits["validation"] if row.seed == seed]
            train_rows = base_train_rows + curriculum_rows
            validation_rows = curriculum_rows
            test_rows = [row for row in splits["test"] if row.seed == seed]
            for method_name in method_names:
                try:
                    stage10_method = _stage10_method_name(method_name)
                    trained = train_two_block_pointer_generator_decoder(
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
                        "base_train_row_count": len(base_train_rows),
                        "curriculum_row_count": len(curriculum_rows),
                        "validation_row_count": len(validation_rows),
                        "test_row_count": len(test_rows),
                        "final_training_loss": trained["final_training_loss"],
                        "learned_position_scale": trained["learned_position_scale"],
                        "learned_copy_gate": trained["learned_copy_gate"],
                        "training_history": trained["training_history"],
                    }
                    for split_name, split_rows in (("train", train_rows), ("validation", validation_rows), ("test", test_rows)):
                        metrics = evaluate_two_block_pointer_generator_decoder(split_rows, stage10_method, trained["weights"])
                        for metric_name, value in metrics.items():
                            if metric_name != "row_count":
                                row[f"{split_name}_{metric_name}"] = value
                    run_table.append(row)
                except Exception as exc:  # pragma: no cover - retained for artifact completeness.
                    failed_runs.append({"task": task_name, "seed": seed, "method": method_name, "error": str(exc)})
    aggregate_table = _add_copy_gate_aggregates(_aggregate(run_table, failed_runs), run_table)
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
        "schema_version": STAGE65_SCHEMA_VERSION,
        "stage": "stage65_pointer_generator_length_curriculum_audit",
        "status": "completed",
        "dataset": "synthetic_small_decoder_train_short_length40_curriculum_test_long_v1",
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "source_rows": "stage10/stage45 matched decoder-only rows",
        "source_stage": "stage64_two_block_pointer_generator_capacity_audit",
        "method_names": list(method_names),
        "tasks": list(TASK_NAMES),
        "seeds": list(seeds),
        "train_lengths": list(TRAIN_LENGTHS) + list(VALIDATION_LENGTHS),
        "base_train_lengths": list(TRAIN_LENGTHS),
        "curriculum_lengths": list(VALIDATION_LENGTHS),
        "test_lengths": list(TEST_LENGTHS),
        "examples_per_length": examples_per_length,
        "epochs": epochs,
        "learning_rate": learning_rate,
        "support_coverage": _support_coverage(seeds, examples_per_length),
        "model": {
            "type": "support_complete_two_block_learned_pointer_generator_length_curriculum_decoder",
            "optimizer": "full_batch_adam",
            "trained_parameters": "token embeddings, two q/k/v/o attention blocks, vocab output projection, positional scale, copy/vocab gate",
            "value_output_mode": "learned mixture of vocab softmax and copied prefix-token mass",
            "curriculum_policy": "original validation length 40 is included in training; held-out test remains lengths 48 and 64",
        },
        "claim_boundary": _claim_boundary(),
        "failed_runs": failed_runs,
        "run_table": run_table,
        "aggregate_table": aggregate_table,
        "ranking_table": ranking_table,
    }
    result["decision"] = _decision(result)
    return result


def write_stage65_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    return write_stage52_outputs(result, output_dir)


def print_stage65_summary(result: dict[str, Any]) -> None:
    print_stage61_summary(result)
