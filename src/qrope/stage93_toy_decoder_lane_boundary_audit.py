from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .stage45_matched_decoder_only_gate import METHOD_NAMES
from .stage52_two_block_decoder_feasibility_audit import GENERALIZATION_TOP1_THRESHOLD


STAGE93_SCHEMA_VERSION = "qrope_stage93_toy_decoder_lane_boundary_audit_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage93_toy_decoder_lane_boundary_audit"
ORIGINAL_RETRIEVAL_TASKS = ("phase_cued_retrieval", "exact_offset_passkey")

STRUCTURAL_STAGE_DIRS: tuple[str, ...] = (
    "stage87_in_decoder_support_routed_copy_expert_audit",
    "stage88_structural_retrieval_routed_copy_expert_audit",
)

FREE_LEARNED_STAGE_DIRS: tuple[str, ...] = (
    "stage64_two_block_pointer_generator_capacity_audit",
    "stage65_pointer_generator_length_curriculum_audit",
    "stage68_content_key_auxiliary_transfer_audit",
    "stage69_original_multitask_pointer_generator_audit",
    "stage84_support_auxiliary_pointer_generator_audit",
    "stage85_dual_auxiliary_pointer_generator_audit",
    "stage86_dual_auxiliary_budget_sensitivity_audit",
    "stage89_structural_teacher_distilled_pointer_generator_audit",
    "stage90_three_block_teacher_distilled_pointer_generator_audit",
    "stage91_curriculum_teacher_distilled_pointer_generator_audit",
    "stage92_support_binding_teacher_pointer_generator_audit",
)

SOURCE_STAGE_DIRS: tuple[str, ...] = STRUCTURAL_STAGE_DIRS + FREE_LEARNED_STAGE_DIRS


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
            "A no-credential boundary audit over existing structural and free learned toy decoder evidence.",
            "Evidence that structural copy routes can solve the original retrieval row family while free learned toy pointer-generators have not internalized the route.",
            "A next-gate recommendation for moving beyond small pointer-generator variants before any positional-method promotion claim.",
        ],
        "excluded": [
            "a claim that PhaseWrap-RoPE replaces RoPE",
            "a claim that PhaseWrap-RoPE is currently better than RoPE in fair matched transformer settings",
            "a claim that structural copy experts are standard free decoder-only language modeling",
            "production transformer superiority",
            "full transformer-scale validation",
            "broad quantum advantage",
        ],
    }


def _has_original_retrieval_tasks(manifest: dict[str, Any]) -> bool:
    tasks = set(manifest.get("tasks", []))
    return all(task in tasks for task in ORIGINAL_RETRIEVAL_TASKS)


def _retrieval_best_top1(manifest: dict[str, Any]) -> dict[str, float]:
    decision = manifest.get("decision", {})
    top1 = decision.get("retrieval_best_top1", {})
    if not isinstance(top1, dict):
        return {}
    return {
        task: float(value)
        for task, value in top1.items()
        if task in ORIGINAL_RETRIEVAL_TASKS and isinstance(value, int | float)
    }


def _retrieval_best_methods(manifest: dict[str, Any]) -> dict[str, str]:
    decision = manifest.get("decision", {})
    methods = decision.get("retrieval_best_methods", {})
    if not isinstance(methods, dict):
        return {}
    return {
        task: value
        for task, value in methods.items()
        if task in ORIGINAL_RETRIEVAL_TASKS and isinstance(value, str)
    }


def _all_retrieval_solved(top1: dict[str, float]) -> bool:
    return all(top1.get(task, 0.0) >= GENERALIZATION_TOP1_THRESHOLD for task in ORIGINAL_RETRIEVAL_TASKS)


def _phasewrap_led(methods: dict[str, str]) -> bool:
    return all(methods.get(task, "").startswith("phasewrap") for task in ORIGINAL_RETRIEVAL_TASKS)


def _row_for_manifest(manifest: dict[str, Any], lane: str) -> dict[str, Any]:
    decision = manifest.get("decision", {})
    top1 = _retrieval_best_top1(manifest)
    methods = _retrieval_best_methods(manifest)
    return {
        "stage": manifest.get("stage"),
        "lane": lane,
        "decision": decision.get("decision"),
        "capacity_established": decision.get("capacity_established"),
        "retrieval_best_top1": top1,
        "retrieval_best_methods": methods,
        "retrieval_solved": _all_retrieval_solved(top1),
        "phasewrap_led": _phasewrap_led(methods),
        "tiny_text_best_top1": decision.get("tiny_text_best_top1"),
        "tiny_text_best_method": decision.get("tiny_text_best_method"),
    }


def _lane_rows(manifests: list[dict[str, Any]], stage_dirs: tuple[str, ...], lane: str) -> list[dict[str, Any]]:
    stages = set(stage_dirs)
    return [
        _row_for_manifest(manifest, lane)
        for manifest in manifests
        if manifest.get("stage") in stages and _has_original_retrieval_tasks(manifest)
    ]


def _best_free_learned_top1(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any] | None]:
    best: dict[str, dict[str, Any] | None] = {task: None for task in ORIGINAL_RETRIEVAL_TASKS}
    for task in ORIGINAL_RETRIEVAL_TASKS:
        for row in rows:
            value = row["retrieval_best_top1"].get(task)
            if not isinstance(value, int | float):
                continue
            candidate = {
                "stage": row["stage"],
                "method": row["retrieval_best_methods"].get(task),
                "top1": float(value),
            }
            current = best[task]
            if current is None or candidate["top1"] > current["top1"]:
                best[task] = candidate
    return best


def _decision(structural_rows: list[dict[str, Any]], free_rows: list[dict[str, Any]], missing_source_artifacts: list[str]) -> dict[str, Any]:
    structural_full_solve = any(row["retrieval_solved"] for row in structural_rows)
    free_full_solve_rows = [row for row in free_rows if row["retrieval_solved"]]
    phasewrap_free_solve_rows = [row for row in free_full_solve_rows if row["phasewrap_led"]]
    if phasewrap_free_solve_rows:
        decision = "TOY_DECODER_LANE_PROMOTION_REVIEW_REQUIRED"
        boundary = "At least one free learned toy decoder generalizes both original retrieval tasks with PhaseWrap-led methods; review before any claim update."
    elif free_full_solve_rows:
        decision = "TOY_DECODER_LANE_SOLVED_NOT_PROMOTION"
        boundary = "A free learned toy decoder generalizes both original retrieval tasks, but the result is not PhaseWrap-led and does not establish positional-method promotion."
    elif structural_full_solve and free_rows:
        decision = "TOY_DECODER_LANE_BOUND_FREE_RETRIEVAL_UNSOLVED"
        boundary = "Structural copy routes solve the row family, but current free learned toy pointer-generators do not generalize both original retrieval tasks."
    elif missing_source_artifacts:
        decision = "TOY_DECODER_LANE_BOUNDARY_INCOMPLETE_EVIDENCE"
        boundary = "The lane boundary could not be fully audited because source artifacts are missing."
    else:
        decision = "TOY_DECODER_LANE_BOUNDARY_NO_STRUCTURAL_SOLVE"
        boundary = "The audited artifacts do not yet show both a structural row-family solve and free learned retrieval failure."
    return {
        "decision": decision,
        "claim_boundary": boundary,
        "generalization_top1_threshold": GENERALIZATION_TOP1_THRESHOLD,
        "structural_retrieval_solved": structural_full_solve,
        "free_learned_full_retrieval_solved": bool(free_full_solve_rows),
        "phasewrap_free_learned_promotion_supported": bool(phasewrap_free_solve_rows),
        "free_learned_full_solve_stages": [row["stage"] for row in free_full_solve_rows],
        "phasewrap_free_learned_solve_stages": [row["stage"] for row in phasewrap_free_solve_rows],
        "missing_source_artifact_count": len(missing_source_artifacts),
    }


def run_stage93_audit(*, artifact_root: Path = DEFAULT_ARTIFACT_ROOT, method_names: tuple[str, ...] = METHOD_NAMES) -> dict[str, Any]:
    manifests, source_artifacts, missing_source_artifacts = _source_manifests(artifact_root)
    structural_rows = _lane_rows(manifests, STRUCTURAL_STAGE_DIRS, "structural_copy_route")
    free_rows = _lane_rows(manifests, FREE_LEARNED_STAGE_DIRS, "free_learned_pointer_generator")
    result = {
        "schema_version": STAGE93_SCHEMA_VERSION,
        "stage": "stage93_toy_decoder_lane_boundary_audit",
        "status": "completed",
        "source_stage": "stage92_support_binding_teacher_pointer_generator_audit",
        "source_artifacts": source_artifacts,
        "missing_source_artifacts": missing_source_artifacts,
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "method_names": list(method_names),
        "tasks": list(ORIGINAL_RETRIEVAL_TASKS),
        "structural_stage_dirs": list(STRUCTURAL_STAGE_DIRS),
        "free_learned_stage_dirs": list(FREE_LEARNED_STAGE_DIRS),
        "claim_boundary": _claim_boundary(),
        "structural_rows": structural_rows,
        "free_learned_rows": free_rows,
        "free_learned_best_top1_by_task": _best_free_learned_top1(free_rows),
        "lane_boundary": (
            "The current toy pointer-generator lane has useful capacity and diagnostic positives, "
            "but its free learned variants have not internalized the support-to-token route that structural experts can supply."
        ),
        "reviewer_next_gate": (
            "Move to a stronger matched decoder-only transformer implementation or a materially different learned binding mechanism; "
            "do not treat further small pointer-generator variants as RoPE-replacement evidence without free held-out retrieval improvement."
        ),
    }
    result["decision"] = _decision(structural_rows, free_rows, missing_source_artifacts)
    return result


def write_stage93_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
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
        "lane_boundary": result["lane_boundary"],
        "reviewer_next_gate": result["reviewer_next_gate"],
        "free_learned_best_top1_by_task": result["free_learned_best_top1_by_task"],
        "missing_source_artifacts": result["missing_source_artifacts"],
    }
    paths = {
        "manifest": str(output_dir / "manifest.json"),
        "result": str(output_dir / "results.json"),
        "summary_csv": str(output_dir / "summary.csv"),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    summary_rows = [
        {"section": "decision", "item": "decision", "value": result["decision"]["decision"]},
        {"section": "decision", "item": "claim_boundary", "value": result["decision"]["claim_boundary"]},
        {"section": "lane_boundary", "item": "boundary", "value": result["lane_boundary"]},
        {"section": "next_gate", "item": "reviewer_next_gate", "value": result["reviewer_next_gate"]},
    ]
    for row in result["structural_rows"] + result["free_learned_rows"]:
        summary_rows.append(
            {
                "section": row["lane"],
                "item": str(row["stage"]),
                "value": json.dumps(
                    {
                        "decision": row["decision"],
                        "retrieval_best_top1": row["retrieval_best_top1"],
                        "retrieval_best_methods": row["retrieval_best_methods"],
                        "retrieval_solved": row["retrieval_solved"],
                    },
                    sort_keys=True,
                ),
            }
        )
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=("section", "item", "value"))
        writer.writeheader()
        writer.writerows(summary_rows)
    return paths


def print_stage93_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']['decision']}")
    print(f"claim_boundary: {result['decision']['claim_boundary']}")
    print(f"missing_source_artifacts: {len(result['missing_source_artifacts'])}")
