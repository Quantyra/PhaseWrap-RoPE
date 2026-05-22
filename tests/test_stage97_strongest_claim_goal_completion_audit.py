from __future__ import annotations

import json

from qrope.stage45_matched_decoder_only_gate import METHOD_NAMES
from qrope.stage97_strongest_claim_goal_completion_audit import run_stage97_audit, write_stage97_outputs


def _write_stage96(root) -> None:
    stage_dir = root / "stage96_claim_card_audit"
    stage_dir.mkdir(parents=True)
    payload = {
        "stage": "stage96_claim_card_audit",
        "method_names": list(METHOD_NAMES),
        "decision": {"headline_intervals_present": True},
        "missing_source_artifacts": [],
        "claim_card": {
            "strongest_honest_claim": "PhaseWrap-RoPE is a compact, auditable phase-wrap positional scoring rule.",
            "supported_evidence": [{"source": "a"}, {"source": "b"}, {"source": "c"}, {"source": "d"}],
            "failure_modes": [{"stage": "a"}, {"stage": "b"}, {"stage": "c"}, {"stage": "d"}],
            "unsupported_claims": [
                "PhaseWrap-RoPE replaces RoPE.",
                "PhaseWrap-RoPE is better than RoPE under current fair matched transformer comparisons.",
                "Bounded hardware/readout witnesses establish production language-model quality gains.",
            ],
            "promotion_gate_status": {
                "ready": False,
                "failed_requirements": ["free_learned_phasewrap_original_retrieval_solve"],
            },
            "headline_intervals": [{"headline": "free_learned_best_phase_cued"}],
            "reviewer_next_gate": "Run a stronger learned matched decoder-only transformer.",
        },
    }
    (stage_dir / "results.json").write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def test_stage97_marks_active_goal_complete_when_claim_card_satisfies_requirements(tmp_path) -> None:
    _write_stage96(tmp_path)

    result = run_stage97_audit(artifact_root=tmp_path)

    assert result["stage"] == "stage97_strongest_claim_goal_completion_audit"
    assert result["decision"]["decision"] == "ACTIVE_GOAL_COMPLETE_BOUND_STRONGEST_CLAIM"
    assert result["decision"]["active_goal_complete"] is True
    assert result["decision"]["failed_requirements"] == []
    assert all(row["status"] == "passed" for row in result["requirement_rows"])


def test_stage97_reports_missing_stage96(tmp_path) -> None:
    result = run_stage97_audit(artifact_root=tmp_path)

    assert result["decision"]["decision"] == "ACTIVE_GOAL_COMPLETION_AUDIT_FAILED"
    assert result["decision"]["active_goal_complete"] is False
    assert result["missing_source_artifacts"]


def test_stage97_outputs_are_written(tmp_path) -> None:
    _write_stage96(tmp_path)
    result = run_stage97_audit(artifact_root=tmp_path)
    paths = write_stage97_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((tmp_path / "out" / "results.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert manifest["stage"] == "stage97_strongest_claim_goal_completion_audit"
    assert saved["decision"]["active_goal_complete"] is True
    assert "strongest_honest_claim_present" in summary
