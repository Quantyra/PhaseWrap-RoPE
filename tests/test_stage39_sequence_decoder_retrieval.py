from __future__ import annotations

import json

import numpy as np

from qrope.stage14_attention_readout import make_stage14_examples
from qrope.stage39_sequence_decoder_retrieval import (
    FEATURE_DIM,
    run_stage39_benchmark,
    sequence_decoder_features,
    sequence_tokens,
    write_stage39_outputs,
)


def test_stage39_sequence_features_cover_full_prefix() -> None:
    row = make_stage14_examples(seeds=(401,), context_lengths=(128,), examples_per_task_length=1)[0]
    tokens = sequence_tokens(row)
    features = sequence_decoder_features(row, "phasewrap_multiscale_adapter")
    assert tokens.shape == (row.query_pos,)
    assert features.shape == (row.query_pos, FEATURE_DIM)
    assert np.all(np.isfinite(features))
    for position, token_id in zip(row.key_positions, row.candidate_values):
        assert int(tokens[position]) == token_id


def test_stage39_benchmark_and_outputs(tmp_path) -> None:
    result = run_stage39_benchmark(
        data_seeds=(401,),
        model_seeds=(3907, 3911),
        context_lengths=(128, 256, 512, 1024),
        examples_per_task_length=1,
        epochs=4,
        hidden_dim=8,
        value_embed_dim=8,
        method_names=("rope_relative", "phasewrap_multiscale_adapter"),
    )
    assert result["stage"] == "stage39_sequence_decoder_retrieval"
    assert result["train_row_count"] == 6
    assert result["test_row_count"] == 3
    assert result["model"]["attention_scope"] == "all prefix sequence tokens compete"
    assert len(result["run_table"]) == 4
    assert len(result["train_table"]) == 4
    assert len(result["validation_table"]) == 4
    assert len(result["task_table"]) == 12
    assert "expected_calibration_error_mean" in result["table"][0]
    assert "a claim that PhaseWrap-RoPE is a validated RoPE replacement" in result["claim_boundary"]["excluded"]

    paths = write_stage39_outputs(result, tmp_path)
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
    assert manifest["stage"] == "stage39_sequence_decoder_retrieval"
    assert saved["selection_table"] == result["selection_table"]
