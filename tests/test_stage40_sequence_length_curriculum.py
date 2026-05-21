from __future__ import annotations

import json

from qrope.stage14_attention_readout import make_stage14_examples
from qrope.stage40_sequence_length_curriculum import (
    prepare_sequence_rows,
    run_stage40_benchmark,
    split_by_curriculum_lengths,
    write_stage40_outputs,
)


def test_stage40_curriculum_split_and_prepare() -> None:
    rows = make_stage14_examples(seeds=(401,), context_lengths=(128, 256, 512, 1024, 2048), examples_per_task_length=1)
    splits = split_by_curriculum_lengths(rows)
    assert {row.sequence_length for row in splits["train"]} == {128, 256, 512}
    assert {row.sequence_length for row in splits["validation"]} == {1024}
    assert {row.sequence_length for row in splits["test"]} == {2048}
    prepared = prepare_sequence_rows(splits["train"][:1], "phasewrap_multiscale_adapter")
    assert prepared[0].features.shape[0] == prepared[0].row.query_pos
    assert prepared[0].token_ids.shape[0] == prepared[0].row.query_pos


def test_stage40_benchmark_and_outputs(tmp_path) -> None:
    result = run_stage40_benchmark(
        data_seeds=(401,),
        model_seeds=(4001, 4003),
        context_lengths=(128, 256, 512, 1024, 2048),
        examples_per_task_length=1,
        epochs=4,
        hidden_dim=8,
        value_embed_dim=8,
        method_names=("rope_relative", "phasewrap_multiscale_adapter"),
    )
    assert result["stage"] == "stage40_sequence_length_curriculum"
    assert result["train_lengths"] == [128, 256, 512]
    assert result["validation_lengths"] == [1024]
    assert result["test_lengths"] == [2048]
    assert result["train_row_count"] == 9
    assert result["validation_row_count"] == 3
    assert result["test_row_count"] == 3
    assert len(result["run_table"]) == 4
    assert len(result["task_table"]) == 12
    assert "curriculum" in result["model"]
    assert "a claim that PhaseWrap-RoPE is a validated RoPE replacement" in result["claim_boundary"]["excluded"]

    paths = write_stage40_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    assert set(paths) == {
        "manifest",
        "results",
        "summary_csv",
        "train_summary_csv",
        "validation_summary_csv",
        "per_run_csv",
        "task_summary_csv",
        "weak_runs",
    }
    assert manifest["stage"] == "stage40_sequence_length_curriculum"
    assert saved["selection_table"] == result["selection_table"]
