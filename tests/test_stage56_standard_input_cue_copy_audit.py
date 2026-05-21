from __future__ import annotations

import json

from qrope.stage45_matched_decoder_only_gate import METHOD_NAMES
from qrope.stage56_standard_input_cue_copy_audit import TASK_NAMES, build_blocked_result, run_stage56_audit, write_stage56_outputs


def test_stage56_blocked_result_is_machine_readable() -> None:
    result = build_blocked_result()
    assert result["stage"] == "stage56_standard_input_cue_copy_audit"
    assert result["status"] == "blocked"
    assert result["no_hardware_submission"] is True
    assert result["provider_credentials_required"] is False
    assert result["method_names"] == list(METHOD_NAMES)
    assert "a claim that visible query-token cue decoding is a learned decoder-only transformer result" in result["claim_boundary"]["excluded"]


def test_stage56_smoke_reports_standard_input_decision() -> None:
    result = run_stage56_audit(
        seeds=(307,),
        examples_per_length=1,
        method_names=("rope_relative", "phasewrap_bias", "no_position"),
        position_scales=(0.0, 1.0),
        cue_scales=(0.0, 4.0),
        distance_scales=(0.0, 4.0),
    )
    assert result["status"] == "completed"
    assert result["stage"] == "stage56_standard_input_cue_copy_audit"
    assert result["tasks"] == list(TASK_NAMES)
    assert result["failed_runs"] == []
    assert len(result["aggregate_table"]) == 3 * len(TASK_NAMES)
    assert result["decision"]["decision"] in {
        "STANDARD_INPUT_CUE_COPY_SOLVES_RETRIEVAL_REVIEW_REQUIRED",
        "STANDARD_INPUT_CUE_COPY_PARTIAL_RETRIEVAL",
        "STANDARD_INPUT_CUE_COPY_RETRIEVAL_FAILED",
    }


def test_stage56_outputs_are_written(tmp_path) -> None:
    result = run_stage56_audit(
        seeds=(307,),
        examples_per_length=1,
        method_names=METHOD_NAMES[:2],
        position_scales=(0.0, 1.0),
        cue_scales=(0.0, 4.0),
        distance_scales=(0.0, 4.0),
    )
    paths = write_stage56_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    assert set(paths) == {"manifest", "result", "summary_csv", "per_run_csv", "failed_runs"}
    assert manifest["stage"] == "stage56_standard_input_cue_copy_audit"
    assert manifest["decision"] == result["decision"]
    assert saved["aggregate_table"] == result["aggregate_table"]
