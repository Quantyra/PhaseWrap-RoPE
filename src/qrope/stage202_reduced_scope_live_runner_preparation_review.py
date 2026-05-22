from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from qrope.stage193_replacement_read_only_backend_refresh import DEFAULT_OUTPUT_DIR as STAGE193_OUTPUT_DIR
from qrope.stage198_reduced_scope_preregistration import DEFAULT_OUTPUT_DIR as STAGE198_OUTPUT_DIR
from qrope.stage201_reduced_scope_exact_approval_review import DEFAULT_OUTPUT_DIR as STAGE201_OUTPUT_DIR
from qrope.stage99_matched_fixed_width_encoding_packet_freezer import OBJECTIVE


STAGE202_SCHEMA_VERSION = "qrope_stage202_reduced_scope_live_runner_preparation_review_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE201_RESULTS = STAGE201_OUTPUT_DIR / "results.json"
DEFAULT_STAGE198_RESULTS = STAGE198_OUTPUT_DIR / "results.json"
DEFAULT_STAGE193_RESULTS = STAGE193_OUTPUT_DIR / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage202_reduced_scope_live_runner_preparation_review"
STAGE201_ACCEPTED = "REDUCED_SCOPE_EXACT_APPROVAL_ACCEPTED_READY_FOR_LIVE_RUNNER_PREPARATION_REVIEW"
STAGE198_READY = "REDUCED_SCOPE_PREREGISTERED_READY_FOR_COST_ATTESTATION_REVIEW"
STAGE193_READY = "REPLACEMENT_READ_ONLY_BACKEND_REFRESH_READY_CREDIT_AND_APPROVAL_STILL_REQUIRED"


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _item(item_id: str, status: str, description: str, evidence: Any) -> dict[str, Any]:
    return {"item_id": item_id, "status": status, "description": description, "evidence": evidence}


def run_stage202_reduced_scope_live_runner_preparation_review(
    *,
    stage201_results_path: Path = DEFAULT_STAGE201_RESULTS,
    stage198_results_path: Path = DEFAULT_STAGE198_RESULTS,
    stage193_results_path: Path = DEFAULT_STAGE193_RESULTS,
) -> dict[str, Any]:
    stage201 = _load_json(stage201_results_path)
    stage198 = _load_json(stage198_results_path)
    stage193 = _load_json(stage193_results_path)
    missing_sources = [
        str(path.as_posix())
        for path, payload in (
            (stage201_results_path, stage201),
            (stage198_results_path, stage198),
            (stage193_results_path, stage193),
        )
        if not isinstance(payload, dict)
    ]

    stage201_decision = stage201.get("decision") if isinstance(stage201, dict) else None
    exact_approval_ready = bool(
        isinstance(stage201, dict)
        and stage201_decision == STAGE201_ACCEPTED
        and stage201.get("approval_phrase_matches") is True
        and stage201.get("human_credit_allowance_verified") is True
    )
    stage198_ready = bool(isinstance(stage198, dict) and stage198.get("decision") == STAGE198_READY)
    stage193_ready = bool(
        isinstance(stage193, dict)
        and stage193.get("decision") == STAGE193_READY
        and stage193.get("backend_lookup_ready") is True
    )
    scope = stage198.get("selected_scope", {}) if isinstance(stage198, dict) else {}
    boundary = stage198.get("interpretation_boundary", {}) if isinstance(stage198, dict) else {}
    backend_metadata = stage193.get("backend_metadata", {}) if isinstance(stage193, dict) else {}
    reduced_scope_frozen = (
        stage198_ready
        and scope.get("scope_id") == "all_lanes_half_shots_2048"
        and scope.get("shots_per_row") == 2048
        and scope.get("estimated_total_job_count") == 324
        and scope.get("estimated_total_shots") == 659360
    )

    preparation_items = [
        _item(
            "stage201_exact_reduced_scope_approval",
            "accepted" if exact_approval_ready else "blocked",
            "Live-runner preparation is disallowed until Stage201 records exact reduced-scope approval after credit attestation.",
            {
                "stage201_decision": stage201_decision,
                "human_credit_allowance_verified": stage201.get("human_credit_allowance_verified") if isinstance(stage201, dict) else None,
                "approval_phrase_matches": stage201.get("approval_phrase_matches") if isinstance(stage201, dict) else None,
            },
        ),
        _item(
            "reduced_scope_preregistration",
            "frozen" if reduced_scope_frozen else "blocked",
            "Runner preparation must preserve the Stage198 all-lanes 2048-shot reduced-precision boundary.",
            {
                "stage198_decision": stage198.get("decision") if isinstance(stage198, dict) else None,
                "scope_id": scope.get("scope_id"),
                "shots_per_row": scope.get("shots_per_row"),
                "estimated_total_job_count": scope.get("estimated_total_job_count"),
                "estimated_total_shots": scope.get("estimated_total_shots"),
            },
        ),
        _item(
            "read_only_backend_refresh",
            "ready_refresh_before_execution" if stage193_ready else "blocked",
            "The latest available IBM backend metadata is read-only evidence; it should be refreshed again close to any approved execution.",
            {
                "stage193_decision": stage193.get("decision") if isinstance(stage193, dict) else None,
                "backend_lookup_ready": stage193.get("backend_lookup_ready") if isinstance(stage193, dict) else None,
                "backend": backend_metadata.get("backend"),
                "operational": backend_metadata.get("operational"),
                "pending_jobs": backend_metadata.get("pending_jobs"),
            },
        ),
        _item(
            "reduced_scope_execution_package",
            "required_not_created",
            "Stage190 is a 4096-shot replacement package; a separate 2048-shot reduced-scope package must be generated before runner work.",
            {
                "stage190_scope_reusable_as_is": False,
                "required_packet_row_shots": boundary.get("shots_per_row"),
                "required_packet_row_jobs": scope.get("packet_row_job_count"),
                "required_calibration_jobs": scope.get("calibration_job_count"),
            },
        ),
        _item(
            "result_ingestion_contract",
            "required_not_created",
            "Runner preparation must preserve canonical raw counts, job IDs, timestamps, backend metadata, and calibration counts for later Stage101/103/137/148 interpretation.",
            {
                "required_packet_fields": ["job_or_task_ids", "backend_metadata", "submitted_at_utc", "completed_at_utc", "raw_counts_by_row"],
                "required_calibration_states": boundary.get("calibration_states"),
                "calibration_shots_per_state": boundary.get("calibration_shots_per_state"),
            },
        ),
        _item(
            "live_execution_boundary",
            "no_runner_created",
            "This review does not create runnable commands, write credentials, submit hardware, or bypass the later execution-package gate.",
            {"hardware_submitted_here": False, "live_submit_command_created_here": False, "runnable_commands_recorded_here": False},
        ),
    ]

    blockers: list[str] = []
    if missing_sources:
        blockers.append("source_artifacts_missing")
    if not exact_approval_ready:
        blockers.append("stage201_exact_reduced_scope_approval_not_accepted")
    if not reduced_scope_frozen:
        blockers.append("stage198_reduced_scope_not_frozen")
    if not stage193_ready:
        blockers.append("stage193_read_only_backend_refresh_not_ready")
    blockers.append("reduced_scope_execution_package_required")
    blockers.append("result_ingestion_contract_required")

    if missing_sources:
        decision = "REDUCED_SCOPE_LIVE_RUNNER_PREPARATION_REVIEW_INCOMPLETE"
    elif exact_approval_ready and reduced_scope_frozen and stage193_ready:
        decision = "REDUCED_SCOPE_LIVE_RUNNER_PREPARATION_REVIEW_READY_TO_BUILD_PACKAGE_NOT_LIVE"
    else:
        decision = "REDUCED_SCOPE_LIVE_RUNNER_PREPARATION_REVIEW_BLOCKED_APPROVAL_OR_PACKAGE_REQUIRED"

    return {
        "schema_version": STAGE202_SCHEMA_VERSION,
        "stage": "stage202_reduced_scope_live_runner_preparation_review",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": decision,
        "source_artifacts": [str(path.as_posix()) for path in (stage201_results_path, stage198_results_path, stage193_results_path)],
        "missing_source_artifacts": missing_sources,
        "blockers": sorted(set(blockers)),
        "stage201_decision": stage201_decision,
        "stage198_decision": stage198.get("decision") if isinstance(stage198, dict) else None,
        "stage193_decision": stage193.get("decision") if isinstance(stage193, dict) else None,
        "scope_id": scope.get("scope_id"),
        "hardware_scope_label": boundary.get("hardware_scope_label"),
        "estimated_total_job_count": scope.get("estimated_total_job_count"),
        "estimated_total_shots": scope.get("estimated_total_shots"),
        "shots_per_row": scope.get("shots_per_row"),
        "budget_cap_usd": stage201.get("budget_cap_usd") if isinstance(stage201, dict) else None,
        "backend_metadata": backend_metadata,
        "exact_approval_ready": exact_approval_ready,
        "reduced_scope_frozen": reduced_scope_frozen,
        "read_only_backend_ready": stage193_ready,
        "reduced_scope_execution_package_created": False,
        "result_ingestion_contract_created": False,
        "preparation_items": preparation_items,
        "no_hardware_submission": True,
        "live_submit_command_created": False,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "runnable_commands_recorded": False,
        "explicit_user_approval_required": True,
        "claim_boundary": {
            "supported": [
                "reduced-scope runner preparation remains blocked until credit attestation and exact approval are accepted",
                "Stage190 4096-shot templates are identified as non-reusable for the 2048-shot reduced scope",
                "runner preparation requirements are enumerated without creating submit commands",
            ],
            "excluded": [
                "hardware job submission",
                "creation of a runnable live-submit command",
                "provider-side IBM credit balance verification",
                "result ingestion, calibration pass, or metric interpretation",
                "a noisy-hardware robustness or auditability conclusion",
            ],
        },
        "next_gate": (
            "After Stage200 credit attestation and Stage201 exact approval are both accepted, build a reduced-scope 2048-shot "
            "execution package and result-ingestion contract. This Stage202 review does not authorize direct hardware submission."
        ),
    }


def write_stage202_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_keys = (
        "schema_version",
        "stage",
        "status",
        "objective",
        "decision",
        "source_artifacts",
        "missing_source_artifacts",
        "blockers",
        "stage201_decision",
        "stage198_decision",
        "stage193_decision",
        "scope_id",
        "hardware_scope_label",
        "estimated_total_job_count",
        "estimated_total_shots",
        "shots_per_row",
        "budget_cap_usd",
        "backend_metadata",
        "exact_approval_ready",
        "reduced_scope_frozen",
        "read_only_backend_ready",
        "reduced_scope_execution_package_created",
        "result_ingestion_contract_created",
        "no_hardware_submission",
        "live_submit_command_created",
        "provider_credentials_required",
        "secret_values_recorded",
        "runnable_commands_recorded",
        "explicit_user_approval_required",
        "claim_boundary",
        "next_gate",
    )
    manifest = {key: result[key] for key in manifest_keys}
    manifest["result_path"] = str((output_dir / "results.json").as_posix())
    manifest["summary_csv_path"] = str((output_dir / "summary.csv").as_posix())
    paths = {"manifest": str(output_dir / "manifest.json"), "result": str(output_dir / "results.json"), "summary_csv": str(output_dir / "summary.csv")}
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=("item_id", "status", "description"))
        writer.writeheader()
        for item in result["preparation_items"]:
            writer.writerow({field: item.get(field) for field in writer.fieldnames})
    return paths


def print_stage202_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"scope_id: {result['scope_id']}")
    print(f"estimated_total_job_count: {result['estimated_total_job_count']}")
    print(f"estimated_total_shots: {result['estimated_total_shots']}")
    print(f"shots_per_row: {result['shots_per_row']}")
    print(f"exact_approval_ready: {result['exact_approval_ready']}")
    print(f"reduced_scope_execution_package_created: {result['reduced_scope_execution_package_created']}")
    print(f"blockers: {', '.join(result['blockers'])}")
    print(f"next_gate: {result['next_gate']}")
