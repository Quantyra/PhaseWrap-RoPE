from __future__ import annotations

import json

from qrope.stage10_small_decoder_transformer import (
    METHOD_NAMES,
    TASK_NAMES,
    build_blocked_result,
    make_stage10_splits,
    positional_bias,
    run_stage10_ablation,
    run_stage10_preflight,
    write_stage10_outputs,
)


def test_stage10_blocked_result_is_machine_readable() -> None:
    result = build_blocked_result()
    assert result["stage"] == "stage10_small_decoder_transformer"
    assert result["status"] == "blocked"
    assert result["no_hardware_submission"] is True
    assert result["provider_credentials_required"] is False
    assert result["method_names"] == list(METHOD_NAMES)
    assert "proof that PhaseWrap-RoPE replaces RoPE" in result["claim_boundary"]["excluded"]


def test_stage10_preflight_reports_completed_or_blocked() -> None:
    result = run_stage10_preflight()
    assert result["status"] in {"completed", "blocked"}
    assert result["method_names"] == list(METHOD_NAMES)


def test_stage10_splits_and_biases_are_deterministic() -> None:
    first = make_stage10_splits(seeds=(307,), examples_per_length=1)
    second = make_stage10_splits(seeds=(307,), examples_per_length=1)
    assert first == second
    row = first["exact_offset_passkey"]["test"][0]
    assert row.reference_delta == row.target_delta
    qa_row = first["tiny_text_fact_qa"]["test"][0]
    assert qa_row.reference_delta == qa_row.target_delta
    assert qa_row.label_token in qa_row.tokens
    for method_name in METHOD_NAMES:
        assert positional_bias(row, method_name).shape == (row.query_pos,)


def test_stage10_ablation_smoke_run() -> None:
    result = run_stage10_ablation(seeds=(307,), examples_per_length=1, epochs=2)
    assert result["status"] == "completed"
    assert result["tasks"] == list(TASK_NAMES)
    assert result["failed_runs"] == []
    assert len(result["aggregate_table"]) == len(METHOD_NAMES) * len(TASK_NAMES)
    assert "test_expected_calibration_error_mean" in result["aggregate_table"][0]
    assert "test_target_probability_mae_mean" in result["aggregate_table"][0]
    assert "test_mean_top1_confidence_mean" in result["aggregate_table"][0]
    assert set(result["best_method_by_task"]) == set(TASK_NAMES)


def test_stage10_outputs_are_written(tmp_path) -> None:
    result = run_stage10_ablation(seeds=(307,), examples_per_length=1, epochs=2)
    paths = write_stage10_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    assert set(paths) == {"manifest", "result", "summary_csv", "per_seed_csv", "failed_runs"}
    assert manifest["stage"] == "stage10_small_decoder_transformer"
    assert manifest["status"] == "completed"
    assert saved["aggregate_table"] == result["aggregate_table"]
    assert (tmp_path / "summary.csv").exists()
    assert (tmp_path / "per_seed_results.csv").exists()
