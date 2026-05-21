from __future__ import annotations

import json

from qrope.stage45_matched_decoder_only_gate import METHOD_NAMES
from qrope.stage61_support_complete_two_block_audit import build_blocked_result, run_stage61_audit, write_stage61_outputs


def test_stage61_blocked_result_is_machine_readable() -> None:
    result = build_blocked_result()
    assert result["stage"] == "stage61_support_complete_two_block_audit"
    assert result["status"] == "blocked"
    assert result["no_hardware_submission"] is True
    assert result["provider_credentials_required"] is False
    assert result["method_names"] == list(METHOD_NAMES)
    assert "a claim that support-complete training alone establishes learned retrieval generalization" in result["claim_boundary"]["excluded"]


def test_stage61_smoke_reports_support_coverage_or_blocked() -> None:
    result = run_stage61_audit(
        seeds=(307,),
        examples_per_length=6,
        epochs=2,
        method_names=("no_position", "rope_relative"),
    )
    assert result["stage"] == "stage61_support_complete_two_block_audit"
    if result["status"] == "blocked":
        assert result["blocked_reason"] == "missing_optional_autograd_dependency"
        return
    assert result["status"] == "completed"
    assert result["support_coverage"]["307"]["test_known_fraction"] == 1.0
    assert result["failed_runs"] == []
    assert result["decision"]["decision"] in {
        "SUPPORT_COMPLETE_TWO_BLOCK_CAPACITY_NOT_ESTABLISHED",
        "SUPPORT_COMPLETE_TWO_BLOCK_RETRIEVAL_REVIEW_REQUIRED",
        "SUPPORT_COMPLETE_TWO_BLOCK_RETRIEVAL_FAILED",
    }


def test_stage61_outputs_are_written(tmp_path) -> None:
    result = run_stage61_audit(
        seeds=(307,),
        examples_per_length=6,
        epochs=2,
        method_names=("no_position",),
    )
    paths = write_stage61_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved_name = "results.json" if result["status"] == "completed" else "preflight.json"
    saved = json.loads((tmp_path / saved_name).read_text(encoding="utf-8"))
    assert set(paths) >= {"manifest", "result", "summary_csv"}
    assert manifest["stage"] == "stage61_support_complete_two_block_audit"
    assert saved["stage"] == "stage61_support_complete_two_block_audit"
