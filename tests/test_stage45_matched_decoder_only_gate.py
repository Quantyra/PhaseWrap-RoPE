from __future__ import annotations

import json

from qrope.stage45_matched_decoder_only_gate import (
    METHOD_NAMES,
    TASK_NAMES,
    build_blocked_result,
    run_stage45_gate,
    write_stage45_outputs,
)


def test_stage45_blocked_result_is_machine_readable() -> None:
    result = build_blocked_result()
    assert result["stage"] == "stage45_matched_decoder_only_gate"
    assert result["status"] == "blocked"
    assert result["no_hardware_submission"] is True
    assert result["provider_credentials_required"] is False
    assert result["method_names"] == list(METHOD_NAMES)
    assert "a claim that PhaseWrap-RoPE replaces RoPE" in result["claim_boundary"]["excluded"]


def test_stage45_smoke_gate_reports_all_tasks_and_methods() -> None:
    result = run_stage45_gate(seeds=(307,), examples_per_length=1, epochs=2)
    assert result["status"] == "completed"
    assert result["tasks"] == list(TASK_NAMES)
    assert result["method_names"] == list(METHOD_NAMES)
    assert result["failed_runs"] == []
    assert len(result["aggregate_table"]) == len(METHOD_NAMES) * len(TASK_NAMES)
    assert result["gate_decision"]["decision"] in {
        "PROMOTION_NOT_SUPPORTED",
        "PROMOTION_CANDIDATE_REQUIRES_REPLICATION",
    }
    assert result["gate_decision"]["best_method_by_task"].keys() == set(TASK_NAMES)


def test_stage45_outputs_are_written(tmp_path) -> None:
    result = run_stage45_gate(seeds=(307,), examples_per_length=1, epochs=2)
    paths = write_stage45_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    assert set(paths) == {"manifest", "result", "summary_csv", "per_seed_csv", "failed_runs"}
    assert manifest["stage"] == "stage45_matched_decoder_only_gate"
    assert manifest["gate_decision"] == result["gate_decision"]
    assert saved["aggregate_table"] == result["aggregate_table"]
    assert (tmp_path / "summary.csv").exists()
    assert (tmp_path / "per_seed_results.csv").exists()
