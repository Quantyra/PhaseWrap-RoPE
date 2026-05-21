from __future__ import annotations

import json

from qrope.stage14_attention_readout import make_stage14_examples
from qrope.stage40_sequence_length_curriculum import split_by_curriculum_lengths
from qrope.stage41_pointer_copy_sequence import prepare_pointer_rows, run_stage41_benchmark, write_stage41_outputs


def test_stage41_prepare_pointer_rows_marks_targets() -> None:
    rows = make_stage14_examples(seeds=(401,), context_lengths=(128, 256, 512, 1024, 2048), examples_per_task_length=1)
    splits = split_by_curriculum_lengths(rows)
    prepared = prepare_pointer_rows(splits["train"][:1], "phasewrap_multiscale_adapter")[0]
    assert prepared.features.shape[0] == prepared.row.query_pos
    assert prepared.token_ids.shape[0] == prepared.row.query_pos
    assert float(prepared.target_token_indicator.sum()) >= 1.0


def test_stage41_benchmark_and_outputs(tmp_path) -> None:
    result = run_stage41_benchmark(
        data_seeds=(401,),
        model_seeds=(4103, 4111),
        context_lengths=(128, 256, 512, 1024, 2048),
        examples_per_task_length=1,
        epochs=4,
        hidden_dim=8,
        method_names=("rope_relative", "phasewrap_multiscale_adapter"),
    )
    assert result["stage"] == "stage41_pointer_copy_sequence"
    assert result["train_lengths"] == [128, 256, 512]
    assert result["validation_lengths"] == [1024]
    assert result["test_lengths"] == [2048]
    assert result["model"]["value_output_mode"] == "copy attention mass to observed prefix token ids"
    assert result["train_row_count"] == 9
    assert result["validation_row_count"] == 3
    assert result["test_row_count"] == 3
    assert len(result["run_table"]) == 4
    assert len(result["task_table"]) == 12
    assert "mean_target_attention_probability_mean" in result["table"][0]
    assert "a claim that PhaseWrap-RoPE is a validated RoPE replacement" in result["claim_boundary"]["excluded"]

    paths = write_stage41_outputs(result, tmp_path)
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
    assert manifest["stage"] == "stage41_pointer_copy_sequence"
    assert saved["selection_table"] == result["selection_table"]
