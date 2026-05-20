from __future__ import annotations

import json

from qrope.stage26_compact_kv_qa import make_stage26_examples, run_stage26_benchmark, split_examples, write_stage26_outputs


def test_make_stage26_examples_are_deterministic() -> None:
    first = make_stage26_examples(seeds=(2601,), context_lengths=(256, 512, 1024, 2048), examples_per_length=1)
    second = make_stage26_examples(seeds=(2601,), context_lengths=(256, 512, 1024, 2048), examples_per_length=1)
    assert first == second
    splits = split_examples(first)
    assert len(splits["train"]) == 2
    assert len(splits["validation"]) == 1
    assert len(splits["test"]) == 1
    assert all(row.candidate_keys[row.target_index] == row.query_key for row in first)


def test_run_stage26_benchmark_is_complete() -> None:
    result = run_stage26_benchmark(
        seeds=(2601,),
        context_lengths=(256, 512, 1024, 2048),
        examples_per_length=1,
        epochs=4,
        method_names=("alibi", "phasewrap_residual_adapter"),
    )
    assert result["stage"] == "stage26_compact_kv_qa"
    assert result["train_row_count"] == 2
    assert result["validation_row_count"] == 1
    assert result["test_row_count"] == 1
    assert {row["split"] for row in result["table"]} == {"train", "validation", "test"}
    assert result["best_method_by_test_top1_mrr"] in {"alibi", "phasewrap_residual_adapter"}
    assert "a claim that PhaseWrap-RoPE is a validated RoPE replacement" in result["claim_boundary"]["excluded"]


def test_stage26_outputs_are_written(tmp_path) -> None:
    result = run_stage26_benchmark(
        seeds=(2601,),
        context_lengths=(256, 512, 1024, 2048),
        examples_per_length=1,
        epochs=4,
        method_names=("alibi", "phasewrap_residual_adapter"),
    )
    paths = write_stage26_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    weak_runs = json.loads((tmp_path / "weak_runs.json").read_text(encoding="utf-8"))
    assert set(paths) == {"manifest", "results", "summary_csv", "weak_runs"}
    assert manifest["stage"] == "stage26_compact_kv_qa"
    assert saved["table"] == result["table"]
    assert weak_runs == result["weak_runs"]
