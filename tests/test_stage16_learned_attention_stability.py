from __future__ import annotations

import json

from qrope.stage14_attention_readout import make_stage14_examples, split_examples
from qrope.stage16_learned_attention_stability import (
    METHOD_NAMES,
    run_stage16_benchmark,
    train_with_init_seed,
    write_stage16_outputs,
)


def test_train_with_init_seed_is_deterministic() -> None:
    rows = make_stage14_examples(seeds=(401,), context_lengths=(128, 256), examples_per_task_length=1)
    train_rows = split_examples(rows)["train"]
    first = train_with_init_seed(train_rows, "phasewrap_distance_adapter", 1009, epochs=4)
    second = train_with_init_seed(train_rows, "phasewrap_distance_adapter", 1009, epochs=4)
    assert first["params"] == second["params"]
    assert first["training_history"] == second["training_history"]


def test_run_stage16_benchmark_is_complete() -> None:
    result = run_stage16_benchmark(
        seeds=(401,),
        context_lengths=(128, 256, 512, 1024),
        examples_per_task_length=1,
        init_seeds=(1009, 1013),
        epochs=4,
    )
    assert result["stage"] == "stage16_learned_attention_stability"
    assert result["no_hardware_submission"] is True
    assert [row["method"] for row in result["aggregate_table"]] == list(METHOD_NAMES)
    assert result["best_method_by_mean_top1_mrr"] in METHOD_NAMES
    assert len(result["per_run_table"]) == len(METHOD_NAMES) * 2
    assert "a claim that PhaseWrap-RoPE is a validated RoPE replacement" in result["claim_boundary"]["excluded"]


def test_stage16_outputs_are_written(tmp_path) -> None:
    result = run_stage16_benchmark(
        seeds=(401,),
        context_lengths=(128, 256, 512, 1024),
        examples_per_task_length=1,
        init_seeds=(1009, 1013),
        epochs=4,
    )
    paths = write_stage16_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    assert set(paths) == {"manifest", "results", "summary_csv", "per_run_csv"}
    assert manifest["stage"] == "stage16_learned_attention_stability"
    assert saved["aggregate_table"] == result["aggregate_table"]
    assert (tmp_path / "summary.csv").exists()
    assert (tmp_path / "per_run_results.csv").exists()
