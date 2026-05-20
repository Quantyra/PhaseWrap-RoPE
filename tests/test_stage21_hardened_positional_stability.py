from __future__ import annotations

import json

from qrope.stage21_hardened_positional_stability import run_stage21_benchmark, write_stage21_outputs


def test_run_stage21_benchmark_is_complete() -> None:
    result = run_stage21_benchmark(
        seeds=(401,),
        init_seeds=(2001, 2011),
        context_lengths=(128, 256, 512, 1024),
        examples_per_task_length=1,
        epochs=4,
        method_names=("rope_relative", "phasewrap_distance_adapter"),
    )
    assert result["stage"] == "stage21_hardened_positional_stability"
    assert result["source_stage"] == "stage20_hardened_positional_value_model"
    assert result["run_count"] == 2
    assert {row["method"] for row in result["summary_table"]} == {"rope_relative", "phasewrap_distance_adapter"}
    assert len(result["per_run_table"]) == 4
    assert result["best_method_by_mean_top1_mrr"] in {"rope_relative", "phasewrap_distance_adapter"}
    assert "a claim that PhaseWrap-RoPE is a validated RoPE replacement" in result["claim_boundary"]["excluded"]


def test_stage21_outputs_are_written(tmp_path) -> None:
    result = run_stage21_benchmark(
        seeds=(401,),
        init_seeds=(2001, 2011),
        context_lengths=(128, 256, 512, 1024),
        examples_per_task_length=1,
        epochs=4,
        method_names=("rope_relative", "phasewrap_distance_adapter"),
    )
    paths = write_stage21_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    assert set(paths) == {"manifest", "results", "summary_csv", "per_run_csv"}
    assert manifest["stage"] == "stage21_hardened_positional_stability"
    assert saved["summary_table"] == result["summary_table"]
