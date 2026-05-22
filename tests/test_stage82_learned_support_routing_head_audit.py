from __future__ import annotations

import json

from qrope.stage82_learned_support_routing_head_audit import run_stage82_audit, write_stage82_outputs


def test_stage82_smoke_reports_learned_routing_decision() -> None:
    result = run_stage82_audit(
        seeds=(307,),
        examples_per_length=6,
        method_names=("no_position", "rope_relative"),
        epochs=20,
        learning_rate=0.05,
        support_aux_weight=1.0,
        routing_epochs=20,
        routing_learning_rate=0.1,
    )
    assert result["stage"] == "stage82_learned_support_routing_head_audit"
    assert result["source_stage"] == "stage81_soft_support_routed_token_selector_audit"
    if result["status"] == "blocked":
        assert result["blocked_reason"] == "missing_optional_autograd_dependency"
        return
    assert result["status"] == "completed"
    assert result["failed_runs"] == []
    assert result["decision"]["decision"] in {
        "LEARNED_SUPPORT_ROUTING_HEAD_SOLVES_PHASE_CUED_NOT_PROMOTION",
        "LEARNED_SUPPORT_ROUTING_HEAD_PHASE_CUED_REVIEW_REQUIRED",
        "LEARNED_SUPPORT_ROUTING_HEAD_SUPPORT_RECOVERED_RETRIEVAL_FAILED",
        "LEARNED_SUPPORT_ROUTING_HEAD_SUPPORT_NOT_RECOVERED",
    }


def test_stage82_records_learned_routing_policy() -> None:
    result = run_stage82_audit(
        seeds=(307,),
        examples_per_length=6,
        method_names=("no_position",),
        epochs=20,
        learning_rate=0.05,
        routing_epochs=20,
        routing_learning_rate=0.1,
    )
    if result["status"] == "blocked":
        return
    assert result["support_coverage"]["307"]["exact_query_support_fraction"] == 1.0
    assert result["model"]["type"] == "same_seed_support_complete_learned_support_routing_head"
    assert "learned support-congruence" in result["model"]["value_output_mode"]
    assert "hard farthest-congruent selector" in result["model"]["metadata_excluded"]
    assert "routing_heads" in result


def test_stage82_outputs_are_written(tmp_path) -> None:
    result = run_stage82_audit(
        seeds=(307,),
        examples_per_length=6,
        method_names=("no_position",),
        epochs=20,
        learning_rate=0.05,
        routing_epochs=20,
        routing_learning_rate=0.1,
    )
    paths = write_stage82_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    assert set(paths) == {"manifest", "result", "summary_csv", "per_run_csv", "failed_runs"}
    assert manifest["stage"] == "stage82_learned_support_routing_head_audit"
    assert saved["stage"] == "stage82_learned_support_routing_head_audit"
    assert (tmp_path / "summary.csv").exists()
