from __future__ import annotations

from pathlib import Path
from typing import Any

from .stage45_matched_decoder_only_gate import METHOD_NAMES
from .stage52_two_block_decoder_feasibility_audit import DEFAULT_LEARNING_RATE, GENERALIZATION_TOP1_THRESHOLD, write_stage52_outputs
from .stage61_support_complete_two_block_audit import (
    DEFAULT_AUDIT_SEEDS,
    DEFAULT_EXAMPLES_PER_LENGTH,
    _support_coverage,
    build_blocked_result as build_stage61_blocked_result,
    print_stage61_summary,
    run_stage61_audit,
)


STAGE62_SCHEMA_VERSION = "qrope_stage62_long_training_support_complete_audit_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage62_long_training_support_complete_audit"
DEFAULT_EPOCHS = 80


def _claim_boundary() -> dict[str, list[str]]:
    return {
        "supported": [
            "A no-credential long-training support-complete two-block decoder capacity audit.",
            "A learned vocab-softmax check with no fixed copy output, no lookup output, and no fallback cue decoder.",
            "Fair RoPE/ALiBI/sinusoidal/no-position/PhaseWrap comparisons with failed-run retention.",
        ],
        "excluded": [
            "production transformer superiority",
            "full transformer-scale validation",
            "a claim that PhaseWrap-RoPE replaces RoPE",
            "a claim that longer training alone establishes learned retrieval generalization",
            "broad quantum advantage",
        ],
    }


def build_blocked_result(*, reason: str = "missing_optional_autograd_dependency") -> dict[str, Any]:
    result = build_stage61_blocked_result(reason=reason)
    result.update(
        {
            "schema_version": STAGE62_SCHEMA_VERSION,
            "stage": "stage62_long_training_support_complete_audit",
            "source_stage": "stage61_support_complete_two_block_audit",
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
        decision = "LONG_TRAINING_SUPPORT_COMPLETE_CAPACITY_NOT_ESTABLISHED"
        boundary = "Longer training improves the support-complete two-block decoder but still does not establish capacity for promotion."
    elif all(value >= GENERALIZATION_TOP1_THRESHOLD for value in retrieval_best_top1.values()):
        decision = "LONG_TRAINING_SUPPORT_COMPLETE_RETRIEVAL_REVIEW_REQUIRED"
        boundary = "Longer support-complete training generalizes retrieval; review method ordering and calibration before any claim update."
    else:
        decision = "LONG_TRAINING_SUPPORT_COMPLETE_RETRIEVAL_FAILED"
        boundary = "Longer support-complete training establishes capacity but does not generalize retrieval."
    return {
        **base,
        "decision": decision,
        "claim_boundary": boundary,
        "base_stage61_decision": base["decision"],
    }


def run_stage62_audit(
    *,
    seeds: tuple[int, ...] = DEFAULT_AUDIT_SEEDS,
    examples_per_length: int = DEFAULT_EXAMPLES_PER_LENGTH,
    epochs: int = DEFAULT_EPOCHS,
    learning_rate: float = DEFAULT_LEARNING_RATE,
    method_names: tuple[str, ...] = METHOD_NAMES,
) -> dict[str, Any]:
    result = run_stage61_audit(
        seeds=seeds,
        examples_per_length=examples_per_length,
        epochs=epochs,
        learning_rate=learning_rate,
        method_names=method_names,
    )
    result.update(
        {
            "schema_version": STAGE62_SCHEMA_VERSION,
            "stage": "stage62_long_training_support_complete_audit",
            "source_stage": "stage61_support_complete_two_block_audit",
            "epochs": epochs,
            "support_coverage": _support_coverage(seeds, examples_per_length),
            "model": {
                "type": "long_training_support_complete_two_block_residual_decoder",
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


def write_stage62_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    return write_stage52_outputs(result, output_dir)


def print_stage62_summary(result: dict[str, Any]) -> None:
    print_stage61_summary(result)
