from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from qrope.stage176_ibm_credit_provider_resolution_handoff import DEFAULT_OUTPUT_DIR as STAGE176_OUTPUT_DIR
from qrope.stage188_replacement_semantics_packet_screen import DEFAULT_OUTPUT_DIR as STAGE188_OUTPUT_DIR
from qrope.stage189_replacement_hardware_readiness_review import (
    APPROVAL_PHRASE,
    DEFAULT_OUTPUT_DIR as STAGE189_OUTPUT_DIR,
)
from qrope.stage190_replacement_execution_package import DEFAULT_OUTPUT_DIR as STAGE190_OUTPUT_DIR
from qrope.stage99_matched_fixed_width_encoding_packet_freezer import OBJECTIVE


STAGE191_SCHEMA_VERSION = "qrope_stage191_replacement_approval_dossier_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE176_RESULTS = STAGE176_OUTPUT_DIR / "results.json"
DEFAULT_STAGE188_RESULTS = STAGE188_OUTPUT_DIR / "results.json"
DEFAULT_STAGE189_RESULTS = STAGE189_OUTPUT_DIR / "results.json"
DEFAULT_STAGE190_RESULTS = STAGE190_OUTPUT_DIR / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage191_replacement_approval_dossier"
STAGE188_SUPPORTS_REOPEN = "REPLACEMENT_SEMANTICS_SIM_SUPPORTS_HARDWARE_REOPEN"
STAGE189_REOPENED = "REPLACEMENT_HARDWARE_REVIEW_REOPENED_BUT_NOT_READY_FOR_LIVE_RUN"
STAGE190_PREPARED = "REPLACEMENT_EXECUTION_PACKAGE_PREPARED_COUNTS_AND_CALIBRATION_REQUIRED"


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _readiness_record(item_id: str, status: str, description: str, evidence: Any) -> dict[str, Any]:
    return {"item_id": item_id, "status": status, "description": description, "evidence": evidence}


def _packet_shots(stage190: dict[str, Any]) -> int:
    return sum(
        int(template.get("shot_count") or 0) * len(template.get("raw_counts_by_row", []))
        for template in stage190.get("execution_templates", [])
        if isinstance(template, dict)
    )


def _calibration_shots(stage190: dict[str, Any]) -> int:
    calibration = stage190.get("calibration_template", {}) if isinstance(stage190, dict) else {}
    return int(calibration.get("shots_per_state") or 0) * len(calibration.get("raw_counts_by_state", []))


def run_stage191_replacement_approval_dossier(
    *,
    stage176_results_path: Path = DEFAULT_STAGE176_RESULTS,
    stage188_results_path: Path = DEFAULT_STAGE188_RESULTS,
    stage189_results_path: Path = DEFAULT_STAGE189_RESULTS,
    stage190_results_path: Path = DEFAULT_STAGE190_RESULTS,
) -> dict[str, Any]:
    stage176 = _load_json(stage176_results_path)
    stage188 = _load_json(stage188_results_path)
    stage189 = _load_json(stage189_results_path)
    stage190 = _load_json(stage190_results_path)
    sources = [
        (stage176_results_path, stage176),
        (stage188_results_path, stage188),
        (stage189_results_path, stage189),
        (stage190_results_path, stage190),
    ]
    missing_sources = [str(path.as_posix()) for path, payload in sources if not isinstance(payload, dict)]
    blockers = []
    if missing_sources:
        blockers.append("missing_source_artifacts")
    if isinstance(stage188, dict) and stage188.get("decision") != STAGE188_SUPPORTS_REOPEN:
        blockers.append("stage188_replacement_sim_not_positive")
    if isinstance(stage189, dict) and stage189.get("decision") != STAGE189_REOPENED:
        blockers.append("stage189_replacement_review_not_reopened")
    if isinstance(stage190, dict) and stage190.get("decision") != STAGE190_PREPARED:
        blockers.append("stage190_execution_package_not_prepared")
    credit_verified = bool(stage176.get("credit_balance_verified")) if isinstance(stage176, dict) else False
    packet_shots = _packet_shots(stage190) if isinstance(stage190, dict) else 0
    calibration_shots = _calibration_shots(stage190) if isinstance(stage190, dict) else 0
    total_shots = packet_shots + calibration_shots
    readiness_records = [
        _readiness_record(
            "replacement_simulation_evidence",
            "passed" if isinstance(stage188, dict) and stage188.get("decision") == STAGE188_SUPPORTS_REOPEN else "blocked",
            "Replacement semantics must have a positive IBM-informed simulated screen.",
            {
                "stage188_decision": stage188.get("decision") if isinstance(stage188, dict) else None,
                "reopen_candidate_count": stage188.get("reopen_candidate_count") if isinstance(stage188, dict) else None,
            },
        ),
        _readiness_record(
            "replacement_execution_package",
            "prepared" if isinstance(stage190, dict) and stage190.get("decision") == STAGE190_PREPARED else "blocked",
            "Replacement packet and calibration templates must be prepared before approval review.",
            {
                "packet_template_count": stage190.get("packet_template_count") if isinstance(stage190, dict) else None,
                "estimated_total_job_count": stage190.get("estimated_total_job_count") if isinstance(stage190, dict) else None,
            },
        ),
        _readiness_record(
            "credit_billing_runtime_allowance",
            "human_verification_required" if not credit_verified else "verified",
            "IBM credit, billing, and Runtime allowance must be verified by the user.",
            {"credit_balance_verified": credit_verified},
        ),
        _readiness_record(
            "exact_human_approval",
            "awaiting_exact_phrase",
            "Live execution remains disallowed unless the replacement approval phrase is provided after all readiness checks.",
            {"approval_phrase_required": APPROVAL_PHRASE},
        ),
        _readiness_record(
            "post_run_interpretation_boundary",
            "counts_required",
            "No robustness/auditability interpretation is possible until calibration and packet counts are collected and ingested.",
            {"provider_result_records_present": False},
        ),
    ]
    if any(record["status"] in {"blocked", "human_verification_required", "awaiting_exact_phrase", "counts_required"} for record in readiness_records):
        blockers.append("replacement_approval_requirements_open")
    if missing_sources:
        decision = "REPLACEMENT_APPROVAL_DOSSIER_INCOMPLETE"
    elif any(record["status"] == "blocked" for record in readiness_records):
        decision = "REPLACEMENT_APPROVAL_DOSSIER_BLOCKED"
    else:
        decision = "REPLACEMENT_APPROVAL_DOSSIER_READY_FOR_HUMAN_REVIEW_NOT_LIVE"
    return {
        "schema_version": STAGE191_SCHEMA_VERSION,
        "stage": "stage191_replacement_approval_dossier",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": decision,
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "blockers": sorted(set(blockers)),
        "semantics_id": stage188.get("semantics_id") if isinstance(stage188, dict) else None,
        "selected_lanes": stage190.get("selected_lanes", []) if isinstance(stage190, dict) else [],
        "selected_lane_count": stage190.get("selected_lane_count") if isinstance(stage190, dict) else None,
        "packet_template_count": stage190.get("packet_template_count") if isinstance(stage190, dict) else None,
        "estimated_packet_row_job_count": stage190.get("estimated_packet_row_job_count") if isinstance(stage190, dict) else None,
        "estimated_calibration_job_count": stage190.get("estimated_calibration_job_count") if isinstance(stage190, dict) else None,
        "estimated_total_job_count": stage190.get("estimated_total_job_count") if isinstance(stage190, dict) else None,
        "estimated_packet_shots": packet_shots,
        "estimated_calibration_shots": calibration_shots,
        "estimated_total_shots": total_shots,
        "credit_balance_verified": credit_verified,
        "replacement_approval_phrase_required": APPROVAL_PHRASE,
        "readiness_records": readiness_records,
        "approval_state": "human_review_open_but_live_run_disallowed",
        "no_hardware_submission": True,
        "explicit_user_approval_required": True,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "runnable_commands_recorded": False,
        "claim_boundary": {
            "supported": [
                "replacement-run evidence and execution-package readiness are consolidated for human review",
                "estimated job and shot exposure is quantified before any provider action",
                "remaining credit, exact-approval, and result-count boundaries are explicit",
            ],
            "excluded": [
                "hardware job submission",
                "runnable live-submit command strings",
                "provider credentials or secret values",
                "IBM credit balance or dollar cost verification",
                "provider result records",
                "a noisy-hardware robustness or auditability conclusion",
            ],
        },
        "next_gate": (
            "Resolve IBM credit/provider allowance and exact human approval separately; only then may a live runner be prepared, "
            "and any results still require calibration/result ingestion before interpretation."
        ),
    }


def write_stage191_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
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
        "semantics_id",
        "selected_lanes",
        "selected_lane_count",
        "packet_template_count",
        "estimated_packet_row_job_count",
        "estimated_calibration_job_count",
        "estimated_total_job_count",
        "estimated_packet_shots",
        "estimated_calibration_shots",
        "estimated_total_shots",
        "credit_balance_verified",
        "replacement_approval_phrase_required",
        "approval_state",
        "no_hardware_submission",
        "explicit_user_approval_required",
        "provider_credentials_required",
        "secret_values_recorded",
        "runnable_commands_recorded",
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
        for record in result["readiness_records"]:
            writer.writerow({field: record.get(field) for field in writer.fieldnames})
    return paths


def print_stage191_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"approval_state: {result['approval_state']}")
    print(f"estimated_total_job_count: {result['estimated_total_job_count']}")
    print(f"estimated_total_shots: {result['estimated_total_shots']}")
    print(f"blockers: {', '.join(result['blockers'])}")
    print(f"next_gate: {result['next_gate']}")
