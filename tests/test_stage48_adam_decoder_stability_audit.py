from __future__ import annotations

import json

from qrope.stage48_adam_decoder_stability_audit import (
    METHOD_NAMES,
    TASK_NAMES,
    build_blocked_result,
    run_stage48_audit,
    write_stage48_outputs,
)


def test_stage48_blocked_result_is_machine_readable() -> None:
    result = build_blocked_result()
    assert result["stage"] == "stage48_adam_decoder_stability_audit"
    assert result["status"] == "blocked"
    assert result["no_hardware_submission"] is True
    assert result["provider_credentials_required"] is False
    assert result["method_names"] == list(METHOD_NAMES)
    assert "a claim that PhaseWrap-RoPE replaces RoPE" in result["claim_boundary"]["excluded"]


def test_stage48_smoke_reports_stability_decision() -> None:
    result = run_stage48_audit(seeds=(307,), examples_per_length=1, epochs=2)
    assert result["status"] == "completed"
    assert result["tasks"] == list(TASK_NAMES)
    assert result["method_names"] == list(METHOD_NAMES)
    assert result["failed_runs"] == []
    assert len(result["aggregate_table"]) == len(METHOD_NAMES) * len(TASK_NAMES)
    assert result["decision"]["decision"] in {
        "PHASEWRAP_TINY_QA_STABLE_RETRIEVAL_FAILED",
        "TINY_QA_POSITIVE_NOT_PHASEWRAP_STABLE_RETRIEVAL_FAILED",
        "RETRIEVAL_GENERALIZATION_PRESENT_REVIEW_REQUIRED",
    }
    assert "tiny_text_best_method" in result["decision"]
    assert "retrieval_generalizes" in result["decision"]


def test_stage48_outputs_are_written(tmp_path) -> None:
    result = run_stage48_audit(seeds=(307,), examples_per_length=1, epochs=2)
    paths = write_stage48_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    assert set(paths) == {"manifest", "result", "summary_csv", "per_run_csv", "failed_runs"}
    assert manifest["stage"] == "stage48_adam_decoder_stability_audit"
    assert manifest["decision"] == result["decision"]
    assert saved["aggregate_table"] == result["aggregate_table"]
    assert (tmp_path / "summary.csv").exists()
    assert (tmp_path / "per_run_results.csv").exists()
