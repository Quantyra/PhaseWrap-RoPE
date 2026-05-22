from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from qrope.stage199_reduced_scope_attestation_packet import DEFAULT_OUTPUT_DIR as STAGE199_OUTPUT_DIR
from qrope.stage99_matched_fixed_width_encoding_packet_freezer import OBJECTIVE


STAGE200_SCHEMA_VERSION = "qrope_stage200_reduced_scope_attestation_intake_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE199_RESULTS = STAGE199_OUTPUT_DIR / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage200_reduced_scope_attestation_intake"
STAGE199_READY = "REDUCED_SCOPE_ATTESTATION_READY_FOR_USER_REVIEW_NOT_LIVE"
REQUIRED_ATTESTATION_PHRASE = "ATTEST IBM CREDIT FOR REDUCED SCOPE STAGE199 WITH 25 USD CAP"


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _item(item_id: str, status: str, description: str, evidence: Any) -> dict[str, Any]:
    return {"item_id": item_id, "status": status, "description": description, "evidence": evidence}


def required_attestation_phrase_for_budget(budget_cap_usd: float | int | None) -> str:
    if budget_cap_usd is None:
        return REQUIRED_ATTESTATION_PHRASE
    cap = float(budget_cap_usd)
    cap_text = str(int(cap)) if cap.is_integer() else f"{cap:.2f}".rstrip("0").rstrip(".")
    return f"ATTEST IBM CREDIT FOR REDUCED SCOPE STAGE199 WITH {cap_text} USD CAP"


def run_stage200_reduced_scope_attestation_intake(
    *,
    stage199_results_path: Path = DEFAULT_STAGE199_RESULTS,
    provided_attestation_phrase: str | None = None,
) -> dict[str, Any]:
    stage199 = _load_json(stage199_results_path)
    missing_sources = [] if isinstance(stage199, dict) else [str(stage199_results_path.as_posix())]
    stage199_ready = bool(isinstance(stage199, dict) and stage199.get("decision") == STAGE199_READY)
    budget_cap_usd = stage199.get("budget_cap_usd") if isinstance(stage199, dict) else None
    required_attestation_phrase = required_attestation_phrase_for_budget(budget_cap_usd)
    phrase_present = provided_attestation_phrase is not None
    phrase_matches = provided_attestation_phrase == required_attestation_phrase
    intake_items = [
        _item(
            "stage199_attestation_packet",
            "ready" if stage199_ready else "blocked",
            "Stage199 must present the reduced-scope cost estimate before any attestation phrase can be accepted.",
            {
                "stage199_decision": stage199.get("decision") if isinstance(stage199, dict) else None,
                "scope_id": stage199.get("scope_id") if isinstance(stage199, dict) else None,
                "estimated_total_shots": stage199.get("estimated_total_shots") if isinstance(stage199, dict) else None,
                "break_even_microseconds_per_shot": stage199.get("break_even_microseconds_per_shot") if isinstance(stage199, dict) else None,
            },
        ),
        _item(
            "exact_attestation_phrase",
            "accepted" if stage199_ready and phrase_matches else "awaiting_exact_phrase" if not phrase_present else "mismatched",
            "Only the exact reduced-scope credit attestation phrase can record human credit allowance verification.",
            {
                "required_attestation_phrase": required_attestation_phrase,
                "provided_attestation_phrase_present": phrase_present,
                "attestation_phrase_matches": phrase_matches if stage199_ready else False,
            },
        ),
        _item(
            "attestation_meaning",
            "bounded_credit_attestation_only",
            "Accepted attestation means IBM account allowance and willingness to spend within the reduced-scope cap only.",
            {
                "scope_id": stage199.get("scope_id") if isinstance(stage199, dict) else None,
                "budget_cap_usd": stage199.get("budget_cap_usd") if isinstance(stage199, dict) else None,
                "does_not_approve_live_submission": True,
                "does_not_accept_exact_live_approval_phrase": True,
            },
        ),
        _item(
            "live_execution_boundary",
            "live_run_disallowed",
            "This gate never prepares or runs hardware; exact live approval remains a later separate gate.",
            {"hardware_submitted_here": False, "live_submit_command_created_here": False},
        ),
    ]
    blockers: list[str] = []
    if missing_sources:
        blockers.append("source_artifacts_missing")
    if not stage199_ready:
        blockers.append("stage199_attestation_packet_not_ready")
    if not phrase_matches:
        blockers.append("exact_reduced_scope_attestation_phrase_required")
    if missing_sources:
        decision = "REDUCED_SCOPE_ATTESTATION_INTAKE_INCOMPLETE"
    elif stage199_ready and phrase_matches:
        decision = "REDUCED_SCOPE_CREDIT_ATTESTATION_ACCEPTED_READY_FOR_EXACT_APPROVAL_REVIEW"
    else:
        decision = "REDUCED_SCOPE_ATTESTATION_INTAKE_AWAITING_EXACT_PHRASE"
    return {
        "schema_version": STAGE200_SCHEMA_VERSION,
        "stage": "stage200_reduced_scope_attestation_intake",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": decision,
        "source_artifacts": [str(stage199_results_path.as_posix())],
        "missing_source_artifacts": missing_sources,
        "blockers": sorted(set(blockers)),
        "scope_id": stage199.get("scope_id") if isinstance(stage199, dict) else None,
        "hardware_scope_label": stage199.get("hardware_scope_label") if isinstance(stage199, dict) else None,
        "estimated_total_job_count": stage199.get("estimated_total_job_count") if isinstance(stage199, dict) else None,
        "estimated_total_shots": stage199.get("estimated_total_shots") if isinstance(stage199, dict) else None,
        "budget_cap_usd": budget_cap_usd,
        "break_even_microseconds_per_shot": stage199.get("break_even_microseconds_per_shot") if isinstance(stage199, dict) else None,
        "required_attestation_phrase": required_attestation_phrase,
        "provided_attestation_phrase_present": phrase_present,
        "attestation_phrase_matches": phrase_matches if stage199_ready else False,
        "human_credit_allowance_verified": stage199_ready and phrase_matches,
        "intake_items": intake_items,
        "no_hardware_submission": True,
        "live_submit_command_created": False,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "runnable_commands_recorded": False,
        "explicit_user_approval_required": True,
        "claim_boundary": {
            "supported": [
                "exact reduced-scope credit attestation phrase intake",
                "credit attestation is bounded to Stage199 reduced scope and the current recorded USD cap",
                "attestation remains separate from exact live approval and live-runner preparation",
            ],
            "excluded": [
                "hardware job submission",
                "provider-side IBM credit balance verification",
                "acceptance of exact live-run approval",
                "creation of a runnable live-submit command",
                "a noisy-hardware robustness or auditability conclusion",
            ],
        },
        "next_gate": (
            "If the exact attestation phrase is accepted, rerun Stage199 with human_credit_allowance_verified=true and then "
            "perform reduced-scope exact approval review. Do not prepare a live runner from this gate alone."
        ),
    }


def write_stage200_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
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
        "scope_id",
        "hardware_scope_label",
        "estimated_total_job_count",
        "estimated_total_shots",
        "budget_cap_usd",
        "break_even_microseconds_per_shot",
        "required_attestation_phrase",
        "provided_attestation_phrase_present",
        "attestation_phrase_matches",
        "human_credit_allowance_verified",
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
        for item in result["intake_items"]:
            writer.writerow({field: item.get(field) for field in writer.fieldnames})
    return paths


def print_stage200_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"scope_id: {result['scope_id']}")
    print(f"estimated_total_shots: {result['estimated_total_shots']}")
    print(f"budget_cap_usd: {result['budget_cap_usd']}")
    print(f"required_attestation_phrase: {result['required_attestation_phrase']}")
    print(f"provided_attestation_phrase_present: {result['provided_attestation_phrase_present']}")
    print(f"attestation_phrase_matches: {result['attestation_phrase_matches']}")
    print(f"human_credit_allowance_verified: {result['human_credit_allowance_verified']}")
    print(f"blockers: {', '.join(result['blockers'])}")
    print(f"next_gate: {result['next_gate']}")
