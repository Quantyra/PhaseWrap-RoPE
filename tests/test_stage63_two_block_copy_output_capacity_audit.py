from __future__ import annotations

import json

from qrope.stage45_matched_decoder_only_gate import METHOD_NAMES
from qrope.stage63_two_block_copy_output_capacity_audit import build_blocked_result, run_stage63_audit, write_stage63_outputs


def test_stage63_blocked_result_is_machine_readable() -> None:
    result = build_blocked_result()
    assert result["stage"] == "stage63_two_block_copy_output_capacity_audit"
    assert result["status"] == "blocked"
    assert result["method_names"] == list(METHOD_NAMES)
    assert "a claim that copy-output repair is equivalent to free learned value generation" in result["claim_boundary"]["excluded"]


def test_stage63_smoke_reports_copy_output_decision_or_blocked() -> None:
    result = run_stage63_audit(
        seeds=(307,),
        examples_per_length=6,
        epochs=2,
        method_names=("no_position", "rope_relative"),
    )
    assert result["stage"] == "stage63_two_block_copy_output_capacity_audit"
    if result["status"] == "blocked":
        assert result["blocked_reason"] == "missing_optional_autograd_dependency"
        return
    assert result["status"] == "completed"
    assert result["support_coverage"]["307"]["test_known_fraction"] == 1.0
    assert result["failed_runs"] == []
    assert result["decision"]["decision"] in {
        "TWO_BLOCK_COPY_OUTPUT_CAPACITY_NOT_ESTABLISHED",
        "TWO_BLOCK_COPY_OUTPUT_RETRIEVAL_REVIEW_REQUIRED",
        "TWO_BLOCK_COPY_OUTPUT_CAPACITY_WITHOUT_RETRIEVAL_GENERALIZATION",
    }


def test_stage63_outputs_are_written(tmp_path) -> None:
    result = run_stage63_audit(
        seeds=(307,),
        examples_per_length=6,
        epochs=2,
        method_names=("no_position",),
    )
    paths = write_stage63_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved_name = "results.json" if result["status"] == "completed" else "preflight.json"
    saved = json.loads((tmp_path / saved_name).read_text(encoding="utf-8"))
    assert set(paths) >= {"manifest", "result", "summary_csv"}
    assert manifest["stage"] == "stage63_two_block_copy_output_capacity_audit"
    assert saved["stage"] == "stage63_two_block_copy_output_capacity_audit"
