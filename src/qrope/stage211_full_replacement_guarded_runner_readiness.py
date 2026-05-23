from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from qrope.stage190_replacement_execution_package import DEFAULT_OUTPUT_DIR as STAGE190_OUTPUT_DIR
from qrope.stage195_replacement_exact_approval_review import STAGE194_CREDIT_VERIFIED as _STAGE195_STAGE194_READY
from qrope.stage99_matched_fixed_width_encoding_packet_freezer import OBJECTIVE


STAGE211_SCHEMA_VERSION = "qrope_stage211_full_replacement_guarded_runner_readiness_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE190_RESULTS = STAGE190_OUTPUT_DIR / "results.json"
DEFAULT_STAGE193_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage193_replacement_read_only_backend_refresh_full4096_250usd" / "results.json"
DEFAULT_STAGE194_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage194_replacement_credit_allowance_decision_packet_full4096_250usd_attested" / "results.json"
DEFAULT_STAGE195_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage195_replacement_exact_approval_review_full4096_250usd_approved" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage211_full_replacement_guarded_runner_readiness_250usd"
STAGE190_READY = "REPLACEMENT_EXECUTION_PACKAGE_PREPARED_COUNTS_AND_CALIBRATION_REQUIRED"
STAGE193_READY = "REPLACEMENT_READ_ONLY_BACKEND_REFRESH_READY_CREDIT_AND_APPROVAL_STILL_REQUIRED"
STAGE194_CREDIT_VERIFIED = "REPLACEMENT_CREDIT_ALLOWANCE_VERIFIED_READY_FOR_EXACT_APPROVAL_REVIEW"
STAGE195_APPROVED = "REPLACEMENT_EXACT_APPROVAL_ACCEPTED_READY_FOR_LIVE_RUNNER_PREPARATION_REVIEW"


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _item(item_id: str, status: str, description: str, evidence: Any) -> dict[str, Any]:
    return {"item_id": item_id, "status": status, "description": description, "evidence": evidence}


def _estimated_total_shots(stage190: dict[str, Any] | None) -> int | None:
    if not isinstance(stage190, dict):
        return None
    recorded = stage190.get("estimated_total_shots")
    if recorded is not None:
        return int(recorded)
    packet_shots = sum(
        int(template.get("shot_count") or 0) * len(template.get("raw_counts_by_row", []))
        for template in stage190.get("execution_templates", [])
        if isinstance(template, dict)
    )
    calibration = stage190.get("calibration_template", {})
    calibration_shots = int(calibration.get("shots_per_state") or 0) * len(calibration.get("raw_counts_by_state", [])) if isinstance(calibration, dict) else 0
    return packet_shots + calibration_shots if packet_shots or calibration_shots else None


def run_stage211_full_replacement_guarded_runner_readiness(
    *,
    stage190_results_path: Path = DEFAULT_STAGE190_RESULTS,
    stage193_results_path: Path = DEFAULT_STAGE193_RESULTS,
    stage194_results_path: Path = DEFAULT_STAGE194_RESULTS,
    stage195_results_path: Path = DEFAULT_STAGE195_RESULTS,
) -> dict[str, Any]:
    stage190 = _load_json(stage190_results_path)
    stage193 = _load_json(stage193_results_path)
    stage194 = _load_json(stage194_results_path)
    stage195 = _load_json(stage195_results_path)
    sources = [
        (stage190_results_path, stage190),
        (stage193_results_path, stage193),
        (stage194_results_path, stage194),
        (stage195_results_path, stage195),
    ]
    missing_sources = [str(path.as_posix()) for path, payload in sources if not isinstance(payload, dict)]
    blockers: list[str] = []
    if missing_sources:
        blockers.append("source_artifacts_missing")
    stage190_ready = bool(isinstance(stage190, dict) and stage190.get("decision") == STAGE190_READY)
    stage193_ready = bool(
        isinstance(stage193, dict)
        and stage193.get("decision") == STAGE193_READY
        and stage193.get("backend_lookup_ready") is True
    )
    stage194_ready = bool(
        isinstance(stage194, dict)
        and stage194.get("decision") == STAGE194_CREDIT_VERIFIED
        and stage194.get("human_credit_allowance_verified") is True
        and float(stage194.get("budget_cap_usd") or 0.0) >= 250.0
    )
    stage195_ready = bool(
        isinstance(stage195, dict)
        and stage195.get("decision") == STAGE195_APPROVED
        and stage195.get("approval_phrase_matches") is True
        and stage195.get("stage194_decision") == _STAGE195_STAGE194_READY
    )
    backend_metadata = stage193.get("backend_metadata", {}) if isinstance(stage193, dict) else {}
    backend = backend_metadata.get("backend")
    estimated_total_shots = _estimated_total_shots(stage190)
    package_contract_ready = bool(
        isinstance(stage190, dict)
        and stage190.get("packet_template_count") == 20
        and stage190.get("calibration_template_count") == 1
        and stage190.get("estimated_packet_row_job_count") == 320
        and stage190.get("estimated_calibration_job_count") == 4
        and stage190.get("estimated_total_job_count") == 324
        and estimated_total_shots == 1314720
        and stage190.get("no_hardware_submission") is True
    )
    if not stage190_ready:
        blockers.append("stage190_full_replacement_package_not_ready")
    if not package_contract_ready:
        blockers.append("stage190_full_replacement_contract_mismatch")
    if not stage193_ready:
        blockers.append("fresh_read_only_backend_refresh_not_ready")
    if not backend:
        blockers.append("backend_missing")
    if not stage194_ready:
        blockers.append("stage194_credit_attestation_not_ready")
    if not stage195_ready:
        blockers.append("stage195_exact_approval_not_ready")

    readiness_items = [
        _item(
            "stage190_full_replacement_package",
            "ready" if stage190_ready and package_contract_ready else "blocked",
            "The full replacement execution package must match the 4096-shot, 324-row-evidence, 1314720-shot contract.",
            {
                "stage190_decision": stage190.get("decision") if isinstance(stage190, dict) else None,
                "packet_template_count": stage190.get("packet_template_count") if isinstance(stage190, dict) else None,
                "estimated_total_job_count": stage190.get("estimated_total_job_count") if isinstance(stage190, dict) else None,
                "estimated_total_shots": estimated_total_shots,
            },
        ),
        _item(
            "fresh_read_only_backend_refresh",
            "ready" if stage193_ready and backend else "blocked",
            "A fresh read-only backend refresh must succeed before final guarded execution.",
            {
                "stage193_decision": stage193.get("decision") if isinstance(stage193, dict) else None,
                "backend": backend,
                "operational": backend_metadata.get("operational"),
                "pending_jobs": backend_metadata.get("pending_jobs"),
            },
        ),
        _item(
            "credit_attestation",
            "ready" if stage194_ready else "blocked",
            "The user-attested $250 credit/cost cap must be recorded before exact live approval is accepted.",
            {
                "stage194_decision": stage194.get("decision") if isinstance(stage194, dict) else None,
                "budget_cap_usd": stage194.get("budget_cap_usd") if isinstance(stage194, dict) else None,
                "human_credit_allowance_verified": stage194.get("human_credit_allowance_verified") if isinstance(stage194, dict) else None,
            },
        ),
        _item(
            "exact_live_approval",
            "ready" if stage195_ready else "blocked",
            "The exact live approval phrase must be accepted before the final guarded runner may submit.",
            {
                "stage195_decision": stage195.get("decision") if isinstance(stage195, dict) else None,
                "approval_phrase_matches": stage195.get("approval_phrase_matches") if isinstance(stage195, dict) else None,
            },
        ),
    ]
    ready = not blockers
    return {
        "schema_version": STAGE211_SCHEMA_VERSION,
        "stage": "stage211_full_replacement_guarded_runner_readiness",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": "FULL_REPLACEMENT_GUARDED_RUNNER_READY_FOR_FINAL_EXECUTION_STEP_NOT_LIVE" if ready else "FULL_REPLACEMENT_GUARDED_RUNNER_READINESS_BLOCKED",
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "blockers": sorted(set(blockers)),
        "backend": backend,
        "fresh_backend_metadata": backend_metadata,
        "budget_cap_usd": stage194.get("budget_cap_usd") if isinstance(stage194, dict) else None,
        "estimated_total_job_count": stage190.get("estimated_total_job_count") if isinstance(stage190, dict) else None,
        "estimated_total_shots": estimated_total_shots,
        "packet_template_count": stage190.get("packet_template_count") if isinstance(stage190, dict) else None,
        "calibration_template_count": stage190.get("calibration_template_count") if isinstance(stage190, dict) else None,
        "stage190_ready": stage190_ready,
        "package_contract_ready": package_contract_ready,
        "fresh_backend_ready": stage193_ready,
        "stage194_credit_attestation_ready": stage194_ready,
        "stage195_exact_approval_ready": stage195_ready,
        "readiness_items": readiness_items,
        "no_hardware_submission": True,
        "live_submit_command_created": False,
        "provider_credentials_required": True,
        "secret_values_recorded": False,
        "runnable_commands_recorded": False,
        "explicit_user_approval_recorded": ready,
        "claim_boundary": {
            "supported": [
                "full 4096-shot replacement package, fresh backend metadata, credit attestation, and exact approval are bound before final execution",
                "no-submit readiness is separated from live hardware execution and result interpretation",
            ],
            "excluded": [
                "hardware job submission",
                "creation or recording of a runnable live-submit command",
                "provider-side result retrieval",
                "calibration pass/fail or robustness interpretation",
            ],
        },
        "next_gate": "Run the final guarded full replacement execution step only from this ready state.",
    }


def write_stage211_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_keys = (
        "schema_version", "stage", "status", "objective", "decision", "source_artifacts",
        "missing_source_artifacts", "blockers", "backend", "fresh_backend_metadata", "budget_cap_usd",
        "estimated_total_job_count", "estimated_total_shots", "packet_template_count",
        "calibration_template_count", "stage190_ready", "package_contract_ready", "fresh_backend_ready",
        "stage194_credit_attestation_ready", "stage195_exact_approval_ready", "no_hardware_submission",
        "live_submit_command_created", "provider_credentials_required", "secret_values_recorded",
        "runnable_commands_recorded", "explicit_user_approval_recorded", "claim_boundary", "next_gate",
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
        for item in result["readiness_items"]:
            writer.writerow({field: item.get(field) for field in writer.fieldnames})
    return paths


def print_stage211_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"backend: {result['backend']}")
    print(f"budget_cap_usd: {result['budget_cap_usd']}")
    print(f"estimated_total_shots: {result['estimated_total_shots']}")
    print(f"blockers: {', '.join(result['blockers'])}")
    print(f"next_gate: {result['next_gate']}")
