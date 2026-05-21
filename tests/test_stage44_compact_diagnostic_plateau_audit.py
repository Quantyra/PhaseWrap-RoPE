from __future__ import annotations

import csv
import json
from pathlib import Path

from qrope.stage44_compact_diagnostic_plateau_audit import run_stage44_audit, write_stage44_outputs


def _write_summary(root: Path, stage_name: str, rows: list[dict[str, object]]) -> None:
    stage_dir = root / stage_name
    stage_dir.mkdir(parents=True)
    fieldnames = [
        "method",
        "run_count",
        "row_count",
        "parameter_count",
        "top1_accuracy_mean",
        "mrr_mean",
        "mean_target_value_probability_mean",
        "expected_calibration_error_mean",
    ]
    with (stage_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _rows(rope_top1: float, phase_top1: float) -> list[dict[str, object]]:
    return [
        {
            "method": "rope_relative",
            "run_count": 5,
            "row_count": 60,
            "parameter_count": 4635,
            "top1_accuracy_mean": rope_top1,
            "mrr_mean": rope_top1,
            "mean_target_value_probability_mean": rope_top1,
            "expected_calibration_error_mean": 0.02,
        },
        {
            "method": "phasewrap_multiscale_adapter",
            "run_count": 5,
            "row_count": 60,
            "parameter_count": 4635,
            "top1_accuracy_mean": phase_top1,
            "mrr_mean": phase_top1,
            "mean_target_value_probability_mean": phase_top1,
            "expected_calibration_error_mean": 0.05,
        },
    ]


def test_stage44_audit_declares_compact_plateau(tmp_path: Path) -> None:
    stage_names = (
        "stage39_sequence_decoder_retrieval",
        "stage40_sequence_length_curriculum",
        "stage41_pointer_copy_sequence",
        "stage42_trainable_pointer_generator_sequence",
        "stage43_generator_hardened_pointer_sequence",
    )
    for stage_name in stage_names:
        _write_summary(tmp_path, stage_name, _rows(rope_top1=1.0, phase_top1=0.97))

    result = run_stage44_audit(input_root=tmp_path)

    assert result["stage"] == "stage44_compact_diagnostic_plateau_audit"
    assert result["source_stages"] == list(stage_names)
    assert result["decision"]["decision"] == "BOUND_COMPACT_DIAGNOSTIC_PLATEAU"
    assert result["decision"]["final_stage_rope_strongest_on_ranking_and_probability"] is True
    assert "a claim that PhaseWrap-RoPE replaces RoPE" in result["claim_boundary"]["excluded"]


def test_stage44_outputs_are_written(tmp_path: Path) -> None:
    for stage_name in (
        "stage39_sequence_decoder_retrieval",
        "stage40_sequence_length_curriculum",
        "stage41_pointer_copy_sequence",
        "stage42_trainable_pointer_generator_sequence",
        "stage43_generator_hardened_pointer_sequence",
    ):
        _write_summary(tmp_path, stage_name, _rows(rope_top1=1.0, phase_top1=0.9))
    result = run_stage44_audit(input_root=tmp_path)

    output_dir = tmp_path / "out"
    paths = write_stage44_outputs(result, output_dir)

    assert set(paths) == {"manifest", "results", "summary_csv"}
    manifest = json.loads((output_dir / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((output_dir / "results.json").read_text(encoding="utf-8"))
    assert manifest["decision"]["decision"] == "BOUND_COMPACT_DIAGNOSTIC_PLATEAU"
    assert saved["stage_records"] == result["stage_records"]
    assert (output_dir / "summary.csv").exists()
