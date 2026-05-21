from __future__ import annotations

from pathlib import Path
from typing import Any

from .stage10_small_decoder_transformer import DEFAULT_SEEDS, TASK_NAMES, make_stage10_splits
from .stage45_matched_decoder_only_gate import METHOD_NAMES
from .stage52_two_block_decoder_feasibility_audit import (
    DEFAULT_LEARNING_RATE,
    GENERALIZATION_TOP1_THRESHOLD,
    RETRIEVAL_TASKS,
    build_blocked_result as build_stage52_blocked_result,
    print_stage52_summary,
    run_stage52_audit,
    write_stage52_outputs,
)
from .stage60_support_fallback_strictness_audit import _query_mod


STAGE61_SCHEMA_VERSION = "qrope_stage61_support_complete_two_block_audit_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage61_support_complete_two_block_audit"
DEFAULT_AUDIT_SEEDS = DEFAULT_SEEDS
DEFAULT_EXAMPLES_PER_LENGTH = 6
DEFAULT_EPOCHS = 20


def _claim_boundary() -> dict[str, list[str]]:
    return {
        "supported": [
            "A no-credential support-complete two-block decoder capacity audit.",
            "A learned vocab-softmax check with no fixed copy output, no lookup output, and no fallback cue decoder.",
            "Fair RoPE/ALiBI/sinusoidal/no-position/PhaseWrap comparisons with failed-run retention.",
        ],
        "excluded": [
            "production transformer superiority",
            "full transformer-scale validation",
            "a claim that PhaseWrap-RoPE replaces RoPE",
            "a claim that support-complete training alone establishes learned retrieval generalization",
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
        test_pairs = sorted(
            {(_query_mod(row), int(row.reference_delta)) for row in splits["phase_cued_retrieval"]["test"] if row.seed == seed}
        )
        train_mods = {pair[0] for pair in train_pairs}
        test_mods = {pair[0] for pair in test_pairs}
        coverage[str(seed)] = {
            "train_support_pairs": [{"query_mod": query_mod, "reference_delta": reference_delta} for query_mod, reference_delta in train_pairs],
            "test_support_pairs": [{"query_mod": query_mod, "reference_delta": reference_delta} for query_mod, reference_delta in test_pairs],
            "test_mods_covered_by_train": sorted(test_mods & train_mods),
            "test_mods_missing_from_train": sorted(test_mods - train_mods),
            "test_known_fraction": round(float(len(test_mods & train_mods) / len(test_mods)), 6) if test_mods else 1.0,
        }
    return coverage


def build_blocked_result(*, reason: str = "missing_optional_autograd_dependency") -> dict[str, Any]:
    result = build_stage52_blocked_result(reason=reason)
    result.update(
        {
            "schema_version": STAGE61_SCHEMA_VERSION,
            "stage": "stage61_support_complete_two_block_audit",
            "source_stage": "stage52_two_block_decoder_feasibility_audit",
            "examples_per_length": DEFAULT_EXAMPLES_PER_LENGTH,
            "epochs": DEFAULT_EPOCHS,
            "claim_boundary": _claim_boundary(),
        }
    )
    return result


def _decision(result: dict[str, Any]) -> dict[str, Any]:
    if result["status"] != "completed":
        return {}
    base = result["decision"]
    retrieval_best_top1 = base["retrieval_best_top1"]
    if not base["capacity_established"]:
        decision = "SUPPORT_COMPLETE_TWO_BLOCK_CAPACITY_NOT_ESTABLISHED"
        boundary = "Even support-complete phase-cued train coverage does not make the learned two-block decoder fit well enough for promotion."
    elif all(value >= GENERALIZATION_TOP1_THRESHOLD for value in retrieval_best_top1.values()):
        decision = "SUPPORT_COMPLETE_TWO_BLOCK_RETRIEVAL_REVIEW_REQUIRED"
        boundary = "Support-complete training generalizes retrieval; review method ordering and calibration before any claim update."
    else:
        decision = "SUPPORT_COMPLETE_TWO_BLOCK_RETRIEVAL_FAILED"
        boundary = "Support-complete training establishes capacity but does not generalize retrieval."
    return {
        **base,
        "decision": decision,
        "claim_boundary": boundary,
        "base_stage52_decision": base["decision"],
    }


def run_stage61_audit(
    *,
    seeds: tuple[int, ...] = DEFAULT_AUDIT_SEEDS,
    examples_per_length: int = DEFAULT_EXAMPLES_PER_LENGTH,
    epochs: int = DEFAULT_EPOCHS,
    learning_rate: float = DEFAULT_LEARNING_RATE,
    method_names: tuple[str, ...] = METHOD_NAMES,
) -> dict[str, Any]:
    result = run_stage52_audit(
        seeds=seeds,
        examples_per_length=examples_per_length,
        epochs=epochs,
        learning_rate=learning_rate,
        method_names=method_names,
    )
    result.update(
        {
            "schema_version": STAGE61_SCHEMA_VERSION,
            "stage": "stage61_support_complete_two_block_audit",
            "source_stage": "stage60_support_fallback_strictness_audit",
            "examples_per_length": examples_per_length,
            "support_coverage": _support_coverage(seeds, examples_per_length),
            "model": {
                "type": "support_complete_two_block_residual_decoder",
                "value_output_mode": "learned vocab softmax, no fixed copy output",
                "support_policy": "phase-cued train split covers all reference-delta residues when examples_per_length is 6",
                "trained_parameters": "token embeddings, two q/k/v/o attention blocks, vocab output projection, positional scale",
            },
            "claim_boundary": _claim_boundary(),
        }
    )
    if result["status"] == "completed":
        result["decision"] = _decision(result)
    return result


def write_stage61_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    return write_stage52_outputs(result, output_dir)


def print_stage61_summary(result: dict[str, Any]) -> None:
    print_stage52_summary(result)
