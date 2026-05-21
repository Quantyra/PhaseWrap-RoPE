from __future__ import annotations

import json

from qrope.stage45_matched_decoder_only_gate import METHOD_NAMES
from qrope.stage65_pointer_generator_length_curriculum_audit import build_blocked_result, run_stage65_audit, write_stage65_outputs


def test_stage65_blocked_result_is_machine_readable() -> None:
    result = build_blocked_result()
    assert result["stage"] == "stage65_pointer_generator_length_curriculum_audit"
    assert result["status"] == "blocked"
    assert result["method_names"] == list(METHOD_NAMES)
    assert "a claim that validation-length curriculum training is the same as the original train-short/test-long gate" in result["claim_boundary"]["excluded"]


def test_stage65_smoke_reports_curriculum_decision_or_blocked() -> None:
    result = run_stage65_audit(
        seeds=(307,),
        examples_per_length=6,
        epochs=2,
        method_names=("no_position", "rope_relative"),
    )
    assert result["stage"] == "stage65_pointer_generator_length_curriculum_audit"
    if result["status"] == "blocked":
        assert result["blocked_reason"] == "missing_optional_autograd_dependency"
        return
    assert result["status"] == "completed"
    assert result["train_lengths"] == [24, 32, 40]
    assert result["test_lengths"] == [48, 64]
    assert result["support_coverage"]["307"]["test_known_fraction"] == 1.0
    assert result["failed_runs"] == []
    assert result["decision"]["decision"] in {
        "POINTER_GENERATOR_LENGTH_CURRICULUM_CAPACITY_NOT_ESTABLISHED",
        "POINTER_GENERATOR_LENGTH_CURRICULUM_RETRIEVAL_REVIEW_REQUIRED",
        "POINTER_GENERATOR_LENGTH_CURRICULUM_WITHOUT_RETRIEVAL_GENERALIZATION",
    }


def test_stage65_outputs_are_written(tmp_path) -> None:
    result = run_stage65_audit(
        seeds=(307,),
        examples_per_length=6,
        epochs=2,
        method_names=("no_position",),
    )
    paths = write_stage65_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved_name = "results.json" if result["status"] == "completed" else "preflight.json"
    saved = json.loads((tmp_path / saved_name).read_text(encoding="utf-8"))
    assert set(paths) >= {"manifest", "result", "summary_csv"}
    assert manifest["stage"] == "stage65_pointer_generator_length_curriculum_audit"
    assert saved["stage"] == "stage65_pointer_generator_length_curriculum_audit"
