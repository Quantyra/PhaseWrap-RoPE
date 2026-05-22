from __future__ import annotations

import json

from qrope.stage45_matched_decoder_only_gate import METHOD_NAMES
from qrope.stage52_two_block_decoder_feasibility_audit import RETRIEVAL_TASKS
from qrope.stage86_dual_auxiliary_budget_sensitivity_audit import (
    build_blocked_result,
    run_stage86_audit,
    write_stage86_outputs,
)


def test_stage86_blocked_result_is_machine_readable() -> None:
    result = build_blocked_result()
    assert result["stage"] == "stage86_dual_auxiliary_budget_sensitivity_audit"
    assert result["status"] == "blocked"
    assert result["method_names"] == list(METHOD_NAMES)
    assert result["source_stage"] == "stage85_dual_auxiliary_pointer_generator_audit"


def test_stage86_smoke_reports_budget_sensitivity_or_blocked() -> None:
    result = run_stage86_audit(
        epoch_budgets=(1, 2),
        seeds=(307,),
        examples_per_length=1,
        method_names=("no_position", "sinusoidal"),
    )
    assert result["stage"] == "stage86_dual_auxiliary_budget_sensitivity_audit"
    if result["status"] == "blocked":
        assert result["blocked_reason"] == "missing_optional_autograd_dependency"
        return
    assert result["status"] == "completed"
    assert result["epoch_budgets"] == [1, 2]
    assert len(result["budget_summaries"]) == 2
    assert result["decision"]["decision"] in {
        "DUAL_AUXILIARY_BUDGET_CAPACITY_NOT_ESTABLISHED",
        "DUAL_AUXILIARY_BUDGET_RETRIEVAL_REVIEW_REQUIRED",
        "DUAL_AUXILIARY_BUDGET_PARTIAL_RETRIEVAL",
        "DUAL_AUXILIARY_BUDGET_WITHOUT_RETRIEVAL_GENERALIZATION",
    }
    first_summary = result["budget_summaries"][0]
    assert set(first_summary["retrieval_best_top1"]) == set(RETRIEVAL_TASKS)
    assert first_summary["failed_run_count"] == 0
    assert first_summary["aggregate_table"]


def test_stage86_outputs_are_written(tmp_path) -> None:
    result = run_stage86_audit(
        epoch_budgets=(1,),
        seeds=(307,),
        examples_per_length=1,
        method_names=("no_position",),
    )
    paths = write_stage86_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved_name = "results.json" if result["status"] == "completed" else "preflight.json"
    saved = json.loads((tmp_path / saved_name).read_text(encoding="utf-8"))
    summary = (tmp_path / "summary.csv").read_text(encoding="utf-8")
    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert manifest["stage"] == "stage86_dual_auxiliary_budget_sensitivity_audit"
    assert saved["stage"] == "stage86_dual_auxiliary_budget_sensitivity_audit"
    assert "best_top1" in summary
