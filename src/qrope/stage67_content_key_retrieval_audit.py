from __future__ import annotations

import hashlib
import random
from pathlib import Path
from typing import Any

import numpy as np

from .stage10_small_decoder_transformer import (
    TEST_LENGTHS,
    TRAIN_LENGTHS,
    VALIDATION_LENGTHS,
    VOCAB_SIZE,
    Stage10Example,
    autograd_available,
)
from .stage45_matched_decoder_only_gate import METHOD_NAMES, _stage10_method_name
from .stage52_two_block_decoder_feasibility_audit import (
    CAPACITY_TRAIN_TOP1_THRESHOLD,
    DEFAULT_LEARNING_RATE,
    GENERALIZATION_TOP1_THRESHOLD,
    _metric_names,
    write_stage52_outputs,
)
from .stage61_support_complete_two_block_audit import DEFAULT_AUDIT_SEEDS, DEFAULT_EXAMPLES_PER_LENGTH
from .stage61_support_complete_two_block_audit import build_blocked_result as build_stage61_blocked_result
from .stage61_support_complete_two_block_audit import print_stage61_summary
from .stage62_long_training_support_complete_audit import DEFAULT_EPOCHS
from .stage64_two_block_pointer_generator_capacity_audit import (
    _add_copy_gate_aggregates,
    evaluate_two_block_pointer_generator_decoder,
    train_two_block_pointer_generator_decoder,
)


STAGE67_SCHEMA_VERSION = "qrope_stage67_content_key_retrieval_audit_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage67_content_key_retrieval_audit"
CONTENT_KEY_TASK = "content_key_retrieval"
TASK_NAMES = (CONTENT_KEY_TASK,)
KEY_TOKENS = tuple(range(64, 80))
VALUE_TOKENS = tuple(range(32, 48))
QUERY_TOKEN = 126


def _claim_boundary() -> dict[str, list[str]]:
    return {
        "supported": [
            "A no-credential content-key retrieval row-redesign audit for the two-block learned pointer-generator path.",
            "Evidence about whether a standard visible key/value cue repairs held-out 48/64 retrieval generalization.",
            "Fair RoPE/ALiBI/sinusoidal/no-position/PhaseWrap comparisons with failed-run retention.",
        ],
        "excluded": [
            "production transformer superiority",
            "full transformer-scale validation",
            "a claim that PhaseWrap-RoPE replaces RoPE",
            "a claim that content-key rows are equivalent to the original phase-cued retrieval gate",
            "a claim that row-redesign success would be positional-method promotion evidence by itself",
            "broad quantum advantage",
        ],
    }


def build_blocked_result(*, reason: str = "missing_optional_autograd_dependency") -> dict[str, Any]:
    result = build_stage61_blocked_result(reason=reason)
    result.update(
        {
            "schema_version": STAGE67_SCHEMA_VERSION,
            "stage": "stage67_content_key_retrieval_audit",
            "source_stage": "stage66_positional_copy_expert_audit",
            "tasks": list(TASK_NAMES),
            "epochs": DEFAULT_EPOCHS,
            "claim_boundary": _claim_boundary(),
        }
    )
    return result


def make_stage67_splits(
    *,
    seeds: tuple[int, ...] = DEFAULT_AUDIT_SEEDS,
    examples_per_length: int = DEFAULT_EXAMPLES_PER_LENGTH,
) -> dict[str, dict[str, list[Stage10Example]]]:
    split_lengths = {"train": TRAIN_LENGTHS, "validation": VALIDATION_LENGTHS, "test": TEST_LENGTHS}
    splits = {CONTENT_KEY_TASK: {"train": [], "validation": [], "test": []}}
    for seed in seeds:
        rng = np.random.default_rng(seed + 67_000)
        for split, lengths in split_lengths.items():
            for sequence_length in lengths:
                query_pos = sequence_length - 1
                for item_index in range(examples_per_length):
                    key_token = int(KEY_TOKENS[(seed + sequence_length + item_index) % len(KEY_TOKENS)])
                    label_token = int(VALUE_TOKENS[(3 * seed + sequence_length + item_index) % len(VALUE_TOKENS)])
                    target_pos = int(rng.integers(max(2, query_pos // 5), max(3, query_pos - 5)))
                    target_delta = query_pos - target_pos
                    tokens = [int(value) for value in rng.integers(0, 32, size=sequence_length)]
                    tokens[target_pos - 1] = key_token
                    tokens[target_pos] = label_token
                    tokens[query_pos - 2] = QUERY_TOKEN
                    tokens[query_pos - 1] = key_token
                    tokens[query_pos] = QUERY_TOKEN
                    splits[CONTENT_KEY_TASK][split].append(
                        Stage10Example(
                            example_id=f"{CONTENT_KEY_TASK}_{split}_seed{seed}_L{sequence_length}_{item_index:03d}",
                            seed=seed,
                            task=CONTENT_KEY_TASK,
                            split=split,
                            sequence_length=sequence_length,
                            query_pos=query_pos,
                            reference_delta=1,
                            target_pos=target_pos,
                            target_delta=target_delta,
                            tokens=tuple(tokens),
                            label_token=label_token,
                        )
                    )
    return splits


def _bootstrap_ci(values: list[float], *, seed_text: str, iterations: int = 300) -> dict[str, float]:
    rng = random.Random(int(hashlib.sha256(seed_text.encode("utf-8")).hexdigest()[:16], 16))
    means: list[float] = []
    for _ in range(iterations):
        sample = [values[rng.randrange(len(values))] for _ in range(len(values))]
        means.append(float(sum(sample) / len(sample)))
    means.sort()
    return {"low": round(means[int(0.025 * (iterations - 1))], 6), "high": round(means[int(0.975 * (iterations - 1))], 6)}


def _aggregate(run_table: list[dict[str, Any]], failed_runs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    aggregate_table: list[dict[str, Any]] = []
    for task_name in TASK_NAMES:
        for method_name in METHOD_NAMES:
            rows = [row for row in run_table if row["task"] == task_name and row["method"] == method_name]
            if not rows:
                continue
            record: dict[str, Any] = {
                "task": task_name,
                "method": method_name,
                "seed_count": len(rows),
                "failed_run_count": len([run for run in failed_runs if run["task"] == task_name and run["method"] == method_name]),
                "learned_position_scale_mean": round(float(np.mean([row["learned_position_scale"] for row in rows])), 6),
            }
            for metric_name in _metric_names("train") + _metric_names("validation") + _metric_names("test") + ("final_training_loss",):
                values = [float(row[metric_name]) for row in rows]
                ci = _bootstrap_ci(values, seed_text=f"stage67:{task_name}:{method_name}:{metric_name}")
                record[f"{metric_name}_mean"] = round(float(np.mean(values)), 6)
                record[f"{metric_name}_ci_low"] = ci["low"]
                record[f"{metric_name}_ci_high"] = ci["high"]
            aggregate_table.append(record)
    return aggregate_table


def _best_row(rows: list[dict[str, Any]], *, split: str = "test") -> dict[str, Any]:
    return sorted(
        rows,
        key=lambda row: (
            row[f"{split}_top1_accuracy_mean"],
            row[f"{split}_mrr_mean"],
            row[f"{split}_mean_target_probability_mean"],
            -row[f"{split}_loss_mean"],
            row["method"],
        ),
        reverse=True,
    )[0]


def _decision(result: dict[str, Any]) -> dict[str, Any]:
    if result["status"] != "completed":
        return {}
    aggregate_table = result["aggregate_table"]
    best_train = _best_row(aggregate_table, split="train")
    best_test = _best_row(aggregate_table, split="test")
    capacity_established = best_train["train_top1_accuracy_mean"] >= CAPACITY_TRAIN_TOP1_THRESHOLD
    retrieval_generalized = best_test["test_top1_accuracy_mean"] >= GENERALIZATION_TOP1_THRESHOLD
    generalized_methods = [
        row["method"] for row in aggregate_table if row["test_top1_accuracy_mean"] >= GENERALIZATION_TOP1_THRESHOLD
    ]
    phasewrap_generalized = retrieval_generalized and best_test["method"].startswith("phasewrap")
    if not capacity_established:
        decision = "CONTENT_KEY_RETRIEVAL_CAPACITY_NOT_ESTABLISHED"
        boundary = "The content-key row redesign does not establish train capacity."
    elif len(generalized_methods) == len(METHOD_NAMES):
        decision = "CONTENT_KEY_RETRIEVAL_SOLVABLE_FOR_ALL_METHODS_NOT_PROMOTION"
        boundary = "The content-key row redesign is solvable for every tested method, including no_position."
    elif retrieval_generalized:
        decision = "CONTENT_KEY_RETRIEVAL_GENERALIZES_REVIEW_REQUIRED"
        boundary = "The content-key row redesign generalizes retrieval; review method ordering before any claim update."
    else:
        decision = "CONTENT_KEY_RETRIEVAL_WITHOUT_GENERALIZATION"
        boundary = "The content-key row redesign preserves capacity but does not generalize retrieval."
    return {
        "decision": decision,
        "capacity_train_top1_threshold": CAPACITY_TRAIN_TOP1_THRESHOLD,
        "generalization_top1_threshold": GENERALIZATION_TOP1_THRESHOLD,
        "best_train_task": best_train["task"],
        "best_train_method": best_train["method"],
        "best_train_top1": best_train["train_top1_accuracy_mean"],
        "capacity_established": capacity_established,
        "retrieval_generalized_tasks": [CONTENT_KEY_TASK] if retrieval_generalized else [],
        "retrieval_generalized_methods": generalized_methods,
        "phasewrap_retrieval_generalized_tasks": [CONTENT_KEY_TASK] if phasewrap_generalized else [],
        "retrieval_best_methods": {CONTENT_KEY_TASK: best_test["method"]},
        "retrieval_best_top1": {CONTENT_KEY_TASK: best_test["test_top1_accuracy_mean"]},
        "tiny_text_best_method": None,
        "tiny_text_best_top1": None,
        "claim_boundary": boundary,
    }


def run_stage67_audit(
    *,
    seeds: tuple[int, ...] = DEFAULT_AUDIT_SEEDS,
    examples_per_length: int = DEFAULT_EXAMPLES_PER_LENGTH,
    epochs: int = DEFAULT_EPOCHS,
    learning_rate: float = DEFAULT_LEARNING_RATE,
    method_names: tuple[str, ...] = METHOD_NAMES,
) -> dict[str, Any]:
    if not autograd_available():
        return build_blocked_result()
    splits_by_task = make_stage67_splits(seeds=seeds, examples_per_length=examples_per_length)
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
        "schema_version": STAGE67_SCHEMA_VERSION,
        "stage": "stage67_content_key_retrieval_audit",
        "status": "completed",
        "dataset": "synthetic_content_key_retrieval_train_short_test_long_v1",
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "source_rows": "stage67 content-key retrieval rows",
        "source_stage": "stage66_positional_copy_expert_audit",
        "method_names": list(method_names),
        "tasks": list(TASK_NAMES),
        "seeds": list(seeds),
        "train_lengths": list(TRAIN_LENGTHS),
        "validation_lengths": list(VALIDATION_LENGTHS),
        "test_lengths": list(TEST_LENGTHS),
        "examples_per_length": examples_per_length,
        "epochs": epochs,
        "learning_rate": learning_rate,
        "model": {
            "type": "two_block_pointer_generator_content_key_retrieval_decoder",
            "optimizer": "full_batch_adam",
            "trained_parameters": "token embeddings, two q/k/v/o attention blocks, vocab output projection, positional scale, copy/vocab gate",
            "value_output_mode": "learned mixture of vocab softmax and copied prefix-token mass",
            "row_policy": "query contains a visible key token; prefix contains a matching key/value pair; positional reference_delta is non-oracular",
        },
        "claim_boundary": _claim_boundary(),
        "failed_runs": failed_runs,
        "run_table": run_table,
        "aggregate_table": aggregate_table,
        "ranking_table": ranking_table,
    }
    result["decision"] = _decision(result)
    return result


def write_stage67_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    return write_stage52_outputs(result, output_dir)


def print_stage67_summary(result: dict[str, Any]) -> None:
    print_stage61_summary(result)
