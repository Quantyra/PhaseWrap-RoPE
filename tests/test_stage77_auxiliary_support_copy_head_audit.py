from __future__ import annotations

import json

from qrope.stage77_auxiliary_support_copy_head_audit import run_stage77_audit, write_stage77_outputs


def test_stage77_smoke_reports_auxiliary_support_copy_decision() -> None:
    result = run_stage77_audit(
        seeds=(307,),
        examples_per_length=1,
        method_names=("no_position", "phasewrap_bias"),
        epochs=20,
        learning_rate=0.05,
        support_aux_weight=1.0,
    )
    assert result["stage"] == "stage77_auxiliary_support_copy_head_audit"
    assert result["source_stage"] == "stage76_integrated_support_copy_head_audit"
    if result["status"] == "blocked":
        assert result["blocked_reason"] == "missing_optional_autograd_dependency"
        return
    assert result["status"] == "completed"
    assert result["failed_runs"] == []
    assert result["decision"]["decision"] in {
        "AUXILIARY_SUPPORT_COPY_HEAD_SOLVES_PHASE_CUED_NOT_PROMOTION",
        "AUXILIARY_SUPPORT_COPY_HEAD_PARTIAL_RETRIEVAL",
        "AUXILIARY_SUPPORT_COPY_HEAD_RETRIEVAL_FAILED",
    }


def test_stage77_records_auxiliary_weight_and_exclusions() -> None:
    result = run_stage77_audit(
        seeds=(307,),
        examples_per_length=1,
        method_names=("no_position",),
        epochs=20,
        learning_rate=0.05,
        support_aux_weight=0.5,
    )
    if result["status"] == "blocked":
        return
    assert result["support_aux_weight"] == 0.5
    assert result["models"]
    assert "hard query-support lookup" in result["model"]["metadata_excluded"]
    assert "standalone pretrained support head" in result["model"]["metadata_excluded"]


def test_stage77_outputs_are_written(tmp_path) -> None:
    result = run_stage77_audit(
        seeds=(307,),
        examples_per_length=1,
        method_names=("no_position",),
        epochs=20,
        learning_rate=0.05,
        support_aux_weight=1.0,
    )
    paths = write_stage77_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    assert set(paths) == {"manifest", "result", "summary_csv", "per_run_csv", "failed_runs"}
    assert manifest["stage"] == "stage77_auxiliary_support_copy_head_audit"
    assert saved["stage"] == "stage77_auxiliary_support_copy_head_audit"
    assert (tmp_path / "summary.csv").exists()
