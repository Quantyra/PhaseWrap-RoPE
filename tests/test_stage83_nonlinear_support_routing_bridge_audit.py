from __future__ import annotations

import json

from qrope.stage83_nonlinear_support_routing_bridge_audit import run_stage83_audit, write_stage83_outputs


def test_stage83_smoke_reports_nonlinear_routing_decision() -> None:
    result = run_stage83_audit(
        seeds=(307,),
        examples_per_length=6,
        method_names=("no_position", "rope_relative"),
        epochs=20,
        learning_rate=0.05,
        support_aux_weight=1.0,
        routing_epochs=20,
        routing_learning_rate=0.03,
        routing_hidden_width=4,
    )
    assert result["stage"] == "stage83_nonlinear_support_routing_bridge_audit"
    assert result["source_stage"] == "stage82_learned_support_routing_head_audit"
    if result["status"] == "blocked":
        assert result["blocked_reason"] == "missing_optional_autograd_dependency"
        return
    assert result["status"] == "completed"
    assert result["failed_runs"] == []
    assert result["decision"]["decision"] in {
        "NONLINEAR_SUPPORT_ROUTING_BRIDGE_SOLVES_PHASE_CUED_NOT_PROMOTION",
        "NONLINEAR_SUPPORT_ROUTING_BRIDGE_PHASE_CUED_REVIEW_REQUIRED",
        "NONLINEAR_SUPPORT_ROUTING_BRIDGE_SUPPORT_RECOVERED_RETRIEVAL_FAILED",
        "NONLINEAR_SUPPORT_ROUTING_BRIDGE_SUPPORT_NOT_RECOVERED",
    }


def test_stage83_records_learned_routing_policy() -> None:
    result = run_stage83_audit(
        seeds=(307,),
        examples_per_length=6,
        method_names=("no_position",),
        epochs=20,
        learning_rate=0.05,
        routing_epochs=20,
        routing_learning_rate=0.03,
        routing_hidden_width=4,
    )
    if result["status"] == "blocked":
        return
    assert result["support_coverage"]["307"]["exact_query_support_fraction"] == 1.0
    assert result["model"]["type"] == "same_seed_support_complete_nonlinear_support_routing_bridge"
    assert "nonlinear learned per-position bridge" in result["model"]["value_output_mode"]
    assert "hard farthest-congruent selector" in result["model"]["metadata_excluded"]
    assert "routing_heads" in result
    assert result["routing_hidden_width"] == 4
    assert "position_bias_x_support" in result["routing_feature_names"]


def test_stage83_outputs_are_written(tmp_path) -> None:
    result = run_stage83_audit(
        seeds=(307,),
        examples_per_length=6,
        method_names=("no_position",),
        epochs=20,
        learning_rate=0.05,
        routing_epochs=20,
        routing_learning_rate=0.03,
        routing_hidden_width=4,
    )
    paths = write_stage83_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    assert set(paths) == {"manifest", "result", "summary_csv", "per_run_csv", "failed_runs"}
    assert manifest["stage"] == "stage83_nonlinear_support_routing_bridge_audit"
    assert saved["stage"] == "stage83_nonlinear_support_routing_bridge_audit"
    assert (tmp_path / "summary.csv").exists()
