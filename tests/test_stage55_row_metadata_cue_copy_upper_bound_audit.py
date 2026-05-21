from __future__ import annotations

import json

from qrope.stage45_matched_decoder_only_gate import METHOD_NAMES
from qrope.stage55_row_metadata_cue_copy_upper_bound_audit import (
    TASK_NAMES,
    build_blocked_result,
    run_stage55_audit,
    write_stage55_outputs,
)


def test_stage55_blocked_result_is_machine_readable() -> None:
    result = build_blocked_result()
    assert result["stage"] == "stage55_row_metadata_cue_copy_upper_bound_audit"
    assert result["status"] == "blocked"
    assert result["no_hardware_submission"] is True
    assert result["provider_credentials_required"] is False
    assert result["method_names"] == list(METHOD_NAMES)
    assert "a claim that explicit row metadata is a standard decoder-only input feature" in result["claim_boundary"]["excluded"]


def test_stage55_smoke_reports_upper_bound_decision() -> None:
    result = run_stage55_audit(
        seeds=(307,),
        examples_per_length=1,
        method_names=("rope_relative", "phasewrap_bias", "no_position"),
        position_scales=(0.0, 1.0),
        cue_scales=(0.0, 4.0),
        distance_scales=(0.0, 4.0),
    )
    assert result["status"] == "completed"
    assert result["stage"] == "stage55_row_metadata_cue_copy_upper_bound_audit"
    assert result["tasks"] == list(TASK_NAMES)
    assert result["failed_runs"] == []
    assert len(result["aggregate_table"]) == 3 * len(TASK_NAMES)
    assert result["decision"]["decision"] in {
        "ROW_METADATA_CUE_COPY_UPPER_BOUND_SOLVES_RETRIEVAL_NOT_PROMOTION",
        "ROW_METADATA_CUE_COPY_PARTIAL_RETRIEVAL_UPPER_BOUND",
        "ROW_METADATA_CUE_COPY_UPPER_BOUND_FAILED",
    }
    assert "no_position_solved_retrieval_tasks" in result["decision"]


def test_stage55_outputs_are_written(tmp_path) -> None:
    result = run_stage55_audit(
        seeds=(307,),
        examples_per_length=1,
        method_names=METHOD_NAMES[:2],
        position_scales=(0.0, 1.0),
        cue_scales=(0.0, 4.0),
        distance_scales=(0.0, 4.0),
    )
    paths = write_stage55_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    assert set(paths) == {"manifest", "result", "summary_csv", "per_run_csv", "failed_runs"}
    assert manifest["stage"] == "stage55_row_metadata_cue_copy_upper_bound_audit"
    assert manifest["decision"] == result["decision"]
    assert saved["aggregate_table"] == result["aggregate_table"]
