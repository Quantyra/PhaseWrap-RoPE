from __future__ import annotations

import json

from qrope.stage45_matched_decoder_only_gate import METHOD_NAMES
from qrope.stage49_copy_decoder_retrieval_repair_audit import (
    TASK_NAMES,
    evaluate_copy_decoder,
    run_stage49_audit,
    select_position_scale,
    write_stage49_outputs,
)
from qrope.stage10_small_decoder_transformer import make_stage10_splits


def test_stage49_copy_decoder_evaluates_stage10_rows() -> None:
    splits = make_stage10_splits(seeds=(307,), examples_per_length=1)
    rows = [row for row in splits["exact_offset_passkey"]["validation"] if row.seed == 307]
    selection = select_position_scale(rows, "rope_relative", candidate_scales=(0.0, 1.0, 4.0))
    metrics = evaluate_copy_decoder(rows, "rope_relative", selection["selected_position_scale"])
    assert selection["selected_position_scale"] in {0.0, 1.0, 4.0}
    assert metrics["row_count"] == 1.0
    assert 0.0 <= metrics["top1_accuracy"] <= 1.0
    assert 0.0 <= metrics["mean_target_probability"] <= 1.0


def test_stage49_audit_reports_retrieval_repair_decision() -> None:
    result = run_stage49_audit(
        seeds=(307,),
        examples_per_length=1,
        method_names=("rope_relative", "phasewrap_bias", "no_position"),
        candidate_scales=(0.0, 2.0, 8.0),
    )
    assert result["stage"] == "stage49_copy_decoder_retrieval_repair_audit"
    assert result["status"] == "completed"
    assert result["tasks"] == list(TASK_NAMES)
    assert result["failed_runs"] == []
    assert len(result["aggregate_table"]) == 3 * len(TASK_NAMES)
    assert result["decision"]["decision"] in {
        "COPY_DECODER_REPAIRS_RETRIEVAL_REVIEW_METHOD_ORDERING",
        "COPY_DECODER_PARTIALLY_REPAIRS_RETRIEVAL",
        "COPY_DECODER_RETRIEVAL_REPAIR_FAILED",
    }
    assert "a claim that PhaseWrap-RoPE replaces RoPE" in result["claim_boundary"]["excluded"]


def test_stage49_outputs_are_written(tmp_path) -> None:
    result = run_stage49_audit(seeds=(307,), examples_per_length=1, method_names=METHOD_NAMES[:2], candidate_scales=(0.0, 1.0))
    paths = write_stage49_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    assert set(paths) == {"manifest", "result", "summary_csv", "per_run_csv", "failed_runs"}
    assert manifest["stage"] == "stage49_copy_decoder_retrieval_repair_audit"
    assert manifest["decision"] == result["decision"]
    assert saved["aggregate_table"] == result["aggregate_table"]
    assert (tmp_path / "summary.csv").exists()
    assert (tmp_path / "per_run_results.csv").exists()
