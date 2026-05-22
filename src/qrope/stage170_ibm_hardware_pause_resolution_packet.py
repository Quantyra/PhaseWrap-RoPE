from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


STAGE170_SCHEMA_VERSION = "qrope_stage170_ibm_hardware_pause_resolution_packet_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE159_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage159_first_provider_backend_preflight" / "results.json"
DEFAULT_STAGE161_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage161_first_provider_exposure_packet" / "results.json"
DEFAULT_STAGE162_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage162_first_provider_approval_dossier" / "results.json"
DEFAULT_STAGE163_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage163_first_provider_prerun_lock" / "results.json"
DEFAULT_STAGE169_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage169_targeted_probe_scope_selection" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage170_ibm_hardware_pause_resolution_packet"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)
STAGE159_READY = "FIRST_PROVIDER_BACKEND_PREFLIGHT_READY_AWAITING_APPROVAL"
STAGE161_READY = "FIRST_PROVIDER_EXPOSURE_PACKET_READY_AWAITING_APPROVAL"
STAGE162_READY = "FIRST_PROVIDER_APPROVAL_DOSSIER_READY_FOR_HUMAN_GO_NO_GO"
STAGE163_READY = "FIRST_PROVIDER_PRERUN_LOCK_READY_AWAITING_APPROVAL"
STAGE169_READY = "TARGETED_IBM_PROBE_SCOPE_LOCKED_TO_STABLE_LANES"
APPROVAL_PHRASE = "APPROVE IBM RUNTIME STAGE133 LIVE RUN"


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _decision_record(stage_id: str, payload: dict[str, Any] | None, expected: str, purpose: str) -> dict[str, Any]:
    decision = payload.get("decision") if isinstance(payload, dict) else None
    return {
        "stage_id": stage_id,
        "decision": decision,
        "expected_decision": expected,
        "ready": decision == expected,
        "purpose": purpose,
    }


def run_stage170_pause_packet(
    *,
    stage159_results_path: Path = DEFAULT_STAGE159_RESULTS,
    stage161_results_path: Path = DEFAULT_STAGE161_RESULTS,
    stage162_results_path: Path = DEFAULT_STAGE162_RESULTS,
    stage163_results_path: Path = DEFAULT_STAGE163_RESULTS,
    stage169_results_path: Path = DEFAULT_STAGE169_RESULTS,
) -> dict[str, Any]:
    stage159 = _load_json(stage159_results_path)
    stage161 = _load_json(stage161_results_path)
    stage162 = _load_json(stage162_results_path)
    stage163 = _load_json(stage163_results_path)
    stage169 = _load_json(stage169_results_path)
    sources = [
        (stage159_results_path, stage159),
        (stage161_results_path, stage161),
        (stage162_results_path, stage162),
        (stage163_results_path, stage163),
        (stage169_results_path, stage169),
    ]
    missing_sources = [str(path.as_posix()) for path, payload in sources if not isinstance(payload, dict)]
    decision_records = [
        _decision_record("stage159", stage159, STAGE159_READY, "read-only backend preflight has resolved the IBM target"),
        _decision_record("stage161", stage161, STAGE161_READY, "job, shot, and credit-boundary exposure is quantified"),
        _decision_record("stage162", stage162, STAGE162_READY, "human GO/NO-GO dossier is assembled"),
        _decision_record("stage163", stage163, STAGE163_READY, "pre-run job shard lock is frozen and awaiting approval"),
        _decision_record("stage169", stage169, STAGE169_READY, "current probe scope is locked to stable simulated lanes"),
    ]
    blockers: list[str] = []
    if missing_sources:
        blockers.append("source_artifacts_missing")
    for record in decision_records:
        if not record["ready"]:
            blockers.append(f"{record['stage_id']}_not_ready")
    approval_phrase_required = stage162.get("approval_phrase_required") if isinstance(stage162, dict) else None
    if approval_phrase_required != APPROVAL_PHRASE:
        blockers.append("approval_phrase_mismatch")
    for stage_id, payload in (("stage161", stage161), ("stage162", stage162)):
        if isinstance(payload, dict) and payload.get("runnable_commands_recorded") is not False:
            blockers.append(f"{stage_id}_runnable_commands_recorded")
    if isinstance(stage162, dict) and stage162.get("secret_values_recorded") is not False:
        blockers.append("stage162_secret_values_recorded")
    if isinstance(stage169, dict) and not stage169.get("stable_target_lanes"):
        blockers.append("stage169_no_stable_target_lanes")
    approved_job_count = stage163.get("approved_job_count") if isinstance(stage163, dict) else None
    locked_total_shots = stage163.get("locked_total_shots") if isinstance(stage163, dict) else None
    exposure_job_count = stage161.get("job_count") if isinstance(stage161, dict) else None
    exposure_total_shots = stage161.get("total_shots") if isinstance(stage161, dict) else None
    if approved_job_count is not None and exposure_job_count is not None and int(approved_job_count) != int(exposure_job_count):
        blockers.append("locked_job_count_exposure_mismatch")
    if locked_total_shots is not None and exposure_total_shots is not None and int(locked_total_shots) != int(exposure_total_shots):
        blockers.append("locked_shot_count_exposure_mismatch")
    credit_balance_verified = bool(stage162.get("credit_balance_verified")) if isinstance(stage162, dict) else False
    pause_resolution_items = [
        "Verify IBM account, billing, credits, and allowed Runtime usage outside the artifact.",
        "Confirm the configured IBM backend is still acceptable, or rerun the read-only Stage159 preflight.",
        "Confirm the hardware scope remains the two stable Stage169 seed314 lanes already covered by the Stage163 lock.",
        "Do not broaden to Stage169 excluded lanes without a new stability and scope-selection gate.",
        f"Only after a human GO, provide the exact approval phrase: {APPROVAL_PHRASE}",
    ]
    if credit_balance_verified:
        decision = (
            "IBM_HARDWARE_PAUSE_RESOLUTION_PACKET_INCOMPLETE"
            if missing_sources
            else "IBM_HARDWARE_PAUSE_READY_FOR_FINAL_HUMAN_GO_NO_GO"
            if not blockers
            else "IBM_HARDWARE_PAUSE_RESOLUTION_BLOCKED"
        )
    else:
        decision = (
            "IBM_HARDWARE_PAUSE_RESOLUTION_PACKET_INCOMPLETE"
            if missing_sources
            else "IBM_HARDWARE_PAUSE_READY_FOR_CREDIT_PROVIDER_RESOLUTION"
            if not blockers
            else "IBM_HARDWARE_PAUSE_RESOLUTION_BLOCKED"
        )
    return {
        "schema_version": STAGE170_SCHEMA_VERSION,
        "stage": "stage170_ibm_hardware_pause_resolution_packet",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": decision,
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "stage_decision_records": decision_records,
        "first_unlock_provider": stage162.get("first_unlock_provider") if isinstance(stage162, dict) else None,
        "approval_phrase_required": approval_phrase_required,
        "approval_state": stage162.get("approval_state") if isinstance(stage162, dict) else None,
        "credit_balance_verified": credit_balance_verified,
        "backend_lookup_ready": stage159.get("backend_lookup_ready") if isinstance(stage159, dict) else None,
        "backend_pending_jobs_at_preflight": (
            stage159.get("backend_metadata", {}).get("pending_jobs") if isinstance(stage159, dict) else None
        ),
        "locked_job_count": approved_job_count,
        "locked_total_shots": locked_total_shots,
        "exposure_job_count": exposure_job_count,
        "exposure_total_shots": exposure_total_shots,
        "missing_result_record_count": stage161.get("missing_result_record_count") if isinstance(stage161, dict) else None,
        "stage169_stable_target_lanes": stage169.get("stable_target_lanes", []) if isinstance(stage169, dict) else [],
        "stage169_excluded_recommended_lanes": stage169.get("excluded_recommended_lanes", []) if isinstance(stage169, dict) else [],
        "stage169_locked_lane_count": stage169.get("locked_lane_count") if isinstance(stage169, dict) else None,
        "blockers": sorted(set(blockers)),
        "pause_resolution_items": pause_resolution_items,
        "no_hardware_submission": True,
        "explicit_user_approval_required": True,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "runnable_commands_recorded": False,
        "claim_boundary": {
            "supported": [
                "non-submitting pause packet for IBM credit/provider resolution",
                "current first-provider scope is the stable Stage169 seed314 IBM product/CX lanes",
                "locked Stage163 job and shot exposure is carried forward before any final human GO/NO-GO",
                "credit and provider state remain human-verification items outside recorded artifacts",
            ],
            "excluded": [
                "hardware job submission",
                "provider credentials, account tokens, or secret values",
                "runnable live-submit command strings",
                "IBM credit balance or dollar cost verification",
                "a noisy-hardware robustness or auditability conclusion",
            ],
        },
        "next_gate": (
            "Pause with the user to resolve IBM credit/provider state. If that resolves and the decision is GO, require the "
            "exact approval phrase before any live Stage133 execution."
        ),
    }


def write_stage170_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "first_unlock_provider": result["first_unlock_provider"],
        "approval_state": result["approval_state"],
        "credit_balance_verified": result["credit_balance_verified"],
        "backend_lookup_ready": result["backend_lookup_ready"],
        "backend_pending_jobs_at_preflight": result["backend_pending_jobs_at_preflight"],
        "locked_job_count": result["locked_job_count"],
        "locked_total_shots": result["locked_total_shots"],
        "stage169_stable_target_lanes": result["stage169_stable_target_lanes"],
        "stage169_excluded_recommended_lanes": result["stage169_excluded_recommended_lanes"],
        "blockers": result["blockers"],
        "pause_resolution_items": result["pause_resolution_items"],
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
        writer = csv.DictWriter(handle, fieldnames=("item_type", "item", "state"))
        writer.writeheader()
        for record in result["stage_decision_records"]:
            writer.writerow({"item_type": record["stage_id"], "item": record["purpose"], "state": "ready" if record["ready"] else "not_ready"})
        for item in result["pause_resolution_items"]:
            writer.writerow({"item_type": "pause_resolution", "item": item, "state": "human_check_required"})
    return paths


def print_stage170_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"first_unlock_provider: {result['first_unlock_provider']}")
    print(f"locked_job_count: {result['locked_job_count']}")
    print(f"locked_total_shots: {result['locked_total_shots']}")
    print(f"credit_balance_verified: {result['credit_balance_verified']}")
    print(f"blockers: {', '.join(result['blockers'])}")
    print(f"next_gate: {result['next_gate']}")
