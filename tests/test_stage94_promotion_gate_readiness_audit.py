from __future__ import annotations

import json
from pathlib import Path

from qrope.stage45_matched_decoder_only_gate import METHOD_NAMES
from qrope.stage94_promotion_gate_readiness_audit import SOURCE_STAGE_DIRS, run_stage94_audit, write_stage94_outputs


def _write_manifest(root: Path, stage: str, payload: dict[str, object]) -> None:
    stage_dir = root / stage
    stage_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "stage": stage,
        "status": "completed",
        "method_names": list(METHOD_NAMES),
        **payload,
    }
    (stage_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")


def test_stage94_bounds_claim_when_phasewrap_free_learned_solve_is_missing(tmp_path) -> None:
    _write_manifest(
        tmp_path,
        "stage67_content_key_retrieval_audit",
        {
            "tasks": ["content_key_retrieval"],
            "failed_runs_path": "failed_runs.json",
            "decision": {
                "decision": "CONTENT_KEY_RETRIEVAL_SOLVABLE_FOR_ALL_METHODS_NOT_PROMOTION",
                "retrieval_best_top1": {"content_key_retrieval": 1.0},
            },
        },
    )
    _write_manifest(
        tmp_path,
        "stage88_structural_retrieval_routed_copy_expert_audit",
        {
            "tasks": ["phase_cued_retrieval", "exact_offset_passkey", "tiny_text_fact_qa"],
            "failed_runs_path": "failed_runs.json",
            "decision": {
                "decision": "STRUCTURAL_RETRIEVAL_ROUTED_COPY_EXPERT_SOLVES_RETRIEVAL_NOT_PROMOTION",
                "retrieval_best_top1": {"phase_cued_retrieval": 0.783333, "exact_offset_passkey": 1.0},
                "retrieval_best_methods": {"phase_cued_retrieval": "rope_relative", "exact_offset_passkey": "rope_relative"},
            },
        },
    )
    _write_manifest(
        tmp_path,
        "stage93_toy_decoder_lane_boundary_audit",
        {
            "tasks": ["phase_cued_retrieval", "exact_offset_passkey"],
            "decision": {
                "decision": "TOY_DECODER_LANE_BOUND_FREE_RETRIEVAL_UNSOLVED",
                "free_learned_full_retrieval_solved": False,
            },
        },
    )

    result = run_stage94_audit(artifact_root=tmp_path)

    assert result["stage"] == "stage94_promotion_gate_readiness_audit"
    assert result["status"] == "completed"
    assert result["decision"]["decision"] == "PROMOTION_GATE_NOT_READY_STRONGEST_CLAIM_BOUNDED"
    assert result["decision"]["promotion_gate_ready"] is False
    assert "free_learned_phasewrap_original_retrieval_solve" in result["decision"]["failed_requirements"]
    assert "confidence_intervals_over_seeds" in result["decision"]["failed_requirements"]
    structural_row = next(row for row in result["requirement_rows"] if row["requirement"] == "structural_solve_not_overread")
    assert structural_row["status"] == "passed"


def test_stage94_can_mark_gate_ready_when_all_requirements_are_met(tmp_path) -> None:
    for stage in SOURCE_STAGE_DIRS:
        _write_manifest(
            tmp_path,
            stage,
            {
                "tasks": ["tiny_text_fact_qa"],
                "failed_runs_path": "failed_runs.json",
                "decision": {
                    "decision": "SYNTHETIC_BACKGROUND_FIXTURE",
                    "tiny_text_best_top1": 0.9,
                    "confidence_interval": {"tiny_text_fact_qa": [0.85, 0.95]},
                },
            },
        )
    _write_manifest(
        tmp_path,
        "stage95_headline_interval_audit",
        {
            "tasks": ["phase_cued_retrieval", "exact_offset_passkey"],
            "decision": {
                "decision": "HEADLINE_INTERVALS_ADDED_PROMOTION_STILL_BOUND",
                "confidence_interval_coverage": True,
            },
        },
    )
    _write_manifest(
        tmp_path,
        "stage89_structural_teacher_distilled_pointer_generator_audit",
        {
            "tasks": ["phase_cued_retrieval", "exact_offset_passkey", "tiny_text_fact_qa"],
            "failed_runs_path": "failed_runs.json",
            "decision": {
                "decision": "SYNTHETIC_PROMOTION_FIXTURE",
                "retrieval_best_top1": {"phase_cued_retrieval": 0.75, "exact_offset_passkey": 0.8},
                "retrieval_best_methods": {"phase_cued_retrieval": "phasewrap_bias", "exact_offset_passkey": "phasewrap_adapter"},
                "tiny_text_best_top1": 0.9,
                "confidence_interval": {"phase_cued_retrieval": [0.7, 0.8]},
            },
        },
    )
    _write_manifest(
        tmp_path,
        "stage88_structural_retrieval_routed_copy_expert_audit",
        {
            "tasks": ["phase_cued_retrieval", "exact_offset_passkey", "tiny_text_fact_qa"],
            "decision": {
                "decision": "STRUCTURAL_RETRIEVAL_ROUTED_COPY_EXPERT_SOLVES_RETRIEVAL_NOT_PROMOTION",
                "retrieval_best_top1": {"phase_cued_retrieval": 0.783333, "exact_offset_passkey": 1.0},
                "retrieval_best_methods": {"phase_cued_retrieval": "rope_relative", "exact_offset_passkey": "rope_relative"},
            },
        },
    )
    _write_manifest(
        tmp_path,
        "stage93_toy_decoder_lane_boundary_audit",
        {
            "tasks": ["phase_cued_retrieval", "exact_offset_passkey"],
            "decision": {
                "decision": "SYNTHETIC_READY_FIXTURE",
                "free_learned_full_retrieval_solved": False,
            },
        },
    )

    result = run_stage94_audit(artifact_root=tmp_path)

    assert result["decision"]["decision"] == "PROMOTION_GATE_READY_FOR_REVIEW"
    assert result["decision"]["promotion_gate_ready"] is True


def test_stage94_outputs_are_written(tmp_path) -> None:
    result = run_stage94_audit(artifact_root=tmp_path)
    paths = write_stage94_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((tmp_path / "out" / "results.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert manifest["stage"] == "stage94_promotion_gate_readiness_audit"
    assert saved["strongest_claim_effect"] == result["strongest_claim_effect"]
    assert "free_learned_phasewrap_original_retrieval_solve" in summary
