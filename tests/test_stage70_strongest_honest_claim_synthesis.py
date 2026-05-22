from __future__ import annotations

import json
from pathlib import Path

from qrope.stage45_matched_decoder_only_gate import METHOD_NAMES
from qrope.stage70_strongest_honest_claim_synthesis import (
    run_stage70_synthesis,
    write_stage70_outputs,
)


def _write_manifest(root: Path, stage: str, manifest: dict[str, object]) -> None:
    stage_dir = root / stage
    stage_dir.mkdir(parents=True)
    payload = {"stage": stage, "status": "completed", "method_names": list(METHOD_NAMES), **manifest}
    (stage_dir / "manifest.json").write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def test_stage70_synthesis_bounds_claim_with_retrieval_failures(tmp_path) -> None:
    _write_manifest(
        tmp_path,
        "stage67_content_key_retrieval_audit",
        {
            "tasks": ["content_key_retrieval"],
            "decision": {
                "decision": "CONTENT_KEY_RETRIEVAL_SOLVABLE_FOR_ALL_METHODS_NOT_PROMOTION",
                "retrieval_best_top1": {"content_key_retrieval": 1.0},
                "retrieval_generalized_methods": list(METHOD_NAMES),
            },
        },
    )
    _write_manifest(
        tmp_path,
        "stage69_original_multitask_pointer_generator_audit",
        {
            "tasks": ["phase_cued_retrieval", "exact_offset_passkey", "tiny_text_fact_qa"],
            "decision": {
                "decision": "ORIGINAL_MULTITASK_POINTER_GENERATOR_WITHOUT_RETRIEVAL_GENERALIZATION",
                "capacity_established": True,
                "retrieval_best_top1": {"phase_cued_retrieval": 0.016667, "exact_offset_passkey": 0.033333},
                "retrieval_best_methods": {"phase_cued_retrieval": "no_position", "exact_offset_passkey": "sinusoidal"},
                "tiny_text_best_top1": 0.516667,
                "tiny_text_best_method": "sinusoidal",
            },
        },
    )
    _write_manifest(
        tmp_path,
        "stage84_support_auxiliary_pointer_generator_audit",
        {
            "tasks": ["phase_cued_retrieval", "exact_offset_passkey", "tiny_text_fact_qa"],
            "decision": {
                "decision": "SUPPORT_AUXILIARY_POINTER_GENERATOR_WITHOUT_RETRIEVAL_GENERALIZATION",
                "capacity_established": True,
                "retrieval_best_top1": {"phase_cued_retrieval": 0.016667, "exact_offset_passkey": 0.033333},
                "retrieval_best_methods": {"phase_cued_retrieval": "sinusoidal", "exact_offset_passkey": "sinusoidal"},
                "tiny_text_best_top1": 0.583333,
                "tiny_text_best_method": "sinusoidal",
            },
        },
    )
    result = run_stage70_synthesis(artifact_root=tmp_path)
    assert result["stage"] == "stage70_strongest_honest_claim_synthesis"
    assert result["status"] == "completed"
    assert result["method_names"] == list(METHOD_NAMES)
    assert result["decision"]["decision"] == "BOUND_STRONGEST_HONEST_CLAIM_WITH_RETRIEVAL_FAILURES"
    assert "RoPE replacement" in result["strongest_honest_claim"]
    assert any("replaces RoPE" in claim for claim in result["unsupported_claims"])
    assert any(item.get("source") == "stage67_content_key_retrieval_audit" for item in result["positive_evidence"])
    assert any(item.get("stage") == "stage69_original_multitask_pointer_generator_audit" for item in result["failure_modes"])
    assert any(item.get("stage") == "stage84_support_auxiliary_pointer_generator_audit" for item in result["failure_modes"])
    assert result["source_stage"] == "stage84_support_auxiliary_pointer_generator_audit"


def test_stage70_labels_nonpromotional_solved_retrieval_without_calling_it_unrepaired(tmp_path) -> None:
    _write_manifest(
        tmp_path,
        "stage80_support_routed_token_selector_audit",
        {
            "tasks": ["phase_cued_retrieval", "exact_offset_passkey", "tiny_text_fact_qa"],
            "decision": {
                "decision": "SUPPORT_ROUTED_TOKEN_SELECTOR_SOLVES_PHASE_CUED_NOT_PROMOTION",
                "capacity_established": None,
                "retrieval_best_top1": {"phase_cued_retrieval": 1.0, "exact_offset_passkey": 0.65},
                "retrieval_best_methods": {"phase_cued_retrieval": "no_position", "exact_offset_passkey": "sinusoidal"},
                "tiny_text_best_top1": 1.0,
                "tiny_text_best_method": "sinusoidal",
            },
        },
    )
    result = run_stage70_synthesis(artifact_root=tmp_path)
    stage80_rows = [item for item in result["failure_modes"] if item.get("stage") == "stage80_support_routed_token_selector_audit"]
    assert stage80_rows
    assert "non-promotional" in stage80_rows[0]["failure"]


def test_stage70_synthesis_flags_promotion_review_when_phasewrap_leads(tmp_path) -> None:
    _write_manifest(
        tmp_path,
        "stage67_content_key_retrieval_audit",
        {
            "tasks": ["content_key_retrieval"],
            "decision": {
                "decision": "CONTENT_KEY_RETRIEVAL_SOLVABLE_FOR_ALL_METHODS_NOT_PROMOTION",
                "retrieval_best_top1": {"content_key_retrieval": 1.0},
                "retrieval_generalized_methods": list(METHOD_NAMES),
            },
        },
    )
    _write_manifest(
        tmp_path,
        "stage69_original_multitask_pointer_generator_audit",
        {
            "tasks": ["phase_cued_retrieval", "exact_offset_passkey", "tiny_text_fact_qa"],
            "decision": {
                "decision": "SYNTHETIC_REVIEW_FIXTURE",
                "capacity_established": True,
                "retrieval_best_top1": {"phase_cued_retrieval": 0.75, "exact_offset_passkey": 0.8},
                "retrieval_best_methods": {"phase_cued_retrieval": "phasewrap_bias", "exact_offset_passkey": "phasewrap_adapter"},
            },
        },
    )
    result = run_stage70_synthesis(artifact_root=tmp_path)
    assert result["decision"]["decision"] == "PROMOTION_REVIEW_REQUIRED"
    assert result["decision"]["promotion_review_supported"] is True


def test_stage70_outputs_are_written(tmp_path) -> None:
    result = run_stage70_synthesis(artifact_root=tmp_path)
    paths = write_stage70_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((tmp_path / "out" / "results.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")
    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert manifest["stage"] == "stage70_strongest_honest_claim_synthesis"
    assert saved["strongest_honest_claim"] == result["strongest_honest_claim"]
    assert "unsupported_claim" in summary
