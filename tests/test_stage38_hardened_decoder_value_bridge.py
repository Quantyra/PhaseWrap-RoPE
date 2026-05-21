from __future__ import annotations

import json

from qrope.stage38_hardened_decoder_value_bridge import run_stage38_benchmark, write_stage38_outputs


def test_stage38_benchmark_and_outputs(tmp_path) -> None:
    result = run_stage38_benchmark(
        data_seeds=(401,),
        model_seeds=(3803, 3821),
        context_lengths=(128, 256, 512, 1024),
        examples_per_task_length=1,
        epochs=4,
        hidden_dim=8,
        value_embed_dim=8,
        method_names=("rope_relative", "phasewrap_multiscale_adapter"),
    )
    assert result["stage"] == "stage38_hardened_decoder_value_bridge"
    assert result["train_row_count"] == 6
    assert result["test_row_count"] == 3
    assert result["model"]["optimizer"] == "full_batch_adam"
    assert result["model"]["hidden_dim"] == 8
    assert result["model"]["value_embed_dim"] == 8
    assert len(result["run_table"]) == 4
    assert len(result["train_table"]) == 4
    assert len(result["validation_table"]) == 4
    assert len(result["task_table"]) == 12
    assert "expected_calibration_error_mean" in result["table"][0]
    assert "a claim that PhaseWrap-RoPE is a validated RoPE replacement" in result["claim_boundary"]["excluded"]

    paths = write_stage38_outputs(result, tmp_path)
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
    assert manifest["stage"] == "stage38_hardened_decoder_value_bridge"
    assert saved["selection_table"] == result["selection_table"]
