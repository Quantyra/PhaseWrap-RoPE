from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from qrope.stage189_replacement_hardware_readiness_review import APPROVAL_PHRASE
from qrope.stage194_replacement_credit_allowance_decision_packet import DEFAULT_OUTPUT_DIR as STAGE194_OUTPUT_DIR
from qrope.stage99_matched_fixed_width_encoding_packet_freezer import OBJECTIVE


STAGE195_SCHEMA_VERSION = "qrope_stage195_replacement_exact_approval_review_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE194_RESULTS = STAGE194_OUTPUT_DIR / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage195_replacement_exact_approval_review"
STAGE194_CREDIT_VERIFIED = "REPLACEMENT_CREDIT_ALLOWANCE_VERIFIED_READY_FOR_EXACT_APPROVAL_REVIEW"
STAGE194_HUMAN_ATTESTATION_OPEN = "REPLACEMENT_CREDIT_ALLOWANCE_READY_FOR_HUMAN_ATTESTATION_NOT_LIVE"


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _approval_item(item_id: str, status: str, description: str, evidence: Any) -> dict[str, Any]:
    return {"item_id": item_id, "status": status, "description": description, "evidence": evidence}


def run_stage195_replacement_exact_approval_review(
    *,
    stage194_results_path: Path = DEFAULT_STAGE194_RESULTS,
    provided_approval_phrase: str | None = None,
) -> dict[str, Any]:
    stage194 = _load_json(stage194_results_path)
    missing_sources = [] if isinstance(stage194, dict) else [str(stage194_results_path.as_posix())]
    stage194_decision = stage194.get("decision") if isinstance(stage194, dict) else None
    credit_verified = bool(stage194.get("human_credit_allowance_verified")) if isinstance(stage194, dict) else False
    credit_gate_ready = stage194_decision == STAGE194_CREDIT_VERIFIED and credit_verified
    credit_gate_attestation_open = stage194_decision == STAGE194_HUMAN_ATTESTATION_OPEN and not credit_verified
    phrase_provided = provided_approval_phrase is not None
    phrase_matches = provided_approval_phrase == APPROVAL_PHRASE
    approval_items = [
        _approval_item(
            "credit_allowance_gate",
            "verified" if credit_gate_ready else "human_attestation_required" if credit_gate_attestation_open else "blocked",
            "Exact approval review requires Stage194 credit/billing/Runtime allowance verification first.",
            {
                "stage194_decision": stage194_decision,
                "human_credit_allowance_verified": credit_verified,
                "budget_cap_usd": stage194.get("budget_cap_usd") if isinstance(stage194, dict) else None,
            },
        ),
        _approval_item(
            "replacement_exposure_confirmation",
            "recorded" if isinstance(stage194, dict) else "missing",
            "The human approver must have the replacement exposure available before any approval phrase can be accepted.",
            {
                "estimated_total_job_count": stage194.get("estimated_total_job_count") if isinstance(stage194, dict) else None,
                "estimated_total_shots": stage194.get("estimated_total_shots") if isinstance(stage194, dict) else None,
            },
        ),
        _approval_item(
            "exact_approval_phrase",
            "accepted" if credit_gate_ready and phrase_matches else "not_requested" if not credit_gate_ready else "missing_or_mismatched",
            "The approval phrase is only evaluated after credit allowance is verified; it must match the replacement phrase exactly.",
            {
                "approval_phrase_required": APPROVAL_PHRASE,
                "provided_approval_phrase_present": phrase_provided,
                "approval_phrase_matches": phrase_matches if credit_gate_ready else False,
            },
        ),
        _approval_item(
            "live_execution_boundary",
            "runner_preparation_review_allowed" if credit_gate_ready and phrase_matches else "live_run_disallowed",
            "This gate never submits hardware; at most it allows a later live-runner preparation review.",
            {"hardware_submitted_here": False, "live_submit_command_created_here": False},
        ),
    ]
    blockers: list[str] = []
    if missing_sources:
        blockers.append("source_artifacts_missing")
    if not credit_gate_ready:
        blockers.append("credit_allowance_not_verified")
    if credit_gate_ready and not phrase_matches:
        blockers.append("exact_replacement_approval_phrase_missing_or_mismatched")
    if missing_sources:
        decision = "REPLACEMENT_EXACT_APPROVAL_REVIEW_INCOMPLETE"
    elif credit_gate_ready and phrase_matches:
        decision = "REPLACEMENT_EXACT_APPROVAL_ACCEPTED_READY_FOR_LIVE_RUNNER_PREPARATION_REVIEW"
    elif credit_gate_attestation_open:
        decision = "REPLACEMENT_EXACT_APPROVAL_REVIEW_BLOCKED_CREDIT_ATTESTATION_REQUIRED"
    else:
        decision = "REPLACEMENT_EXACT_APPROVAL_REVIEW_BLOCKED"
    return {
        "schema_version": STAGE195_SCHEMA_VERSION,
        "stage": "stage195_replacement_exact_approval_review",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": decision,
        "source_artifacts": [str(stage194_results_path.as_posix())],
        "missing_source_artifacts": missing_sources,
        "blockers": sorted(set(blockers)),
        "stage194_decision": stage194_decision,
        "human_credit_allowance_verified": credit_verified,
        "estimated_total_job_count": stage194.get("estimated_total_job_count") if isinstance(stage194, dict) else None,
        "estimated_total_shots": stage194.get("estimated_total_shots") if isinstance(stage194, dict) else None,
        "budget_cap_usd": stage194.get("budget_cap_usd") if isinstance(stage194, dict) else None,
        "approval_phrase_required": APPROVAL_PHRASE,
        "provided_approval_phrase_present": phrase_provided,
        "approval_phrase_matches": phrase_matches if credit_gate_ready else False,
        "approval_items": approval_items,
        "no_hardware_submission": True,
        "live_submit_command_created": False,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "runnable_commands_recorded": False,
        "explicit_user_approval_required": True,
        "claim_boundary": {
            "supported": [
                "exact replacement approval is isolated from credit allowance verification",
                "approval phrase matching is only accepted after Stage194 records human credit allowance verification",
                "a successful approval review permits only later live-runner preparation review",
            ],
            "excluded": [
                "hardware job submission",
                "Sampler or Estimator runtime execution",
                "provider credentials, token values, CRN values, or account secrets",
                "provider-side IBM credit balance or dollar-cost verification",
                "creation of a runnable live-submit command",
                "a noisy-hardware robustness or auditability conclusion",
            ],
        },
        "next_gate": (
            "Resolve Stage194 credit allowance first. If the user then provides the exact replacement approval phrase, rerun "
            "Stage195 with that phrase and proceed only to live-runner preparation review, not direct submission."
        ),
    }


def write_stage195_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
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
        "stage194_decision",
        "human_credit_allowance_verified",
        "estimated_total_job_count",
        "estimated_total_shots",
        "budget_cap_usd",
        "approval_phrase_required",
        "provided_approval_phrase_present",
        "approval_phrase_matches",
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
        for item in result["approval_items"]:
            writer.writerow({field: item.get(field) for field in writer.fieldnames})
    return paths


def print_stage195_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"human_credit_allowance_verified: {result['human_credit_allowance_verified']}")
    print(f"provided_approval_phrase_present: {result['provided_approval_phrase_present']}")
    print(f"approval_phrase_matches: {result['approval_phrase_matches']}")
    print(f"blockers: {', '.join(result['blockers'])}")
    print(f"next_gate: {result['next_gate']}")
