from __future__ import annotations

import json

from qrope.stage45_matched_decoder_only_gate import METHOD_NAMES
from qrope.stage60_support_fallback_strictness_audit import TASK_NAMES, build_blocked_result, run_stage60_audit, write_stage60_outputs


def test_stage60_blocked_result_is_machine_readable() -> None:
    result = build_blocked_result()
    assert result["stage"] == "stage60_support_fallback_strictness_audit"
    assert result["status"] == "blocked"
    assert result["no_hardware_submission"] is True
    assert result["provider_credentials_required"] is False
    assert result["method_names"] == list(METHOD_NAMES)
    assert "a claim that fallback decoding is a matched decoder-only transformer" in result["claim_boundary"]["excluded"]


def test_stage60_smoke_reports_fallback_strictness_decision() -> None:
    result = run_stage60_audit(
        seeds=(307, 311),
        examples_per_length=1,
        method_names=("rope_relative", "phasewrap_bias", "no_position"),
        position_scales=(0.0, 1.0),
        cue_scales=(0.0, 4.0),
        distance_scales=(0.0, 4.0),
    )
    assert result["status"] == "completed"
    assert result["stage"] == "stage60_support_fallback_strictness_audit"
    assert result["tasks"] == list(TASK_NAMES)
    assert result["failed_runs"] == []
    assert result["support_policies"] == ["fallback_mod16", "strict_known_only"]
    assert len(result["aggregate_table"]) == 2 * 3 * len(TASK_NAMES)
    assert set(result["learned_query_support_maps_by_seed"]) == {"307", "311"}
    assert "phase_cued_support_coverage" in result
    assert result["decision"]["decision"] in {
        "FALLBACK_DEPENDENT_PHASE_CUED_RETRIEVAL_NOT_PROMOTION",
        "STRICT_SUPPORT_STILL_SOLVES_NOT_PROMOTION",
        "SUPPORT_STRICTNESS_RETRIEVAL_FAILED",
    }


def test_stage60_outputs_are_written(tmp_path) -> None:
    result = run_stage60_audit(
        seeds=(307, 311),
        examples_per_length=1,
        method_names=METHOD_NAMES[:2],
        position_scales=(0.0, 1.0),
        cue_scales=(0.0, 4.0),
        distance_scales=(0.0, 4.0),
    )
    paths = write_stage60_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    assert set(paths) == {"manifest", "result", "summary_csv", "per_run_csv", "failed_runs"}
    assert manifest["stage"] == "stage60_support_fallback_strictness_audit"
    assert manifest["decision"] == result["decision"]
    assert saved["aggregate_table"] == result["aggregate_table"]
