from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


STAGE176_SCHEMA_VERSION = "qrope_stage176_ibm_credit_provider_resolution_handoff_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE159_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage159_first_provider_backend_preflight" / "results.json"
DEFAULT_STAGE170_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage170_ibm_hardware_pause_resolution_packet" / "results.json"
DEFAULT_STAGE175_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage175_first_provider_preresult_readiness_synthesis" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage176_ibm_credit_provider_resolution_handoff"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)
STAGE159_READY = "FIRST_PROVIDER_BACKEND_PREFLIGHT_READY_AWAITING_APPROVAL"
STAGE170_READY = "IBM_HARDWARE_PAUSE_READY_FOR_CREDIT_PROVIDER_RESOLUTION"
STAGE175_READY = "FIRST_PROVIDER_PRERESULT_READY_FOR_CREDIT_PROVIDER_RESOLUTION"
STAGE175_FINAL_READY = "FIRST_PROVIDER_PRERESULT_READY_FOR_FINAL_HUMAN_GO_NO_GO"
APPROVAL_PHRASE = "APPROVE IBM RUNTIME STAGE133 LIVE RUN"


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _resolution_item(item_id: str, description: str, status: str, evidence: Any) -> dict[str, Any]:
    return {
        "item_id": item_id,
        "description": description,
        "status": status,
        "evidence": evidence,
    }


def run_stage176_resolution_handoff(
    *,
    stage159_results_path: Path = DEFAULT_STAGE159_RESULTS,
    stage170_results_path: Path = DEFAULT_STAGE170_RESULTS,
    stage175_results_path: Path = DEFAULT_STAGE175_RESULTS,
) -> dict[str, Any]:
    stage159 = _load_json(stage159_results_path)
    stage170 = _load_json(stage170_results_path)
    stage175 = _load_json(stage175_results_path)
    sources = [(stage159_results_path, stage159), (stage170_results_path, stage170), (stage175_results_path, stage175)]
    missing_sources = [str(path.as_posix()) for path, payload in sources if not isinstance(payload, dict)]
    blockers: list[str] = []
    if missing_sources:
        blockers.append("source_artifacts_missing")
    if isinstance(stage159, dict) and stage159.get("decision") != STAGE159_READY:
        blockers.append("stage159_backend_preflight_not_ready")
    if isinstance(stage170, dict) and stage170.get("decision") != STAGE170_READY:
        blockers.append("stage170_pause_packet_not_at_credit_resolution")
    if isinstance(stage175, dict) and stage175.get("decision") not in {STAGE175_READY, STAGE175_FINAL_READY}:
        blockers.append("stage175_preresult_synthesis_not_ready")
    approval_phrase_required = stage170.get("approval_phrase_required") if isinstance(stage170, dict) else None
    if approval_phrase_required != APPROVAL_PHRASE:
        blockers.append("approval_phrase_mismatch")
    credit_balance_verified = bool(stage175.get("credit_balance_verified")) if isinstance(stage175, dict) else False
    resolution_items = [
        _resolution_item(
            "configured_credentials_present",
            "IBM token, instance, and backend configuration were present for the latest read-only backend lookup.",
            "verified_non_secret_presence" if isinstance(stage159, dict) and stage159.get("ibm_token_present") and stage159.get("ibm_instance_crn_present") and stage159.get("ibm_backend_env_present") else "needs_attention",
            {
                "ibm_token_present": stage159.get("ibm_token_present") if isinstance(stage159, dict) else None,
                "ibm_instance_crn_present": stage159.get("ibm_instance_crn_present") if isinstance(stage159, dict) else None,
                "ibm_backend_env_present": stage159.get("ibm_backend_env_present") if isinstance(stage159, dict) else None,
            },
        ),
        _resolution_item(
            "backend_read_only_preflight",
            "Configured IBM backend resolved read-only without hardware submission.",
            "verified" if isinstance(stage159, dict) and stage159.get("backend_lookup_ready") is True else "needs_read_only_refresh",
            {
                "backend": stage159.get("backend_metadata", {}).get("backend") if isinstance(stage159, dict) else None,
                "operational": stage159.get("backend_metadata", {}).get("operational") if isinstance(stage159, dict) else None,
                "pending_jobs_at_preflight": stage159.get("backend_metadata", {}).get("pending_jobs") if isinstance(stage159, dict) else None,
            },
        ),
        _resolution_item(
            "credit_billing_runtime_allowance",
            "IBM account credit, billing, and Runtime allowance must be verified by the user outside the artifact.",
            "verified" if credit_balance_verified else "human_verification_required",
            {"credit_balance_verified": credit_balance_verified},
        ),
        _resolution_item(
            "locked_scope_confirmation",
            "Human GO/NO-GO discussion is limited to the locked stable Stage169 seed314 IBM lanes.",
            "verified",
            {
                "stable_target_lanes": stage175.get("stable_target_lanes", []) if isinstance(stage175, dict) else [],
                "locked_job_count": stage175.get("locked_job_count") if isinstance(stage175, dict) else None,
                "locked_total_shots": stage175.get("locked_total_shots") if isinstance(stage175, dict) else None,
            },
        ),
        _resolution_item(
            "exact_approval_phrase",
            "Live execution remains disallowed unless the exact approval phrase is provided after credit/provider resolution.",
            "awaiting_exact_phrase",
            {"approval_phrase_required": approval_phrase_required},
        ),
    ]
    if any(item["status"] == "needs_attention" for item in resolution_items):
        blockers.append("configured_credentials_presence_not_verified")
    if any(item["status"] == "needs_read_only_refresh" for item in resolution_items):
        blockers.append("backend_read_only_preflight_not_verified")
    decision = (
        "IBM_CREDIT_PROVIDER_RESOLUTION_HANDOFF_INCOMPLETE"
        if missing_sources
        else "IBM_CREDIT_PROVIDER_RESOLUTION_HANDOFF_READY_FOR_HUMAN_CHECK"
        if not blockers and not credit_balance_verified
        else "IBM_CREDIT_PROVIDER_RESOLUTION_HANDOFF_READY_FOR_FINAL_GO_NO_GO"
        if not blockers and credit_balance_verified
        else "IBM_CREDIT_PROVIDER_RESOLUTION_HANDOFF_BLOCKED"
    )
    return {
        "schema_version": STAGE176_SCHEMA_VERSION,
        "stage": "stage176_ibm_credit_provider_resolution_handoff",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": decision,
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "stage159_decision": stage159.get("decision") if isinstance(stage159, dict) else None,
        "stage170_decision": stage170.get("decision") if isinstance(stage170, dict) else None,
        "stage175_decision": stage175.get("decision") if isinstance(stage175, dict) else None,
        "first_unlock_provider": stage175.get("first_unlock_provider") if isinstance(stage175, dict) else None,
        "credit_balance_verified": credit_balance_verified,
        "approval_phrase_required": approval_phrase_required,
        "resolution_items": resolution_items,
        "locked_job_count": stage175.get("locked_job_count") if isinstance(stage175, dict) else None,
        "locked_total_shots": stage175.get("locked_total_shots") if isinstance(stage175, dict) else None,
        "stable_target_lanes": stage175.get("stable_target_lanes", []) if isinstance(stage175, dict) else [],
        "blockers": sorted(set(blockers)),
        "no_hardware_submission": True,
        "explicit_user_approval_required": True,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "runnable_commands_recorded": False,
        "claim_boundary": {
            "supported": [
                "controlled no-secret handoff for resolving IBM credit/provider state with the user",
                "non-secret confirmation that read-only IBM configuration and backend lookup previously succeeded",
                "explicit distinction between configured credentials presence and verified credit/billing allowance",
                "scope confirmation for the locked first-provider IBM run before any final GO/NO-GO",
            ],
            "excluded": [
                "hardware job submission",
                "provider credentials, token values, CRN values, or account secrets",
                "runnable live-submit command strings",
                "IBM credit balance or dollar cost verification",
                "provider result records",
                "a noisy-hardware robustness or auditability conclusion",
            ],
        },
        "next_gate": (
            "Resolve the human-only IBM credit/billing/Runtime allowance check. If acceptable, perform a final GO/NO-GO "
            "against the locked scope and require the exact approval phrase before any live execution."
        ),
    }


def write_stage176_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "stage159_decision": result["stage159_decision"],
        "stage170_decision": result["stage170_decision"],
        "stage175_decision": result["stage175_decision"],
        "first_unlock_provider": result["first_unlock_provider"],
        "credit_balance_verified": result["credit_balance_verified"],
        "locked_job_count": result["locked_job_count"],
        "locked_total_shots": result["locked_total_shots"],
        "stable_target_lanes": result["stable_target_lanes"],
        "blockers": result["blockers"],
        "no_hardware_submission": result["no_hardware_submission"],
        "explicit_user_approval_required": result["explicit_user_approval_required"],
        "provider_credentials_required": result["provider_credentials_required"],
        "secret_values_recorded": result["secret_values_recorded"],
        "runnable_commands_recorded": result["runnable_commands_recorded"],
        "result_path": str((output_dir / "results.json").as_posix()),
        "summary_csv_path": str((output_dir / "summary.csv").as_posix()),
        "claim_boundary": result["claim_boundary"],
        "next_gate": result["next_gate"],
    }
    paths = {
        "manifest": str(output_dir / "manifest.json"),
        "result": str(output_dir / "results.json"),
        "summary_csv": str(output_dir / "summary.csv"),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=("item_id", "status", "description"))
        writer.writeheader()
        for item in result["resolution_items"]:
            writer.writerow({field: item.get(field) for field in writer.fieldnames})
    return paths


def print_stage176_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"credit_balance_verified: {result['credit_balance_verified']}")
    print(f"locked_job_count: {result['locked_job_count']}")
    print(f"locked_total_shots: {result['locked_total_shots']}")
    print(f"blockers: {', '.join(result['blockers'])}")
    print(f"next_gate: {result['next_gate']}")
