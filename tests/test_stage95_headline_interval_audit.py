from __future__ import annotations

import csv
import json
from pathlib import Path

from qrope.stage45_matched_decoder_only_gate import METHOD_NAMES
from qrope.stage95_headline_interval_audit import run_stage95_audit, write_stage95_outputs


def _write_manifest(root: Path, stage_dir: str, payload: dict[str, object] | None = None) -> None:
    directory = root / stage_dir
    directory.mkdir(parents=True, exist_ok=True)
    manifest = {
        "stage": stage_dir,
        "status": "completed",
        "method_names": list(METHOD_NAMES),
        "tasks": ["phase_cued_retrieval", "exact_offset_passkey", "tiny_text_fact_qa"],
        **(payload or {}),
    }
    (directory / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")


def _write_summary(root: Path, stage_dir: str, rows: list[dict[str, object]]) -> None:
    directory = root / stage_dir
    directory.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "task",
        "method",
        "seed_count",
        "failed_run_count",
        "test_top1_accuracy_mean",
        "test_top1_accuracy_ci_low",
        "test_top1_accuracy_ci_high",
        "test_mrr_mean",
        "test_mrr_ci_low",
        "test_mrr_ci_high",
        "test_mean_target_probability_mean",
        "test_mean_target_probability_ci_low",
        "test_mean_target_probability_ci_high",
        "test_expected_calibration_error_mean",
        "test_expected_calibration_error_ci_low",
        "test_expected_calibration_error_ci_high",
    ]
    with (directory / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _row(task: str, method: str, top1: float) -> dict[str, object]:
    return {
        "task": task,
        "method": method,
        "seed_count": 5,
        "failed_run_count": 0,
        "test_top1_accuracy_mean": top1,
        "test_top1_accuracy_ci_low": max(0.0, top1 - 0.05),
        "test_top1_accuracy_ci_high": min(1.0, top1 + 0.05),
        "test_mrr_mean": top1,
        "test_mrr_ci_low": max(0.0, top1 - 0.04),
        "test_mrr_ci_high": min(1.0, top1 + 0.04),
        "test_mean_target_probability_mean": 0.2,
        "test_mean_target_probability_ci_low": 0.18,
        "test_mean_target_probability_ci_high": 0.22,
        "test_expected_calibration_error_mean": 0.1,
        "test_expected_calibration_error_ci_low": 0.08,
        "test_expected_calibration_error_ci_high": 0.12,
    }


def _write_all_required_inputs(root: Path) -> None:
    stage_rows = {
        "stage88_structural_retrieval_routed_copy_expert_audit": [
            _row("phase_cued_retrieval", "rope_relative", 0.783333),
            _row("exact_offset_passkey", "rope_relative", 1.0),
        ],
        "stage85_dual_auxiliary_pointer_generator_audit": [
            _row("phase_cued_retrieval", "sinusoidal", 0.05),
        ],
        "stage90_three_block_teacher_distilled_pointer_generator_audit": [
            _row("exact_offset_passkey", "sinusoidal", 0.433333),
        ],
        "stage92_support_binding_teacher_pointer_generator_audit": [
            _row("phase_cued_retrieval", "alibi", 0.05),
            _row("exact_offset_passkey", "sinusoidal", 0.366667),
        ],
        "stage93_toy_decoder_lane_boundary_audit": [],
    }
    for stage_dir, rows in stage_rows.items():
        _write_manifest(root, stage_dir)
        _write_summary(root, stage_dir, rows)
    (root / "stage93_toy_decoder_lane_boundary_audit" / "results.json").write_text(
        json.dumps(
            {
                "decision": {
                    "phasewrap_free_learned_promotion_supported": False,
                    "free_learned_full_retrieval_solved": False,
                }
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def test_stage95_surfaces_headline_intervals_without_promotion(tmp_path) -> None:
    _write_all_required_inputs(tmp_path)

    result = run_stage95_audit(artifact_root=tmp_path)

    assert result["stage"] == "stage95_headline_interval_audit"
    assert result["status"] == "completed"
    assert result["decision"]["decision"] == "HEADLINE_INTERVALS_ADDED_PROMOTION_STILL_BOUND"
    assert result["decision"]["confidence_interval_coverage"] is True
    assert result["decision"]["free_learned_full_retrieval_solved_by_headlines"] is False
    assert len(result["headline_rows"]) == 6
    phase_row = next(row for row in result["headline_rows"] if row["headline"] == "structural_phase_cued_solve")
    assert phase_row["intervals"]["test_top1_accuracy"]["mean"] == 0.783333
    assert phase_row["seed_count"] == 5


def test_stage95_reports_missing_headline_rows(tmp_path) -> None:
    _write_manifest(tmp_path, "stage88_structural_retrieval_routed_copy_expert_audit")
    _write_summary(tmp_path, "stage88_structural_retrieval_routed_copy_expert_audit", [])

    result = run_stage95_audit(artifact_root=tmp_path)

    assert result["decision"]["decision"] == "HEADLINE_INTERVAL_AUDIT_INCOMPLETE"
    assert result["decision"]["confidence_interval_coverage"] is False
    assert result["decision"]["missing_headline_rows"]


def test_stage95_outputs_are_written(tmp_path) -> None:
    _write_all_required_inputs(tmp_path)
    result = run_stage95_audit(artifact_root=tmp_path)
    paths = write_stage95_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((tmp_path / "out" / "results.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert manifest["stage"] == "stage95_headline_interval_audit"
    assert saved["strongest_claim_effect"] == result["strongest_claim_effect"]
    assert "structural_phase_cued_solve" in summary
