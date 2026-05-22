from __future__ import annotations

import json

from qrope.stage10_small_decoder_transformer import TASK_NAMES
from qrope.stage45_matched_decoder_only_gate import METHOD_NAMES
from qrope.stage85_dual_auxiliary_pointer_generator_audit import (
    build_blocked_result,
    run_stage85_audit,
    write_stage85_outputs,
)


def test_stage85_blocked_result_is_machine_readable() -> None:
    result = build_blocked_result()
    assert result["stage"] == "stage85_dual_auxiliary_pointer_generator_audit"
    assert result["status"] == "blocked"
    assert result["method_names"] == list(METHOD_NAMES)
    assert result["tasks"] == list(TASK_NAMES)
    assert result["training_tasks"] == list(TASK_NAMES)


def test_stage85_smoke_reports_dual_auxiliary_decision_or_blocked() -> None:
    result = run_stage85_audit(
        seeds=(307,),
        examples_per_length=6,
        epochs=2,
        method_names=("no_position", "rope_relative"),
    )
    assert result["stage"] == "stage85_dual_auxiliary_pointer_generator_audit"
    if result["status"] == "blocked":
        assert result["blocked_reason"] == "missing_optional_autograd_dependency"
        return
    assert result["status"] == "completed"
    assert result["tasks"] == list(TASK_NAMES)
    assert result["training_tasks"] == list(TASK_NAMES)
    assert result["failed_runs"] == []
    assert result["decision"]["decision"] in {
        "DUAL_AUXILIARY_POINTER_GENERATOR_CAPACITY_NOT_ESTABLISHED",
        "DUAL_AUXILIARY_POINTER_GENERATOR_RETRIEVAL_REVIEW_REQUIRED",
        "DUAL_AUXILIARY_POINTER_GENERATOR_PARTIAL_RETRIEVAL",
        "DUAL_AUXILIARY_POINTER_GENERATOR_ATTENTION_REPAIRED_TOKEN_FAILED",
        "DUAL_AUXILIARY_POINTER_GENERATOR_WITHOUT_RETRIEVAL_GENERALIZATION",
    }
    assert result["source_stage"] == "stage84_support_auxiliary_pointer_generator_audit"
    assert result["support_coverage"]["307"]["test_known_fraction"] == 1.0
    assert result["model"]["type"] == "two_block_pointer_generator_dual_auxiliary_decoder"
    assert "target-position attention auxiliary loss" in result["model"]["target_attention_supervision_policy"]
    first_run = result["run_table"][0]
    assert first_run["training_tasks"] == list(TASK_NAMES)
    assert first_run["support_aux_weight"] == result["support_aux_weight"]
    assert first_run["target_attention_aux_weight"] == result["target_attention_aux_weight"]
    assert first_run["multitask_train_row_count"] > first_run["task_train_row_count"]
    assert "test_mean_target_attention" in first_run


def test_stage85_outputs_are_written(tmp_path) -> None:
    result = run_stage85_audit(
        seeds=(307,),
        examples_per_length=1,
        epochs=2,
        method_names=("no_position",),
    )
    paths = write_stage85_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved_name = "results.json" if result["status"] == "completed" else "preflight.json"
    saved = json.loads((tmp_path / saved_name).read_text(encoding="utf-8"))
    assert set(paths) >= {"manifest", "result", "summary_csv"}
    assert manifest["stage"] == "stage85_dual_auxiliary_pointer_generator_audit"
    assert saved["stage"] == "stage85_dual_auxiliary_pointer_generator_audit"
