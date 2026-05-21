from __future__ import annotations

from pathlib import Path
from typing import Any

from .stage10_small_decoder_transformer import DEFAULT_SEEDS, TASK_NAMES
from .stage45_matched_decoder_only_gate import METHOD_NAMES
from .stage47_adam_decoder_generalization_audit import DEFAULT_LEARNING_RATE
from .stage52_two_block_decoder_feasibility_audit import (
    GENERALIZATION_TOP1_THRESHOLD,
    build_blocked_result as build_stage52_blocked_result,
    print_stage52_summary,
    run_stage52_audit,
    write_stage52_outputs,
)


STAGE53_SCHEMA_VERSION = "qrope_stage53_two_block_retrieval_hardening_audit_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage53_two_block_retrieval_hardening_audit"
DEFAULT_AUDIT_SEEDS = (DEFAULT_SEEDS[0],)
DEFAULT_EXAMPLES_PER_LENGTH = 2
DEFAULT_EPOCHS = 90


def _claim_boundary() -> dict[str, list[str]]:
    return {
        "supported": [
            "A retrieval-exposure and training-budget hardening audit for the Stage 52 two-block decoder.",
            "Fair RoPE/ALiBI/sinusoidal/no-position/PhaseWrap comparisons under the same matched row family.",
            "Evidence about whether the stronger decoder path begins to repair retrieval before five-seed scale-up.",
        ],
        "excluded": [
            "production transformer superiority",
            "full transformer-scale validation",
            "a claim that PhaseWrap-RoPE replaces RoPE",
            "a claim that a one-seed hardening audit satisfies the five-seed promotion standard",
            "broad quantum advantage",
        ],
    }


def build_blocked_result(*, reason: str = "missing_optional_autograd_dependency") -> dict[str, Any]:
    blocked = build_stage52_blocked_result(reason=reason)
    blocked["schema_version"] = STAGE53_SCHEMA_VERSION
    blocked["stage"] = "stage53_two_block_retrieval_hardening_audit"
    blocked["claim_boundary"] = _claim_boundary()
    blocked["seeds"] = list(DEFAULT_AUDIT_SEEDS)
    return blocked


def _stage53_decision(stage52_decision: dict[str, Any]) -> dict[str, Any]:
    retrieval_generalized = list(stage52_decision.get("retrieval_generalized_tasks", []))
    phasewrap_retrieval_generalized = list(stage52_decision.get("phasewrap_retrieval_generalized_tasks", []))
    if retrieval_generalized:
        decision = "TWO_BLOCK_RETRIEVAL_HARDENING_GENERALIZATION_PRESENT_REVIEW_REQUIRED"
        boundary = "Retrieval hardening produced at least one held-out retrieval lane above threshold; review method ordering before any claim update."
    else:
        decision = "TWO_BLOCK_RETRIEVAL_HARDENING_FAILED"
        boundary = "Retrieval hardening still does not establish held-out retrieval generalization."
    return {
        **stage52_decision,
        "decision": decision,
        "retrieval_hardening_generalization_top1_threshold": GENERALIZATION_TOP1_THRESHOLD,
        "retrieval_generalized_tasks": retrieval_generalized,
        "phasewrap_retrieval_generalized_tasks": phasewrap_retrieval_generalized,
        "claim_boundary": boundary,
    }


def run_stage53_audit(
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
    if result["status"] != "completed":
        return build_blocked_result(reason=result.get("blocked_reason", "stage52_blocked"))
    result["schema_version"] = STAGE53_SCHEMA_VERSION
    result["stage"] = "stage53_two_block_retrieval_hardening_audit"
    result["source_stage"] = "stage52_two_block_decoder_feasibility_audit"
    result["claim_boundary"] = _claim_boundary()
    result["decision"] = _stage53_decision(result["decision"])
    result["model"]["purpose"] = "retrieval exposure and training-budget hardening after Stage 52 feasibility"
    return result


def write_stage53_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    return write_stage52_outputs(result, output_dir)


def print_stage53_summary(result: dict[str, Any]) -> None:
    print_stage52_summary(result)
