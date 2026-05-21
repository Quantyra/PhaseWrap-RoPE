from __future__ import annotations

import json

from qrope.stage75_learned_query_support_head_audit import run_stage75_audit, write_stage75_outputs


def test_stage75_smoke_reports_learned_support_head_decision() -> None:
    result = run_stage75_audit(
        seeds=(307, 311),
        examples_per_length=1,
        method_names=("no_position", "phasewrap_bias"),
        position_scales=(0.0,),
        cue_scales=(0.0, 8.0),
        distance_scales=(0.0, 4.0),
        support_head_epochs=80,
        support_head_learning_rate=0.3,
    )
    assert result["stage"] == "stage75_learned_query_support_head_audit"
    assert result["status"] == "completed"
    assert result["source_stage"] == "stage74_leave_one_seed_query_support_audit"
    assert result["failed_runs"] == []
    assert result["decision"]["decision"] in {
        "LEARNED_QUERY_SUPPORT_HEAD_SOLVES_PHASE_CUED_NOT_PROMOTION",
        "LEARNED_QUERY_SUPPORT_HEAD_PARTIAL_RETRIEVAL",
        "LEARNED_QUERY_SUPPORT_HEAD_RETRIEVAL_FAILED",
    }


def test_stage75_trains_support_heads_without_hard_lookup() -> None:
    result = run_stage75_audit(
        seeds=(307, 311),
        examples_per_length=1,
        method_names=("no_position",),
        position_scales=(0.0,),
        cue_scales=(8.0,),
        distance_scales=(4.0,),
        support_head_epochs=80,
        support_head_learning_rate=0.3,
    )
    heads = result["support_heads"]
    assert set(heads) == {"307", "311"}
    assert all("weights" in head for head in heads.values())
    assert all(len(head["classes"]) > 1 for head in heads.values())
    assert "hard query-support lookup" in result["model"]["metadata_excluded"]


def test_stage75_outputs_are_written(tmp_path) -> None:
    result = run_stage75_audit(
        seeds=(307, 311),
        examples_per_length=1,
        method_names=("no_position",),
        position_scales=(0.0,),
        cue_scales=(8.0,),
        distance_scales=(4.0,),
        support_head_epochs=80,
        support_head_learning_rate=0.3,
    )
    paths = write_stage75_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    assert set(paths) == {"manifest", "result", "summary_csv", "per_run_csv", "failed_runs"}
    assert manifest["stage"] == "stage75_learned_query_support_head_audit"
    assert saved["support_heads"]
    assert (tmp_path / "summary.csv").exists()
