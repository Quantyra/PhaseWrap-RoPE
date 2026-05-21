from __future__ import annotations

import json

from qrope.stage46_decoder_capacity_hardening_audit import (
    METHOD_NAMES,
    TASK_NAMES,
    build_blocked_result,
    run_stage46_audit,
    write_stage46_outputs,
)


def test_stage46_blocked_result_is_machine_readable() -> None:
    result = build_blocked_result()
    assert result["stage"] == "stage46_decoder_capacity_hardening_audit"
    assert result["status"] == "blocked"
    assert result["no_hardware_submission"] is True
    assert result["provider_credentials_required"] is False
    assert result["method_names"] == list(METHOD_NAMES)
    assert "a claim that PhaseWrap-RoPE replaces RoPE" in result["claim_boundary"]["excluded"]


def test_stage46_smoke_audit_reports_capacity_decision() -> None:
    result = run_stage46_audit(seeds=(307,), examples_per_length=1, epochs=2)
    assert result["status"] == "completed"
    assert result["tasks"] == list(TASK_NAMES)
    assert result["method_names"] == list(METHOD_NAMES)
    assert result["failed_runs"] == []
    assert len(result["aggregate_table"]) == len(METHOD_NAMES) * len(TASK_NAMES)
    assert result["decision"]["decision"] in {
        "CAPACITY_NOT_ESTABLISHED",
        "TRAIN_FIT_WITHOUT_GENERALIZATION",
        "CAPACITY_GATE_READY_FOR_POSITIONAL_COMPARISON",
    }
    assert "train_top1_accuracy_mean" in result["aggregate_table"][0]
    assert "test_top1_accuracy_mean" in result["aggregate_table"][0]


def test_stage46_outputs_are_written(tmp_path) -> None:
    result = run_stage46_audit(seeds=(307,), examples_per_length=1, epochs=2)
    paths = write_stage46_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    assert set(paths) == {"manifest", "result", "summary_csv", "per_run_csv", "failed_runs"}
    assert manifest["stage"] == "stage46_decoder_capacity_hardening_audit"
    assert manifest["decision"] == result["decision"]
    assert saved["aggregate_table"] == result["aggregate_table"]
    assert (tmp_path / "summary.csv").exists()
    assert (tmp_path / "per_run_results.csv").exists()
