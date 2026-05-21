from __future__ import annotations

import json

from qrope.stage45_matched_decoder_only_gate import METHOD_NAMES
from qrope.stage66_positional_copy_expert_audit import build_blocked_result, run_stage66_audit, write_stage66_outputs


def test_stage66_blocked_result_is_machine_readable() -> None:
    result = build_blocked_result()
    assert result["stage"] == "stage66_positional_copy_expert_audit"
    assert result["status"] == "blocked"
    assert result["method_names"] == list(METHOD_NAMES)
    assert "a claim that a direct positional-copy expert is full decoder-only language-model validation" in result["claim_boundary"]["excluded"]


def test_stage66_smoke_reports_expert_decision_or_blocked() -> None:
    result = run_stage66_audit(
        seeds=(307,),
        examples_per_length=1,
        epochs=2,
        method_names=("no_position", "rope_relative"),
    )
    assert result["stage"] == "stage66_positional_copy_expert_audit"
    if result["status"] == "blocked":
        assert result["blocked_reason"] == "missing_optional_autograd_dependency"
        return
    assert result["status"] == "completed"
    assert result["failed_runs"] == []
    assert result["model"]["value_output_mode"].startswith("learned mixture")
    assert result["decision"]["decision"] in {
        "POSITIONAL_COPY_EXPERT_CAPACITY_NOT_ESTABLISHED",
        "POSITIONAL_COPY_EXPERT_RETRIEVAL_REVIEW_REQUIRED",
        "POSITIONAL_COPY_EXPERT_PARTIAL_RETRIEVAL_GENERALIZATION",
        "POSITIONAL_COPY_EXPERT_WITHOUT_RETRIEVAL_GENERALIZATION",
    }
    first_row = result["run_table"][0]
    assert "learned_expert_gate" in first_row
    assert "test_mean_expert_gate" in first_row


def test_stage66_outputs_are_written(tmp_path) -> None:
    result = run_stage66_audit(
        seeds=(307,),
        examples_per_length=1,
        epochs=2,
        method_names=("no_position",),
    )
    paths = write_stage66_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved_name = "results.json" if result["status"] == "completed" else "preflight.json"
    saved = json.loads((tmp_path / saved_name).read_text(encoding="utf-8"))
    assert set(paths) >= {"manifest", "result", "summary_csv"}
    assert manifest["stage"] == "stage66_positional_copy_expert_audit"
    assert saved["stage"] == "stage66_positional_copy_expert_audit"
