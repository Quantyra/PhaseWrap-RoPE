from __future__ import annotations

import json

from qrope.stage45_matched_decoder_only_gate import METHOD_NAMES
from qrope.stage53_two_block_retrieval_hardening_audit import (
    TASK_NAMES,
    build_blocked_result,
    run_stage53_audit,
    write_stage53_outputs,
)


def test_stage53_blocked_result_is_machine_readable() -> None:
    result = build_blocked_result()
    assert result["stage"] == "stage53_two_block_retrieval_hardening_audit"
    assert result["status"] == "blocked"
    assert result["no_hardware_submission"] is True
    assert result["provider_credentials_required"] is False
    assert result["method_names"] == list(METHOD_NAMES)
    assert "a claim that PhaseWrap-RoPE replaces RoPE" in result["claim_boundary"]["excluded"]


def test_stage53_smoke_reports_hardening_decision() -> None:
    result = run_stage53_audit(
        seeds=(307,),
        examples_per_length=1,
        epochs=2,
        method_names=("rope_relative", "phasewrap_bias", "no_position"),
    )
    assert result["status"] == "completed"
    assert result["stage"] == "stage53_two_block_retrieval_hardening_audit"
    assert result["tasks"] == list(TASK_NAMES)
    assert result["failed_runs"] == []
    assert len(result["aggregate_table"]) == 3 * len(TASK_NAMES)
    assert result["decision"]["decision"] in {
        "TWO_BLOCK_RETRIEVAL_HARDENING_GENERALIZATION_PRESENT_REVIEW_REQUIRED",
        "TWO_BLOCK_RETRIEVAL_HARDENING_FAILED",
    }
    assert "retrieval_hardening_generalization_top1_threshold" in result["decision"]


def test_stage53_outputs_are_written(tmp_path) -> None:
    result = run_stage53_audit(seeds=(307,), examples_per_length=1, epochs=2, method_names=METHOD_NAMES[:2])
    paths = write_stage53_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    assert set(paths) == {"manifest", "result", "summary_csv", "per_run_csv", "failed_runs"}
    assert manifest["stage"] == "stage53_two_block_retrieval_hardening_audit"
    assert manifest["decision"] == result["decision"]
    assert saved["aggregate_table"] == result["aggregate_table"]
