from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


STAGE179_SCHEMA_VERSION = "qrope_stage179_current_ibm_hardware_path_disposition_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE169_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage169_targeted_probe_scope_selection" / "results.json"
DEFAULT_STAGE176_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage176_ibm_credit_provider_resolution_handoff" / "results.json"
DEFAULT_STAGE177_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage177_ibm_backend_informed_noise_probe" / "results.json"
DEFAULT_STAGE178_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage178_ibm_coherent_offset_sensitivity" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage179_current_ibm_hardware_path_disposition"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)
STAGE169_LOCKED = "TARGETED_IBM_PROBE_SCOPE_LOCKED_TO_STABLE_LANES"
STAGE176_CREDIT_HANDOFF = "IBM_CREDIT_PROVIDER_RESOLUTION_HANDOFF_READY_FOR_HUMAN_CHECK"
STAGE177_NO_GO = "IBM_BACKEND_INFORMED_SIM_DOES_NOT_SUPPORT_TARGETED_HARDWARE_RUN_YET"
STAGE178_NO_RECOVERY = "IBM_COHERENT_OFFSET_SENSITIVITY_DOES_NOT_RECOVER_TARGETED_SIGNAL"


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _decision(payload: Any) -> str | None:
    return str(payload.get("decision")) if isinstance(payload, dict) and payload.get("decision") else None


def _stable_count(payload: Any, key: str) -> int | None:
    if not isinstance(payload, dict):
        return None
    value = payload.get(key)
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _requirement_records(stage169: dict[str, Any] | None, stage176: dict[str, Any] | None, stage177: dict[str, Any] | None, stage178: dict[str, Any] | None) -> list[dict[str, Any]]:
    locked_jobs = stage169.get("approved_job_count") if isinstance(stage169, dict) else None
    locked_shots = stage169.get("locked_total_shots") if isinstance(stage169, dict) else None
    return [
        {
            "requirement_id": "locked_scope_exists",
            "status": "satisfied" if _decision(stage169) == STAGE169_LOCKED else "missing_or_failed",
            "evidence": {
                "stage169_decision": _decision(stage169),
                "locked_lanes": stage169.get("locked_lane_ids") if isinstance(stage169, dict) else None,
                "approved_job_count": locked_jobs,
                "locked_total_shots": locked_shots,
            },
        },
        {
            "requirement_id": "credit_not_reason_to_proceed",
            "status": "satisfied" if _decision(stage176) == STAGE176_CREDIT_HANDOFF else "missing_or_failed",
            "evidence": {
                "stage176_decision": _decision(stage176),
                "credit_balance_verified": stage176.get("credit_balance_verified") if isinstance(stage176, dict) else None,
            },
        },
        {
            "requirement_id": "ibm_backend_informed_simulation_support",
            "status": "contradicted" if _decision(stage177) == STAGE177_NO_GO else "not_contradicted",
            "evidence": {
                "stage177_decision": _decision(stage177),
                "primary_stable_target_count": _stable_count(stage177, "primary_stable_target_count"),
                "proxy_stable_target_count": _stable_count(stage177, "proxy_stable_target_count"),
                "backend": stage177.get("backend_snapshot_summary", {}).get("backend") if isinstance(stage177, dict) else None,
            },
        },
        {
            "requirement_id": "coherent_offset_recovery_support",
            "status": "contradicted" if _decision(stage178) == STAGE178_NO_RECOVERY else "not_contradicted",
            "evidence": {
                "stage178_decision": _decision(stage178),
                "stable_offset_count": _stable_count(stage178, "stable_offset_count"),
                "locked_offset_record_count": _stable_count(stage178, "locked_offset_record_count"),
                "signed_offsets_radians": stage178.get("signed_offsets_radians") if isinstance(stage178, dict) else None,
            },
        },
    ]


def run_stage179_current_ibm_hardware_path_disposition(
    *,
    stage169_results_path: Path = DEFAULT_STAGE169_RESULTS,
    stage176_results_path: Path = DEFAULT_STAGE176_RESULTS,
    stage177_results_path: Path = DEFAULT_STAGE177_RESULTS,
    stage178_results_path: Path = DEFAULT_STAGE178_RESULTS,
) -> dict[str, Any]:
    stage169 = _load_json(stage169_results_path)
    stage176 = _load_json(stage176_results_path)
    stage177 = _load_json(stage177_results_path)
    stage178 = _load_json(stage178_results_path)
    sources = [
        (stage169_results_path, stage169),
        (stage176_results_path, stage176),
        (stage177_results_path, stage177),
        (stage178_results_path, stage178),
    ]
    missing_sources = [str(path.as_posix()) for path, payload in sources if not isinstance(payload, dict)]
    blockers = []
    if missing_sources:
        blockers.append("missing_source_artifacts")
    if isinstance(stage169, dict) and _decision(stage169) != STAGE169_LOCKED:
        blockers.append("stage169_scope_not_locked")
    if isinstance(stage177, dict) and _decision(stage177) != STAGE177_NO_GO:
        blockers.append("stage177_not_backend_informed_no_go")
    if isinstance(stage178, dict) and _decision(stage178) != STAGE178_NO_RECOVERY:
        blockers.append("stage178_not_offset_no_recovery")

    requirement_records = _requirement_records(
        stage169 if isinstance(stage169, dict) else None,
        stage176 if isinstance(stage176, dict) else None,
        stage177 if isinstance(stage177, dict) else None,
        stage178 if isinstance(stage178, dict) else None,
    )
    if blockers:
        decision = "CURRENT_IBM_HARDWARE_PATH_DISPOSITION_INCOMPLETE"
        disposition = "unresolved"
    elif _decision(stage177) == STAGE177_NO_GO and _decision(stage178) == STAGE178_NO_RECOVERY:
        decision = "CURRENT_IBM_HARDWARE_PATH_ARCHIVE_RECOMMENDED"
        disposition = "archive_current_328_job_ibm_run"
    else:
        decision = "CURRENT_IBM_HARDWARE_PATH_REQUIRES_HUMAN_REVIEW"
        disposition = "manual_review"

    return {
        "schema_version": STAGE179_SCHEMA_VERSION,
        "stage": "stage179_current_ibm_hardware_path_disposition",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": decision,
        "disposition": disposition,
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "blockers": sorted(set(blockers)),
        "requirement_records": requirement_records,
        "locked_scope": {
            "stable_target_lanes": stage169.get("stable_target_lanes") if isinstance(stage169, dict) else None,
            "approved_job_count": stage169.get("approved_job_count") if isinstance(stage169, dict) else None,
            "locked_total_shots": stage169.get("locked_total_shots") if isinstance(stage169, dict) else None,
        },
        "evidence_summary": {
            "stage177_primary_stable_target_count": _stable_count(stage177, "primary_stable_target_count"),
            "stage177_proxy_stable_target_count": _stable_count(stage177, "proxy_stable_target_count"),
            "stage178_stable_offset_count": _stable_count(stage178, "stable_offset_count"),
            "stage178_locked_offset_record_count": _stable_count(stage178, "locked_offset_record_count"),
        },
        "reopen_requirements": [
            "a redesigned fixed-width target/circuit family with IBM-backend-informed primary stable targets on both templates",
            "or a new backend/provider whose readout and gate-error-informed simulation preserves PhaseWrap margins above two shot quanta",
            "or real calibration evidence that materially changes the accepted backend-informed noise model before any full matched-packet run",
        ],
        "simulated_only": True,
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "runnable_commands_recorded": False,
        "claim_boundary": {
            "supported": [
                "formal no-submit disposition of the current locked IBM 328-job hardware path",
                "evidence-based separation between archiving the current IBM run and completing the broader noisy-hardware objective",
                "reopen criteria for future hardware-path redesign",
            ],
            "excluded": [
                "hardware job submission",
                "IBM credit or billing verification",
                "a final noisy-hardware robustness or auditability conclusion",
                "a claim that PhaseWrap lacks advantages on all possible noisy quantum hardware targets",
            ],
        },
        "next_gate": (
            "Archive the current locked IBM run. Continue the objective only through redesigned fixed-width targets, alternative "
            "providers/backends, or stronger calibration evidence that changes the accepted noise model."
        ),
    }


def write_stage179_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        key: result[key]
        for key in (
            "schema_version",
            "stage",
            "status",
            "objective",
            "decision",
            "disposition",
            "source_artifacts",
            "missing_source_artifacts",
            "blockers",
            "locked_scope",
            "evidence_summary",
            "reopen_requirements",
            "simulated_only",
            "no_hardware_submission",
            "provider_credentials_required",
            "secret_values_recorded",
            "runnable_commands_recorded",
            "claim_boundary",
            "next_gate",
        )
    }
    manifest["result_path"] = str((output_dir / "results.json").as_posix())
    manifest["summary_csv_path"] = str((output_dir / "summary.csv").as_posix())
    paths = {
        "manifest": str(output_dir / "manifest.json"),
        "result": str(output_dir / "results.json"),
        "summary_csv": str(output_dir / "summary.csv"),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=("requirement_id", "status", "evidence"))
        writer.writeheader()
        for record in result["requirement_records"]:
            writer.writerow(
                {
                    "requirement_id": record["requirement_id"],
                    "status": record["status"],
                    "evidence": json.dumps(record["evidence"], sort_keys=True),
                }
            )
    return paths


def print_stage179_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"disposition: {result['disposition']}")
    print(f"blockers: {', '.join(result['blockers'])}")
    print(f"next_gate: {result['next_gate']}")
