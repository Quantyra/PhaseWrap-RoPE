from __future__ import annotations

import json

from qrope.stage10_small_decoder_transformer import (
    METHOD_NAMES,
    build_blocked_result,
    run_stage10_preflight,
    write_stage10_outputs,
)


def test_stage10_blocked_result_is_machine_readable() -> None:
    result = build_blocked_result()
    assert result["stage"] == "stage10_small_decoder_transformer"
    assert result["status"] == "blocked"
    assert result["disk_free_bytes"] >= 0
    assert result["minimum_recommended_free_bytes_for_transformer_install"] > 0
    assert result["no_hardware_submission"] is True
    assert result["provider_credentials_required"] is False
    assert result["method_names"] == list(METHOD_NAMES)
    assert "proof that PhaseWrap-RoPE replaces RoPE" in result["claim_boundary"]["excluded"]


def test_stage10_preflight_reports_ready_or_blocked() -> None:
    result = run_stage10_preflight()
    assert result["status"] in {"ready", "blocked"}
    assert result["optional_dependency_group"] == "transformer"
    assert result["method_names"] == list(METHOD_NAMES)


def test_stage10_outputs_are_written(tmp_path) -> None:
    result = build_blocked_result()
    paths = write_stage10_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    preflight = json.loads((tmp_path / "preflight.json").read_text(encoding="utf-8"))
    assert set(paths) == {"manifest", "preflight", "summary_csv"}
    assert manifest["stage"] == "stage10_small_decoder_transformer"
    assert manifest["status"] == "blocked"
    assert preflight == result
    assert (tmp_path / "summary.csv").exists()
