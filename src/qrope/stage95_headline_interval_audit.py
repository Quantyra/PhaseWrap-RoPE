from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .stage45_matched_decoder_only_gate import METHOD_NAMES
from .stage52_two_block_decoder_feasibility_audit import GENERALIZATION_TOP1_THRESHOLD


STAGE95_SCHEMA_VERSION = "qrope_stage95_headline_interval_audit_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage95_headline_interval_audit"
ORIGINAL_RETRIEVAL_TASKS = ("phase_cued_retrieval", "exact_offset_passkey")

HEADLINE_SPECS: tuple[dict[str, str], ...] = (
    {
        "headline": "structural_phase_cued_solve",
        "stage_dir": "stage88_structural_retrieval_routed_copy_expert_audit",
        "task": "phase_cued_retrieval",
        "method": "rope_relative",
        "lane": "structural_copy_route",
    },
    {
        "headline": "structural_exact_offset_solve",
        "stage_dir": "stage88_structural_retrieval_routed_copy_expert_audit",
        "task": "exact_offset_passkey",
        "method": "rope_relative",
        "lane": "structural_copy_route",
    },
    {
        "headline": "free_learned_best_phase_cued",
        "stage_dir": "stage85_dual_auxiliary_pointer_generator_audit",
        "task": "phase_cued_retrieval",
        "method": "sinusoidal",
        "lane": "free_learned_pointer_generator",
    },
    {
        "headline": "free_learned_best_exact_offset",
        "stage_dir": "stage90_three_block_teacher_distilled_pointer_generator_audit",
        "task": "exact_offset_passkey",
        "method": "sinusoidal",
        "lane": "free_learned_pointer_generator",
    },
    {
        "headline": "recent_support_binding_phase_cued",
        "stage_dir": "stage92_support_binding_teacher_pointer_generator_audit",
        "task": "phase_cued_retrieval",
        "method": "alibi",
        "lane": "free_learned_pointer_generator",
    },
    {
        "headline": "recent_support_binding_exact_offset",
        "stage_dir": "stage92_support_binding_teacher_pointer_generator_audit",
        "task": "exact_offset_passkey",
        "method": "sinusoidal",
        "lane": "free_learned_pointer_generator",
    },
)

SOURCE_STAGE_DIRS: tuple[str, ...] = tuple(sorted({spec["stage_dir"] for spec in HEADLINE_SPECS})) + (
    "stage93_toy_decoder_lane_boundary_audit",
)


def _claim_boundary() -> dict[str, list[str]]:
    return {
        "supported": [
            "A no-credential interval extraction audit for current headline structural and free learned retrieval evidence.",
            "Seed-interval preservation for positive structural row-family solvability and negative free learned retrieval results.",
            "A narrowed promotion-gate gap showing interval reporting exists while PhaseWrap-led free learned retrieval evidence remains missing.",
        ],
        "excluded": [
            "a claim that PhaseWrap-RoPE replaces RoPE",
            "a claim that interval reporting creates a PhaseWrap-led retrieval solve",
            "a claim that structural copy experts are standard free decoder-only language modeling",
            "production transformer superiority",
            "full transformer-scale validation",
            "broad quantum advantage",
        ],
    }


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _source_artifacts(artifact_root: Path) -> tuple[list[str], list[str]]:
    artifacts: list[str] = []
    missing: list[str] = []
    for stage_dir in SOURCE_STAGE_DIRS:
        for file_name in ("manifest.json", "summary.csv"):
            path = artifact_root / stage_dir / file_name
            artifacts.append(str(path.as_posix()))
            if not path.exists():
                missing.append(str(path.as_posix()))
    stage93_results = artifact_root / "stage93_toy_decoder_lane_boundary_audit" / "results.json"
    artifacts.append(str(stage93_results.as_posix()))
    if not stage93_results.exists():
        missing.append(str(stage93_results.as_posix()))
    return artifacts, missing


def _read_summary_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _float(row: dict[str, str], key: str) -> float | None:
    value = row.get(key)
    if value in (None, ""):
        return None
    return float(value)


def _metric_interval(row: dict[str, str], prefix: str) -> dict[str, float | None]:
    return {
        "mean": _float(row, f"{prefix}_mean"),
        "ci_low": _float(row, f"{prefix}_ci_low"),
        "ci_high": _float(row, f"{prefix}_ci_high"),
    }


def _find_headline_row(artifact_root: Path, spec: dict[str, str]) -> dict[str, Any]:
    summary_path = artifact_root / spec["stage_dir"] / "summary.csv"
    if not summary_path.exists():
        return {
            **spec,
            "status": "missing",
            "missing_path": str(summary_path.as_posix()),
        }
    rows = _read_summary_rows(summary_path)
    row = next((item for item in rows if item.get("task") == spec["task"] and item.get("method") == spec["method"]), None)
    if row is None:
        return {
            **spec,
            "status": "missing",
            "missing_row": {"task": spec["task"], "method": spec["method"]},
        }
    intervals = {
        "test_top1_accuracy": _metric_interval(row, "test_top1_accuracy"),
        "test_mrr": _metric_interval(row, "test_mrr"),
        "test_mean_target_probability": _metric_interval(row, "test_mean_target_probability"),
        "test_expected_calibration_error": _metric_interval(row, "test_expected_calibration_error"),
    }
    return {
        **spec,
        "status": "present",
        "seed_count": int(float(row.get("seed_count", 0))),
        "failed_run_count": int(float(row.get("failed_run_count", 0))),
        "intervals": intervals,
        "top1_crosses_generalization_threshold": (
            intervals["test_top1_accuracy"]["mean"] is not None
            and intervals["test_top1_accuracy"]["mean"] >= GENERALIZATION_TOP1_THRESHOLD
        ),
    }


def _stage93_boundary(artifact_root: Path) -> dict[str, Any] | None:
    return _load_json(artifact_root / "stage93_toy_decoder_lane_boundary_audit" / "results.json")


def _decision(headline_rows: list[dict[str, Any]], stage93: dict[str, Any] | None, missing_source_artifacts: list[str]) -> dict[str, Any]:
    missing_rows = [row for row in headline_rows if row["status"] != "present"]
    interval_coverage = not missing_rows and not missing_source_artifacts
    free_rows = [row for row in headline_rows if row["status"] == "present" and row["lane"] == "free_learned_pointer_generator"]
    free_full_solve = all(
        any(row["task"] == task and row["top1_crosses_generalization_threshold"] for row in free_rows)
        for task in ORIGINAL_RETRIEVAL_TASKS
    )
    stage93_promotion = bool(stage93 and stage93.get("decision", {}).get("phasewrap_free_learned_promotion_supported") is True)
    if interval_coverage and not free_full_solve and not stage93_promotion:
        decision = "HEADLINE_INTERVALS_ADDED_PROMOTION_STILL_BOUND"
        boundary = "Headline seed intervals are now surfaced, but free learned retrieval still does not support PhaseWrap promotion."
    elif interval_coverage and stage93_promotion:
        decision = "HEADLINE_INTERVALS_ADDED_PROMOTION_REVIEW_REQUIRED"
        boundary = "Headline seed intervals are surfaced and Stage93 indicates PhaseWrap-led free learned retrieval; review before claim update."
    else:
        decision = "HEADLINE_INTERVAL_AUDIT_INCOMPLETE"
        boundary = "The interval audit could not surface every selected headline interval."
    return {
        "decision": decision,
        "claim_boundary": boundary,
        "generalization_top1_threshold": GENERALIZATION_TOP1_THRESHOLD,
        "confidence_interval_coverage": interval_coverage,
        "free_learned_full_retrieval_solved_by_headlines": free_full_solve,
        "phasewrap_free_learned_promotion_supported": stage93_promotion,
        "missing_headline_rows": [
            {key: row[key] for key in ("headline", "stage_dir", "task", "method")}
            for row in missing_rows
        ],
        "missing_source_artifact_count": len(missing_source_artifacts),
    }


def run_stage95_audit(*, artifact_root: Path = DEFAULT_ARTIFACT_ROOT, method_names: tuple[str, ...] = METHOD_NAMES) -> dict[str, Any]:
    source_artifacts, missing_source_artifacts = _source_artifacts(artifact_root)
    headline_rows = [_find_headline_row(artifact_root, spec) for spec in HEADLINE_SPECS]
    stage93 = _stage93_boundary(artifact_root)
    result = {
        "schema_version": STAGE95_SCHEMA_VERSION,
        "stage": "stage95_headline_interval_audit",
        "status": "completed",
        "source_stage": "stage93_toy_decoder_lane_boundary_audit",
        "source_artifacts": source_artifacts,
        "missing_source_artifacts": missing_source_artifacts,
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "method_names": list(method_names),
        "tasks": list(ORIGINAL_RETRIEVAL_TASKS),
        "claim_boundary": _claim_boundary(),
        "headline_rows": headline_rows,
        "stage93_decision": stage93.get("decision", {}) if stage93 else None,
        "strongest_claim_effect": (
            "Stage95 removes interval reporting as a current artifact gap for selected headlines, "
            "but preserves the stronger blocker: no free learned PhaseWrap-led original-retrieval solve."
        ),
        "reviewer_next_gate": (
            "Use these surfaced intervals when reporting the bounded claim; the next model gate must still produce "
            "free learned PhaseWrap-led retrieval evidence before promotion can be reconsidered."
        ),
    }
    result["decision"] = _decision(headline_rows, stage93, missing_source_artifacts)
    return result


def write_stage95_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "source_stage": result["source_stage"],
        "source_artifacts": result["source_artifacts"],
        "no_hardware_submission": result["no_hardware_submission"],
        "provider_credentials_required": result["provider_credentials_required"],
        "method_names": result["method_names"],
        "tasks": result["tasks"],
        "result_path": str((output_dir / "results.json").as_posix()),
        "summary_csv_path": str((output_dir / "summary.csv").as_posix()),
        "decision": result["decision"],
        "claim_boundary": result["claim_boundary"],
        "strongest_claim_effect": result["strongest_claim_effect"],
        "reviewer_next_gate": result["reviewer_next_gate"],
        "missing_source_artifacts": result["missing_source_artifacts"],
    }
    paths = {
        "manifest": str(output_dir / "manifest.json"),
        "result": str(output_dir / "results.json"),
        "summary_csv": str(output_dir / "summary.csv"),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=(
                "headline",
                "lane",
                "stage_dir",
                "task",
                "method",
                "status",
                "seed_count",
                "failed_run_count",
                "test_top1_accuracy_mean",
                "test_top1_accuracy_ci_low",
                "test_top1_accuracy_ci_high",
                "test_mrr_mean",
                "test_mean_target_probability_mean",
                "test_expected_calibration_error_mean",
            ),
        )
        writer.writeheader()
        for row in result["headline_rows"]:
            intervals = row.get("intervals", {})
            writer.writerow(
                {
                    "headline": row["headline"],
                    "lane": row["lane"],
                    "stage_dir": row["stage_dir"],
                    "task": row["task"],
                    "method": row["method"],
                    "status": row["status"],
                    "seed_count": row.get("seed_count"),
                    "failed_run_count": row.get("failed_run_count"),
                    "test_top1_accuracy_mean": intervals.get("test_top1_accuracy", {}).get("mean"),
                    "test_top1_accuracy_ci_low": intervals.get("test_top1_accuracy", {}).get("ci_low"),
                    "test_top1_accuracy_ci_high": intervals.get("test_top1_accuracy", {}).get("ci_high"),
                    "test_mrr_mean": intervals.get("test_mrr", {}).get("mean"),
                    "test_mean_target_probability_mean": intervals.get("test_mean_target_probability", {}).get("mean"),
                    "test_expected_calibration_error_mean": intervals.get("test_expected_calibration_error", {}).get("mean"),
                }
            )
    return paths


def print_stage95_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']['decision']}")
    print(f"claim_boundary: {result['decision']['claim_boundary']}")
    print(f"confidence_interval_coverage: {result['decision']['confidence_interval_coverage']}")
