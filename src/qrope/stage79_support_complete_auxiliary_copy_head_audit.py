from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from .stage10_small_decoder_transformer import DEFAULT_SEEDS, TASK_NAMES, Stage10Example, make_stage10_splits
from .stage45_matched_decoder_only_gate import METHOD_NAMES
from .stage52_two_block_decoder_feasibility_audit import GENERALIZATION_TOP1_THRESHOLD, RETRIEVAL_TASKS
from .stage56_standard_input_cue_copy_audit import DEFAULT_EXAMPLES_PER_LENGTH, write_stage56_outputs
from .stage58_pooled_train_query_support_audit import _query_mod
from .stage77_auxiliary_support_copy_head_audit import (
    DEFAULT_LEARNING_RATE,
    DEFAULT_SUPPORT_AUX_WEIGHT,
    build_blocked_result as build_stage77_blocked_result,
    print_stage77_summary,
    run_stage77_audit,
)


STAGE79_SCHEMA_VERSION = "qrope_stage79_support_complete_auxiliary_copy_head_audit_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage79_support_complete_auxiliary_copy_head_audit"
DEFAULT_AUDIT_SEEDS = DEFAULT_SEEDS
DEFAULT_SUPPORT_COMPLETE_EXAMPLES_PER_LENGTH = 6
DEFAULT_EPOCHS = 80


def _claim_boundary() -> dict[str, list[str]]:
    return {
        "supported": [
            "A no-credential support-complete same-seed auxiliary support/copy-head audit over original Stage10 rows.",
            "Evidence about whether Stage77's failure persists after same-seed phase-cued support coverage is restored.",
            "Fair RoPE/ALiBI/sinusoidal/no-position/PhaseWrap reporting with failed-run retention.",
        ],
        "excluded": [
            "production transformer superiority",
            "full transformer-scale validation",
            "a claim that PhaseWrap-RoPE replaces RoPE",
            "a claim that this compact support-complete auxiliary copy-head is a matched decoder-only transformer",
            "a claim that support-complete auxiliary copy training alone establishes positional-method promotion",
            "broad quantum advantage",
        ],
    }


def _support_coverage(seeds: tuple[int, ...], examples_per_length: int) -> dict[str, Any]:
    splits = make_stage10_splits(seeds=seeds, examples_per_length=examples_per_length)
    coverage: dict[str, Any] = {}
    for seed in seeds:
        train_pairs = sorted(
            {(_query_mod(row), int(row.reference_delta)) for row in splits["phase_cued_retrieval"]["train"] if row.seed == seed}
        )
        test_rows = [row for row in splits["phase_cued_retrieval"]["test"] if row.seed == seed]
        train_pair_set = set(train_pairs)
        exact_hits = [(_query_mod(row), int(row.reference_delta)) in train_pair_set for row in test_rows]
        coverage[str(seed)] = {
            "train_support_pairs": [{"query_mod": query_mod, "reference_delta": reference_delta} for query_mod, reference_delta in train_pairs],
            "test_support_pairs": [
                {"query_mod": _query_mod(row), "reference_delta": int(row.reference_delta)} for row in test_rows
            ],
            "exact_query_support_fraction": round(float(np.mean(exact_hits)), 6) if test_rows else 0.0,
        }
    return coverage


def build_blocked_result(*, reason: str = "missing_optional_autograd_dependency") -> dict[str, Any]:
    result = build_stage77_blocked_result(reason=reason)
    result.update(
        {
            "schema_version": STAGE79_SCHEMA_VERSION,
            "stage": "stage79_support_complete_auxiliary_copy_head_audit",
            "source_stage": "stage78_support_coverage_split_audit",
            "examples_per_length": DEFAULT_SUPPORT_COMPLETE_EXAMPLES_PER_LENGTH,
            "epochs": DEFAULT_EPOCHS,
            "claim_boundary": _claim_boundary(),
        }
    )
    return result


def _decision(result: dict[str, Any]) -> dict[str, Any]:
    aggregate_table = result["aggregate_table"]
    base = result["decision"]
    phase_rows = [row for row in aggregate_table if row["task"] == "phase_cued_retrieval"]
    phase_best = sorted(
        phase_rows,
        key=lambda row: (
            row["test_top1_accuracy_mean"],
            row["test_mrr_mean"],
            row["test_mean_target_probability_mean"],
            row["method"],
        ),
        reverse=True,
    )[0]
    retrieval_solved = [
        task
        for task in RETRIEVAL_TASKS
        if max(row["test_top1_accuracy_mean"] for row in aggregate_table if row["task"] == task) >= GENERALIZATION_TOP1_THRESHOLD
    ]
    support_accuracy = base["mean_phase_cued_test_support_accuracy"]
    if phase_best["test_top1_accuracy_mean"] >= GENERALIZATION_TOP1_THRESHOLD:
        decision = "SUPPORT_COMPLETE_AUXILIARY_COPY_HEAD_PHASE_CUED_REVIEW_REQUIRED"
        boundary = "Support-complete auxiliary copy training repairs phase-cued retrieval; review method ordering and calibration before any claim update."
    elif support_accuracy >= 1.0:
        decision = "SUPPORT_COMPLETE_AUXILIARY_COPY_HEAD_SUPPORT_RECOVERED_RETRIEVAL_FAILED"
        boundary = "Same-seed support-complete training recovers held-out support labels but still does not repair phase-cued token retrieval."
    else:
        decision = "SUPPORT_COMPLETE_AUXILIARY_COPY_HEAD_SUPPORT_NOT_RECOVERED"
        boundary = "Support-complete exposure does not fully recover held-out support labels."
    return {
        **base,
        "decision": decision,
        "base_stage77_decision": base["decision"],
        "retrieval_solved_tasks": retrieval_solved,
        "phase_cued_best_method": phase_best["method"],
        "phase_cued_best_top1": phase_best["test_top1_accuracy_mean"],
        "claim_boundary": boundary,
    }


def run_stage79_audit(
    *,
    seeds: tuple[int, ...] = DEFAULT_AUDIT_SEEDS,
    examples_per_length: int = DEFAULT_SUPPORT_COMPLETE_EXAMPLES_PER_LENGTH,
    method_names: tuple[str, ...] = METHOD_NAMES,
    epochs: int = DEFAULT_EPOCHS,
    learning_rate: float = DEFAULT_LEARNING_RATE,
    support_aux_weight: float = DEFAULT_SUPPORT_AUX_WEIGHT,
) -> dict[str, Any]:
    result = run_stage77_audit(
        seeds=seeds,
        examples_per_length=examples_per_length,
        method_names=method_names,
        epochs=epochs,
        learning_rate=learning_rate,
        support_aux_weight=support_aux_weight,
    )
    result.update(
        {
            "schema_version": STAGE79_SCHEMA_VERSION,
            "stage": "stage79_support_complete_auxiliary_copy_head_audit",
            "dataset": "synthetic_stage10_original_rows_same_seed_support_complete_auxiliary_support_copy_v1",
            "source_stage": "stage78_support_coverage_split_audit",
            "examples_per_length": examples_per_length,
            "support_complete_policy": "examples_per_length=6 restores same-seed phase-cued query-support coverage for held-out rows",
            "support_coverage": _support_coverage(seeds, examples_per_length),
            "model": {
                "type": "same_seed_support_complete_auxiliary_support_copy_head",
                "value_output_mode": "deterministic copied prefix-token mass",
                "metadata_excluded": ["hard query-support lookup", "standalone pretrained support head", "row.reference_delta exact value at evaluation", "row.target_pos", "row.target_delta"],
            },
            "claim_boundary": _claim_boundary(),
        }
    )
    if result["status"] == "completed":
        result["decision"] = _decision(result)
    return result


def write_stage79_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    return write_stage56_outputs(result, output_dir)


def print_stage79_summary(result: dict[str, Any]) -> None:
    print_stage77_summary(result)
