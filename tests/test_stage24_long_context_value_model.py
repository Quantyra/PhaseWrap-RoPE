from __future__ import annotations

import json

from qrope.stage13_positional_adapter import METHOD_NAMES
from qrope.stage14_attention_readout import make_stage14_examples
from qrope.stage24_long_context_value_model import (
    run_stage24_benchmark,
    split_long_context_value_rows,
    write_stage24_outputs,
)


def test_split_long_context_value_rows() -> None:
    rows = make_stage14_examples(seeds=(401,), context_lengths=(512, 1024, 2048, 4096), examples_per_task_length=1)
    splits = split_long_context_value_rows(rows)
    assert len(splits["train"]) == 6
    assert len(splits["validation"]) == 3
    assert len(splits["test"]) == 3


def test_run_stage24_benchmark_is_complete() -> None:
    result = run_stage24_benchmark(
        seeds=(401,),
        context_lengths=(512, 1024, 2048, 4096),
        examples_per_task_length=1,
        epochs=3,
        method_names=("rope_relative", "phasewrap_distance_adapter"),
        embed_dim=4,
    )
    assert result["stage"] == "stage24_long_context_value_model"
    assert result["source_stage"] == "stage22_long_context_retrieval"
    assert result["train_row_count"] == 6
    assert result["validation_row_count"] == 3
    assert result["test_row_count"] == 3
    assert {row["split"] for row in result["table"]} == {"train", "validation", "test"}
    assert result["method_names"] == ["rope_relative", "phasewrap_distance_adapter"]
    assert result["best_method_by_test_top1_mrr"] in {"rope_relative", "phasewrap_distance_adapter"}
    assert "a claim that PhaseWrap-RoPE is a validated RoPE replacement" in result["claim_boundary"]["excluded"]


def test_stage24_outputs_are_written(tmp_path) -> None:
    result = run_stage24_benchmark(
        seeds=(401,),
        context_lengths=(512, 1024, 2048, 4096),
        examples_per_task_length=1,
        epochs=3,
        method_names=METHOD_NAMES[:2],
        embed_dim=4,
    )
    paths = write_stage24_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    assert set(paths) == {"manifest", "results", "summary_csv", "task_summary_csv"}
    assert manifest["stage"] == "stage24_long_context_value_model"
    assert saved["table"] == result["table"]
