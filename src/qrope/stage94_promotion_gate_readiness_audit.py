from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .stage45_matched_decoder_only_gate import METHOD_NAMES
from .stage52_two_block_decoder_feasibility_audit import GENERALIZATION_TOP1_THRESHOLD


STAGE94_SCHEMA_VERSION = "qrope_stage94_promotion_gate_readiness_audit_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage94_promotion_gate_readiness_audit"
ORIGINAL_RETRIEVAL_TASKS = ("phase_cued_retrieval", "exact_offset_passkey")
NON_PHASE_LABELED_TASKS = ("content_key_retrieval", "tiny_text_fact_qa")

SOURCE_STAGE_DIRS: tuple[str, ...] = (
    "stage45_matched_decoder_only_gate",
    "stage48_adam_decoder_stability_audit",
    "stage67_content_key_retrieval_audit",
    "stage70_strongest_honest_claim_synthesis",
    "stage88_structural_retrieval_routed_copy_expert_audit",
    "stage89_structural_teacher_distilled_pointer_generator_audit",
    "stage90_three_block_teacher_distilled_pointer_generator_audit",
    "stage91_curriculum_teacher_distilled_pointer_generator_audit",
    "stage92_support_binding_teacher_pointer_generator_audit",
    "stage93_toy_decoder_lane_boundary_audit",
    "stage95_headline_interval_audit",
)


def _load_manifest(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _source_manifests(artifact_root: Path) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    source_artifacts: list[str] = []
    missing_source_artifacts: list[str] = []
    manifests: list[dict[str, Any]] = []
    for stage_dir in SOURCE_STAGE_DIRS:
        manifest_path = artifact_root / stage_dir / "manifest.json"
        source_artifacts.append(str(manifest_path.as_posix()))
        manifest = _load_manifest(manifest_path)
        if manifest is None:
            missing_source_artifacts.append(str(manifest_path.as_posix()))
            continue
        manifests.append(manifest)
    return manifests, source_artifacts, missing_source_artifacts


def _claim_boundary() -> dict[str, list[str]]:
    return {
        "supported": [
            "A no-credential audit of whether current artifacts satisfy the predeclared transformer promotion gate.",
            "A requirement-by-requirement readiness table preserving current positives and explicit missing proof.",
            "A next-gate boundary for stronger matched decoder-only transformer evidence before any RoPE-replacement claim.",
        ],
        "excluded": [
            "a claim that PhaseWrap-RoPE replaces RoPE",
            "a claim that PhaseWrap-RoPE is currently better than RoPE in fair matched transformer settings",
            "a claim that structural copy experts satisfy the free learned transformer gate",
            "production transformer superiority",
            "full transformer-scale validation",
            "broad quantum advantage",
        ],
    }


def _method_set(manifest: dict[str, Any]) -> set[str]:
    return set(str(method) for method in manifest.get("method_names", []))


def _retrieval_best_top1(manifest: dict[str, Any]) -> dict[str, float]:
    top1 = manifest.get("decision", {}).get("retrieval_best_top1", {})
    if not isinstance(top1, dict):
        return {}
    return {
        task: float(value)
        for task, value in top1.items()
        if task in ORIGINAL_RETRIEVAL_TASKS and isinstance(value, int | float)
    }


def _retrieval_best_methods(manifest: dict[str, Any]) -> dict[str, str]:
    methods = manifest.get("decision", {}).get("retrieval_best_methods", {})
    if not isinstance(methods, dict):
        return {}
    return {
        task: str(value)
        for task, value in methods.items()
        if task in ORIGINAL_RETRIEVAL_TASKS and isinstance(value, str)
    }


def _all_original_retrieval_solved(manifest: dict[str, Any]) -> bool:
    top1 = _retrieval_best_top1(manifest)
    return all(top1.get(task, 0.0) >= GENERALIZATION_TOP1_THRESHOLD for task in ORIGINAL_RETRIEVAL_TASKS)


def _phasewrap_led_original_retrieval_solve(manifest: dict[str, Any]) -> bool:
    if not _all_original_retrieval_solved(manifest):
        return False
    methods = _retrieval_best_methods(manifest)
    return all(methods.get(task, "").startswith("phasewrap") for task in ORIGINAL_RETRIEVAL_TASKS)


def _has_failed_run_retention(manifest: dict[str, Any]) -> bool:
    return "failed_runs_path" in manifest or "failed_runs" in manifest or "failed_run_count" in manifest


def _has_confidence_intervals(manifest: dict[str, Any]) -> bool:
    text = json.dumps(manifest.get("decision", {}), sort_keys=True)
    return "confidence_interval" in text or "ci95" in text or "bootstrap_interval" in text


def _non_phase_labeled_successes(manifests: list[dict[str, Any]]) -> list[dict[str, Any]]:
    successes: list[dict[str, Any]] = []
    for manifest in manifests:
        tasks = set(manifest.get("tasks", []))
        decision = manifest.get("decision", {})
        for task in NON_PHASE_LABELED_TASKS:
            if task not in tasks:
                continue
            top1 = None
            if task == "content_key_retrieval":
                value = decision.get("retrieval_best_top1", {}).get(task) if isinstance(decision.get("retrieval_best_top1"), dict) else None
                if isinstance(value, int | float):
                    top1 = float(value)
            elif task == "tiny_text_fact_qa" and isinstance(decision.get("tiny_text_best_top1"), int | float):
                top1 = float(decision["tiny_text_best_top1"])
            if top1 is not None and top1 >= GENERALIZATION_TOP1_THRESHOLD:
                successes.append(
                    {
                        "stage": manifest.get("stage"),
                        "task": task,
                        "top1": top1,
                        "decision": decision.get("decision"),
                    }
                )
    return successes


def _requirement_rows(manifests: list[dict[str, Any]], missing_source_artifacts: list[str]) -> list[dict[str, Any]]:
    required_methods = set(METHOD_NAMES)
    matched_method_stages = [
        manifest.get("stage")
        for manifest in manifests
        if required_methods.issubset(_method_set(manifest))
    ]
    phasewrap_solve_stages = [
        manifest.get("stage")
        for manifest in manifests
        if _phasewrap_led_original_retrieval_solve(manifest)
    ]
    structural_solve_stages = [
        manifest.get("stage")
        for manifest in manifests
        if manifest.get("stage") == "stage88_structural_retrieval_routed_copy_expert_audit" and _all_original_retrieval_solved(manifest)
    ]
    non_phase_successes = _non_phase_labeled_successes(manifests)
    failed_run_retention_stages = [
        manifest.get("stage")
        for manifest in manifests
        if _has_failed_run_retention(manifest)
    ]
    confidence_interval_stages = [
        manifest.get("stage")
        for manifest in manifests
        if _has_confidence_intervals(manifest)
    ]
    stage93 = next((manifest for manifest in manifests if manifest.get("stage") == "stage93_toy_decoder_lane_boundary_audit"), None)
    stage93_bounded = bool(stage93 and stage93.get("decision", {}).get("free_learned_full_retrieval_solved") is False)
    return [
        {
            "requirement": "source_artifacts_present",
            "status": "passed" if not missing_source_artifacts else "failed",
            "evidence": "All selected source manifests are present." if not missing_source_artifacts else "One or more selected source manifests are missing.",
            "source_stages": [],
        },
        {
            "requirement": "fair_method_set_present",
            "status": "passed" if matched_method_stages else "failed",
            "evidence": "At least one loaded artifact includes the full no-position/sinusoidal/ALiBI/RoPE/PhaseWrap method set.",
            "source_stages": matched_method_stages,
        },
        {
            "requirement": "non_phase_labeled_task_included",
            "status": "passed" if non_phase_successes else "failed",
            "evidence": "Current artifacts include non-phase-labeled task successes, but these are diagnostic unless PhaseWrap leads under a fair free learned transformer gate.",
            "source_stages": [row["stage"] for row in non_phase_successes],
            "supporting_rows": non_phase_successes,
        },
        {
            "requirement": "free_learned_phasewrap_original_retrieval_solve",
            "status": "failed" if not phasewrap_solve_stages else "passed",
            "evidence": "No current free learned artifact solves both original retrieval tasks with PhaseWrap-led methods.",
            "source_stages": phasewrap_solve_stages,
        },
        {
            "requirement": "structural_solve_not_overread",
            "status": "passed" if structural_solve_stages and stage93_bounded else "failed",
            "evidence": "Structural row-family solves are preserved as positive evidence but excluded from promotion-readiness.",
            "source_stages": structural_solve_stages + (["stage93_toy_decoder_lane_boundary_audit"] if stage93_bounded else []),
        },
        {
            "requirement": "failed_run_retention",
            "status": "passed" if failed_run_retention_stages else "failed",
            "evidence": "Selected training artifacts retain failed-run fields or paths.",
            "source_stages": failed_run_retention_stages,
        },
        {
            "requirement": "confidence_intervals_over_seeds",
            "status": "failed" if not confidence_interval_stages else "passed",
            "evidence": (
                "Selected manifests expose confidence interval coverage for headline metrics."
                if confidence_interval_stages
                else "No selected manifest exposes confidence intervals for headline promotion metrics."
            ),
            "source_stages": confidence_interval_stages,
        },
    ]


def _decision(requirement_rows: list[dict[str, Any]]) -> dict[str, Any]:
    failed = [row for row in requirement_rows if row["status"] != "passed"]
    phasewrap_solve = next(row for row in requirement_rows if row["requirement"] == "free_learned_phasewrap_original_retrieval_solve")
    ci = next(row for row in requirement_rows if row["requirement"] == "confidence_intervals_over_seeds")
    if not failed:
        decision = "PROMOTION_GATE_READY_FOR_REVIEW"
        boundary = "All selected promotion-gate requirements are satisfied; review before updating claims."
    elif phasewrap_solve["status"] == "failed":
        decision = "PROMOTION_GATE_NOT_READY_STRONGEST_CLAIM_BOUNDED"
        boundary = "Current evidence still lacks a free learned PhaseWrap-led solve of both original retrieval tasks, so the strongest claim remains bounded."
    elif ci["status"] == "failed":
        decision = "PROMOTION_GATE_NOT_READY_MISSING_INTERVALS"
        boundary = "Current evidence has a candidate solve but lacks confidence intervals required for promotion readiness."
    else:
        decision = "PROMOTION_GATE_NOT_READY_INCOMPLETE_REQUIREMENTS"
        boundary = "Current evidence is missing one or more predeclared promotion-gate requirements."
    return {
        "decision": decision,
        "claim_boundary": boundary,
        "generalization_top1_threshold": GENERALIZATION_TOP1_THRESHOLD,
        "promotion_gate_ready": not failed,
        "failed_requirements": [row["requirement"] for row in failed],
    }


def run_stage94_audit(*, artifact_root: Path = DEFAULT_ARTIFACT_ROOT, method_names: tuple[str, ...] = METHOD_NAMES) -> dict[str, Any]:
    manifests, source_artifacts, missing_source_artifacts = _source_manifests(artifact_root)
    requirement_rows = _requirement_rows(manifests, missing_source_artifacts)
    result = {
        "schema_version": STAGE94_SCHEMA_VERSION,
        "stage": "stage94_promotion_gate_readiness_audit",
        "status": "completed",
        "source_stage": "stage95_headline_interval_audit",
        "source_artifacts": source_artifacts,
        "missing_source_artifacts": missing_source_artifacts,
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "method_names": list(method_names),
        "tasks": list(ORIGINAL_RETRIEVAL_TASKS) + list(NON_PHASE_LABELED_TASKS),
        "claim_boundary": _claim_boundary(),
        "requirement_rows": requirement_rows,
        "strongest_claim_effect": (
            "Stage 94 confirms that the current strongest honest claim remains bounded until a free learned matched transformer "
            "or materially stronger decoder gate satisfies the PhaseWrap-led retrieval requirement."
        ),
        "reviewer_next_gate": (
            "Implement a stronger matched decoder-only transformer benchmark with retained failed runs and confidence intervals; "
            "require a free learned PhaseWrap-led solve or competitive non-phase-labeled benchmark result before reopening promotion claims."
        ),
    }
    result["decision"] = _decision(requirement_rows)
    return result


def write_stage94_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
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
        writer = csv.DictWriter(handle, fieldnames=("requirement", "status", "evidence", "source_stages"))
        writer.writeheader()
        for row in result["requirement_rows"]:
            writer.writerow(
                {
                    "requirement": row["requirement"],
                    "status": row["status"],
                    "evidence": row["evidence"],
                    "source_stages": json.dumps(row.get("source_stages", []), sort_keys=True),
                }
            )
    return paths


def print_stage94_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']['decision']}")
    print(f"claim_boundary: {result['decision']['claim_boundary']}")
    print(f"failed_requirements: {', '.join(result['decision']['failed_requirements'])}")
