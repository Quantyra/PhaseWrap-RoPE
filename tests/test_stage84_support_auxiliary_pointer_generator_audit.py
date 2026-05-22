from __future__ import annotations

import json

from qrope.stage10_small_decoder_transformer import TASK_NAMES
from qrope.stage45_matched_decoder_only_gate import METHOD_NAMES
from qrope.stage84_support_auxiliary_pointer_generator_audit import (
    build_blocked_result,
    run_stage84_audit,
    write_stage84_outputs,
)


def test_stage84_blocked_result_is_machine_readable() -> None:
    result = build_blocked_result()
    assert result["stage"] == "stage84_support_auxiliary_pointer_generator_audit"
    assert result["status"] == "blocked"
    assert result["method_names"] == list(METHOD_NAMES)
    assert result["tasks"] == list(TASK_NAMES)
    assert result["training_tasks"] == list(TASK_NAMES)


def test_stage84_smoke_reports_multitask_decision_or_blocked() -> None:
    result = run_stage84_audit(
        seeds=(307,),
        examples_per_length=6,
        epochs=2,
        method_names=("no_position", "rope_relative"),
    )
    assert result["stage"] == "stage84_support_auxiliary_pointer_generator_audit"
    if result["status"] == "blocked":
        assert result["blocked_reason"] == "missing_optional_autograd_dependency"
        return
    assert result["status"] == "completed"
    assert result["tasks"] == list(TASK_NAMES)
    assert result["training_tasks"] == list(TASK_NAMES)
    assert result["failed_runs"] == []
    assert result["decision"]["decision"] in {
        "SUPPORT_AUXILIARY_POINTER_GENERATOR_CAPACITY_NOT_ESTABLISHED",
        "SUPPORT_AUXILIARY_POINTER_GENERATOR_RETRIEVAL_REVIEW_REQUIRED",
        "SUPPORT_AUXILIARY_POINTER_GENERATOR_PARTIAL_RETRIEVAL",
        "SUPPORT_AUXILIARY_POINTER_GENERATOR_WITHOUT_RETRIEVAL_GENERALIZATION",
    }
    assert result["source_stage"] == "stage83_nonlinear_support_routing_bridge_audit"
    assert result["support_coverage"]["307"]["test_known_fraction"] == 1.0
    assert result["model"]["type"] == "two_block_pointer_generator_support_auxiliary_decoder"
    first_run = result["run_table"][0]
    assert first_run["training_tasks"] == list(TASK_NAMES)
    assert first_run["support_aux_weight"] == result["support_aux_weight"]
    assert first_run["multitask_train_row_count"] > first_run["task_train_row_count"]


def test_stage84_outputs_are_written(tmp_path) -> None:
    result = run_stage84_audit(
        seeds=(307,),
        examples_per_length=1,
        epochs=2,
        method_names=("no_position",),
    )
    paths = write_stage84_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved_name = "results.json" if result["status"] == "completed" else "preflight.json"
    saved = json.loads((tmp_path / saved_name).read_text(encoding="utf-8"))
    assert set(paths) >= {"manifest", "result", "summary_csv"}
    assert manifest["stage"] == "stage84_support_auxiliary_pointer_generator_audit"
    assert saved["stage"] == "stage84_support_auxiliary_pointer_generator_audit"
