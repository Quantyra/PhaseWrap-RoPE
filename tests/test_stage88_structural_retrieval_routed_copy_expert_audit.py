from __future__ import annotations

import json

from qrope.stage10_small_decoder_transformer import TASK_NAMES
from qrope.stage45_matched_decoder_only_gate import METHOD_NAMES
from qrope.stage88_structural_retrieval_routed_copy_expert_audit import (
    build_blocked_result,
    run_stage88_audit,
    write_stage88_outputs,
)


def test_stage88_blocked_result_is_machine_readable() -> None:
    result = build_blocked_result()
    assert result["stage"] == "stage88_structural_retrieval_routed_copy_expert_audit"
    assert result["status"] == "blocked"
    assert result["method_names"] == list(METHOD_NAMES)
    assert result["tasks"] == list(TASK_NAMES)
    assert result["source_stage"] == "stage87_in_decoder_support_routed_copy_expert_audit"


def test_stage88_smoke_reports_structural_retrieval_expert_decision_or_blocked() -> None:
    result = run_stage88_audit(
        seeds=(307,),
        examples_per_length=6,
        epochs=2,
        method_names=("no_position", "sinusoidal"),
    )
    assert result["stage"] == "stage88_structural_retrieval_routed_copy_expert_audit"
    if result["status"] == "blocked":
        assert result["blocked_reason"] == "missing_optional_autograd_dependency"
        return
    assert result["status"] == "completed"
    assert result["tasks"] == list(TASK_NAMES)
    assert result["failed_runs"] == []
    assert result["decision"]["decision"] in {
        "STRUCTURAL_RETRIEVAL_ROUTED_COPY_EXPERT_CAPACITY_NOT_ESTABLISHED",
        "STRUCTURAL_RETRIEVAL_ROUTED_COPY_EXPERT_SOLVES_RETRIEVAL_REVIEW_REQUIRED",
        "STRUCTURAL_RETRIEVAL_ROUTED_COPY_EXPERT_SOLVES_RETRIEVAL_NOT_PROMOTION",
        "STRUCTURAL_RETRIEVAL_ROUTED_COPY_EXPERT_PARTIAL_RETRIEVAL",
        "STRUCTURAL_RETRIEVAL_ROUTED_COPY_EXPERT_WITHOUT_RETRIEVAL_GENERALIZATION",
    }
    assert result["model"]["type"] == "two_block_pointer_generator_structural_retrieval_routed_copy_expert"
    assert "decoder-predicted support probabilities" in result["model"]["phase_cued_routing_policy"]
    assert "positional-bias score" in result["model"]["exact_offset_routing_policy"]
    first_run = result["run_table"][0]
    assert first_run["support_route_weight"] == result["support_route_weight"]
    assert first_run["exact_offset_route_weight"] == result["exact_offset_route_weight"]
    assert first_run["multitask_train_row_count"] > first_run["task_train_row_count"]


def test_stage88_outputs_are_written(tmp_path) -> None:
    result = run_stage88_audit(
        seeds=(307,),
        examples_per_length=1,
        epochs=2,
        method_names=("no_position",),
    )
    paths = write_stage88_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved_name = "results.json" if result["status"] == "completed" else "preflight.json"
    saved = json.loads((tmp_path / saved_name).read_text(encoding="utf-8"))
    assert set(paths) >= {"manifest", "result", "summary_csv"}
    assert manifest["stage"] == "stage88_structural_retrieval_routed_copy_expert_audit"
    assert saved["stage"] == "stage88_structural_retrieval_routed_copy_expert_audit"
