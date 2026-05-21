from __future__ import annotations

import json

import numpy as np

from qrope.stage14_attention_readout import make_stage14_examples
from qrope.stage40_sequence_length_curriculum import prepare_sequence_rows, split_by_curriculum_lengths
from qrope.stage43_generator_hardened_pointer_sequence import (
    evaluate_generator_hardened_pointer_sequence,
    run_stage43_benchmark,
    train_generator_hardened_pointer_sequence,
    write_stage43_outputs,
)


def test_stage43_training_is_deterministic() -> None:
    rows = make_stage14_examples(seeds=(401,), context_lengths=(128, 256, 512, 1024, 2048), examples_per_task_length=1)
    splits = split_by_curriculum_lengths(rows)
    prepared = prepare_sequence_rows(splits["train"], "rope_relative")
    first = train_generator_hardened_pointer_sequence(prepared, "rope_relative", model_seed=4307, epochs=3, hidden_dim=8, value_embed_dim=12)
    second = train_generator_hardened_pointer_sequence(prepared, "rope_relative", model_seed=4307, epochs=3, hidden_dim=8, value_embed_dim=12)
    assert first["param_sha256"] == second["param_sha256"]
    assert first["value_output_mode"] == "generator_hardened_pointer_generator_copy_vocab_mixture"
    assert first["generator_loss_weight"] == 0.35


def test_stage43_evaluation_reports_generator_branch_metrics() -> None:
    rows = make_stage14_examples(seeds=(401,), context_lengths=(128, 256, 512, 1024, 2048), examples_per_task_length=1)
    splits = split_by_curriculum_lengths(rows)
    prepared = prepare_sequence_rows(splits["train"], "phasewrap_multiscale_adapter")
    training = train_generator_hardened_pointer_sequence(prepared, "phasewrap_multiscale_adapter", model_seed=4307, epochs=3, hidden_dim=8, value_embed_dim=12)
    params = {key: np.array(value, dtype=float) for key, value in training["params"].items()}
    metrics = evaluate_generator_hardened_pointer_sequence(prepared[:2], params)
    assert 0.0 <= metrics["mean_copy_gate"] <= 1.0
    assert 0.0 <= metrics["mean_generator_target_probability"] <= 1.0
    assert "generator_top1_accuracy" in metrics
    assert "mean_generator_first_relevant_value_rank" in metrics


def test_stage43_benchmark_and_outputs(tmp_path) -> None:
    result = run_stage43_benchmark(
        data_seeds=(401,),
        model_seeds=(4307, 4319),
        context_lengths=(128, 256, 512, 1024, 2048),
        examples_per_task_length=1,
        epochs=4,
        hidden_dim=8,
        value_embed_dim=12,
        method_names=("rope_relative", "phasewrap_multiscale_adapter"),
    )
    assert result["stage"] == "stage43_generator_hardened_pointer_sequence"
    assert result["train_lengths"] == [128, 256, 512]
    assert result["validation_lengths"] == [1024]
    assert result["test_lengths"] == [2048]
    assert result["model"]["value_output_mode"] == "generator-hardened pointer-generator mixture of copied prefix-token mass and learned vocab distribution"
    assert result["model"]["generator_loss_weight"] == 0.35
    assert result["train_row_count"] == 9
    assert result["validation_row_count"] == 3
    assert result["test_row_count"] == 3
    assert len(result["run_table"]) == 4
    assert len(result["task_table"]) == 12
    assert "generator_top1_accuracy_mean" in result["table"][0]
    assert "mean_generator_target_probability_mean" in result["table"][0]
    assert "a claim that PhaseWrap-RoPE is a validated RoPE replacement" in result["claim_boundary"]["excluded"]

    paths = write_stage43_outputs(result, tmp_path)
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
    assert manifest["stage"] == "stage43_generator_hardened_pointer_sequence"
    assert saved["generator_selection_table"] == result["generator_selection_table"]
