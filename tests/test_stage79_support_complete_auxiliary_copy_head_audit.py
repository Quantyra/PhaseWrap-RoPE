from __future__ import annotations

import json

from qrope.stage79_support_complete_auxiliary_copy_head_audit import run_stage79_audit, write_stage79_outputs


def test_stage79_smoke_reports_support_complete_decision() -> None:
    result = run_stage79_audit(
        seeds=(307,),
        examples_per_length=6,
        method_names=("no_position", "rope_relative"),
        epochs=20,
        learning_rate=0.05,
        support_aux_weight=1.0,
    )
    assert result["stage"] == "stage79_support_complete_auxiliary_copy_head_audit"
    assert result["source_stage"] == "stage78_support_coverage_split_audit"
    if result["status"] == "blocked":
        assert result["blocked_reason"] == "missing_optional_autograd_dependency"
        return
    assert result["status"] == "completed"
    assert result["failed_runs"] == []
    assert result["decision"]["decision"] in {
        "SUPPORT_COMPLETE_AUXILIARY_COPY_HEAD_PHASE_CUED_REVIEW_REQUIRED",
        "SUPPORT_COMPLETE_AUXILIARY_COPY_HEAD_SUPPORT_RECOVERED_RETRIEVAL_FAILED",
        "SUPPORT_COMPLETE_AUXILIARY_COPY_HEAD_SUPPORT_NOT_RECOVERED",
    }


def test_stage79_records_support_complete_coverage() -> None:
    result = run_stage79_audit(
        seeds=(307,),
        examples_per_length=6,
        method_names=("no_position",),
        epochs=20,
        learning_rate=0.05,
    )
    if result["status"] == "blocked":
        return
    assert result["support_complete_policy"].startswith("examples_per_length=6")
    assert result["support_coverage"]["307"]["exact_query_support_fraction"] == 1.0
    assert "hard query-support lookup" in result["model"]["metadata_excluded"]


def test_stage79_outputs_are_written(tmp_path) -> None:
    result = run_stage79_audit(
        seeds=(307,),
        examples_per_length=6,
        method_names=("no_position",),
        epochs=20,
        learning_rate=0.05,
    )
    paths = write_stage79_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    assert set(paths) == {"manifest", "result", "summary_csv", "per_run_csv", "failed_runs"}
    assert manifest["stage"] == "stage79_support_complete_auxiliary_copy_head_audit"
    assert saved["stage"] == "stage79_support_complete_auxiliary_copy_head_audit"
    assert (tmp_path / "summary.csv").exists()
