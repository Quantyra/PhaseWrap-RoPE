from __future__ import annotations

import json

from qrope.stage25_long_context_value_stability import run_stage25_benchmark, write_stage25_outputs


def test_run_stage25_benchmark_is_complete() -> None:
    result = run_stage25_benchmark(
        seeds=(401,),
        context_lengths=(512, 1024, 2048, 4096),
        examples_per_task_length=1,
        init_seeds=(2401, 2411),
        epochs=3,
        method_names=("rope_relative", "phasewrap_residual_adapter"),
        embed_dim=4,
    )
    assert result["stage"] == "stage25_long_context_value_stability"
    assert result["source_stage"] == "stage24_long_context_value_model"
    assert result["run_count"] == 2
    assert result["best_method_by_mean_top1_mrr"] in {"rope_relative", "phasewrap_residual_adapter"}
    assert {row["method"] for row in result["summary_table"]} == {"rope_relative", "phasewrap_residual_adapter"}
    assert len(result["per_run_table"]) == 4
    assert "a claim that PhaseWrap-RoPE is a validated RoPE replacement" in result["claim_boundary"]["excluded"]


def test_stage25_outputs_are_written(tmp_path) -> None:
    result = run_stage25_benchmark(
        seeds=(401,),
        context_lengths=(512, 1024, 2048, 4096),
        examples_per_task_length=1,
        init_seeds=(2401, 2411),
        epochs=3,
        method_names=("rope_relative", "phasewrap_residual_adapter"),
        embed_dim=4,
    )
    paths = write_stage25_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    weak_runs = json.loads((tmp_path / "weak_run_records.json").read_text(encoding="utf-8"))
    assert set(paths) == {"manifest", "results", "summary_csv", "per_run_csv", "weak_run_records"}
    assert manifest["stage"] == "stage25_long_context_value_stability"
    assert saved["summary_table"] == result["summary_table"]
    assert weak_runs == result["weak_run_records"]
