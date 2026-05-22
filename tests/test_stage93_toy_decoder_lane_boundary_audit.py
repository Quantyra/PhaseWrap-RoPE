from __future__ import annotations

import json
from pathlib import Path

from qrope.stage45_matched_decoder_only_gate import METHOD_NAMES
from qrope.stage93_toy_decoder_lane_boundary_audit import run_stage93_audit, write_stage93_outputs


def _write_manifest(root: Path, stage: str, decision: dict[str, object]) -> None:
    stage_dir = root / stage
    stage_dir.mkdir(parents=True)
    payload = {
        "stage": stage,
        "status": "completed",
        "method_names": list(METHOD_NAMES),
        "tasks": ["phase_cued_retrieval", "exact_offset_passkey", "tiny_text_fact_qa"],
        "decision": decision,
    }
    (stage_dir / "manifest.json").write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def test_stage93_bounds_toy_decoder_lane_when_structural_solves_but_free_learned_fails(tmp_path) -> None:
    _write_manifest(
        tmp_path,
        "stage88_structural_retrieval_routed_copy_expert_audit",
        {
            "decision": "STRUCTURAL_RETRIEVAL_ROUTED_COPY_EXPERT_SOLVES_RETRIEVAL_NOT_PROMOTION",
            "capacity_established": True,
            "retrieval_best_top1": {"phase_cued_retrieval": 0.783333, "exact_offset_passkey": 1.0},
            "retrieval_best_methods": {"phase_cued_retrieval": "rope_relative", "exact_offset_passkey": "rope_relative"},
            "tiny_text_best_top1": 0.933334,
            "tiny_text_best_method": "sinusoidal",
        },
    )
    _write_manifest(
        tmp_path,
        "stage89_structural_teacher_distilled_pointer_generator_audit",
        {
            "decision": "STRUCTURAL_TEACHER_DISTILLED_POINTER_GENERATOR_WITHOUT_RETRIEVAL_GENERALIZATION",
            "capacity_established": True,
            "retrieval_best_top1": {"phase_cued_retrieval": 0.05, "exact_offset_passkey": 0.366667},
            "retrieval_best_methods": {"phase_cued_retrieval": "sinusoidal", "exact_offset_passkey": "sinusoidal"},
            "tiny_text_best_top1": 0.866667,
            "tiny_text_best_method": "sinusoidal",
        },
    )
    _write_manifest(
        tmp_path,
        "stage92_support_binding_teacher_pointer_generator_audit",
        {
            "decision": "SUPPORT_BINDING_TEACHER_POINTER_GENERATOR_WITHOUT_RETRIEVAL_GENERALIZATION",
            "capacity_established": True,
            "retrieval_best_top1": {"phase_cued_retrieval": 0.05, "exact_offset_passkey": 0.366667},
            "retrieval_best_methods": {"phase_cued_retrieval": "alibi", "exact_offset_passkey": "sinusoidal"},
            "tiny_text_best_top1": 0.883333,
            "tiny_text_best_method": "sinusoidal",
        },
    )

    result = run_stage93_audit(artifact_root=tmp_path)

    assert result["stage"] == "stage93_toy_decoder_lane_boundary_audit"
    assert result["status"] == "completed"
    assert result["method_names"] == list(METHOD_NAMES)
    assert result["decision"]["decision"] == "TOY_DECODER_LANE_BOUND_FREE_RETRIEVAL_UNSOLVED"
    assert result["decision"]["structural_retrieval_solved"] is True
    assert result["decision"]["free_learned_full_retrieval_solved"] is False
    assert result["decision"]["phasewrap_free_learned_promotion_supported"] is False
    assert result["free_learned_best_top1_by_task"]["exact_offset_passkey"]["top1"] == 0.366667
    assert "stronger matched decoder-only transformer" in result["reviewer_next_gate"]


def test_stage93_flags_promotion_review_only_for_phasewrap_led_free_learned_solve(tmp_path) -> None:
    _write_manifest(
        tmp_path,
        "stage89_structural_teacher_distilled_pointer_generator_audit",
        {
            "decision": "SYNTHETIC_PHASEWRAP_FREE_SOLVE",
            "capacity_established": True,
            "retrieval_best_top1": {"phase_cued_retrieval": 0.75, "exact_offset_passkey": 0.8},
            "retrieval_best_methods": {"phase_cued_retrieval": "phasewrap_bias", "exact_offset_passkey": "phasewrap_adapter"},
        },
    )

    result = run_stage93_audit(artifact_root=tmp_path)

    assert result["decision"]["decision"] == "TOY_DECODER_LANE_PROMOTION_REVIEW_REQUIRED"
    assert result["decision"]["phasewrap_free_learned_promotion_supported"] is True
    assert result["decision"]["phasewrap_free_learned_solve_stages"] == ["stage89_structural_teacher_distilled_pointer_generator_audit"]


def test_stage93_outputs_are_written(tmp_path) -> None:
    result = run_stage93_audit(artifact_root=tmp_path)
    paths = write_stage93_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((tmp_path / "out" / "results.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert manifest["stage"] == "stage93_toy_decoder_lane_boundary_audit"
    assert saved["lane_boundary"] == result["lane_boundary"]
    assert "next_gate" in summary
