from __future__ import annotations

import json

from qrope.stage22_long_context_retrieval import run_stage22_benchmark, write_stage22_outputs


def test_run_stage22_benchmark_is_complete() -> None:
    result = run_stage22_benchmark(seeds=(401,), context_lengths=(128, 256), examples_per_task_length=1)
    assert result["stage"] == "stage22_long_context_retrieval"
    assert result["source_stage"] == "stage12_ruler_retrieval"
    assert result["no_hardware_submission"] is True
    assert result["row_count"] == 6
    assert {row["sequence_length"] for row in result["length_table"]} == {128, 256}
    assert result["best_method_by_top1_mrr"] in set(result["method_names"])
    assert "a claim that PhaseWrap-RoPE is a validated RoPE replacement" in result["claim_boundary"]["excluded"]


def test_stage22_outputs_are_written(tmp_path) -> None:
    result = run_stage22_benchmark(seeds=(401,), context_lengths=(128, 256), examples_per_task_length=1)
    paths = write_stage22_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    assert set(paths) == {"manifest", "results", "summary_csv", "task_summary_csv", "length_summary_csv", "per_example_csv"}
    assert manifest["stage"] == "stage22_long_context_retrieval"
    assert "per_example_rows" not in saved
    assert (tmp_path / "per_example_results.csv").exists()
