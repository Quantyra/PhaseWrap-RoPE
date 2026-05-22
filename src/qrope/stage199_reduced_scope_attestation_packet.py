from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from qrope.stage196_replacement_cost_estimate_packet import IBM_DOC_USD_PER_QUANTUM_SECOND_EXAMPLE
from qrope.stage198_reduced_scope_preregistration import DEFAULT_OUTPUT_DIR as STAGE198_OUTPUT_DIR
from qrope.stage99_matched_fixed_width_encoding_packet_freezer import OBJECTIVE


STAGE199_SCHEMA_VERSION = "qrope_stage199_reduced_scope_attestation_packet_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE198_RESULTS = STAGE198_OUTPUT_DIR / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage199_reduced_scope_attestation_packet"
STAGE198_READY = "REDUCED_SCOPE_PREREGISTERED_READY_FOR_COST_ATTESTATION_REVIEW"
SCENARIO_MICROSECONDS_PER_SHOT: tuple[float, ...] = (5.0, 10.0, 11.9, 25.0, 50.0, 100.0)


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _scenario(total_shots: int, budget_cap_usd: float, microseconds_per_shot: float) -> dict[str, Any]:
    quantum_seconds = total_shots * microseconds_per_shot / 1_000_000.0
    estimated_usd = quantum_seconds * IBM_DOC_USD_PER_QUANTUM_SECOND_EXAMPLE
    return {
        "microseconds_per_shot": microseconds_per_shot,
        "estimated_quantum_seconds": quantum_seconds,
        "estimated_usd": estimated_usd,
        "within_budget_cap": estimated_usd <= budget_cap_usd,
    }


def _attestation_item(item_id: str, status: str, description: str, evidence: Any) -> dict[str, Any]:
    return {"item_id": item_id, "status": status, "description": description, "evidence": evidence}


def run_stage199_reduced_scope_attestation_packet(
    *,
    stage198_results_path: Path = DEFAULT_STAGE198_RESULTS,
    budget_cap_usd: float = 25.0,
    human_credit_allowance_verified: bool = False,
) -> dict[str, Any]:
    stage198 = _load_json(stage198_results_path)
    missing_sources = [] if isinstance(stage198, dict) else [str(stage198_results_path.as_posix())]
    stage198_ready = bool(isinstance(stage198, dict) and stage198.get("decision") == STAGE198_READY)
    scope = stage198.get("selected_scope", {}) if isinstance(stage198, dict) else {}
    boundary = stage198.get("interpretation_boundary", {}) if isinstance(stage198, dict) else {}
    total_jobs = int(scope.get("estimated_total_job_count") or 0)
    total_shots = int(scope.get("estimated_total_shots") or 0)
    shots_per_row = int(scope.get("shots_per_row") or 0)
    budget_quantum_seconds = budget_cap_usd / IBM_DOC_USD_PER_QUANTUM_SECOND_EXAMPLE if budget_cap_usd > 0 else 0.0
    break_even_microseconds_per_shot = (budget_quantum_seconds / total_shots) * 1_000_000.0 if total_shots > 0 else 0.0
    scenarios = [_scenario(total_shots, budget_cap_usd, value) for value in SCENARIO_MICROSECONDS_PER_SHOT]
    attestation_prompt = (
        "Please verify in IBM that the selected instance has enough remaining credit/billing/Runtime allowance for the "
        f"reduced-scope run `{scope.get('scope_id')}`: {total_jobs} row-level jobs, {total_shots} total shots, "
        f"{shots_per_row} shots per packet row, and a ${budget_cap_usd:.2f} local cap. Using IBM's documented "
        f"$1600/1000-quantum-second example, this cap allows {budget_quantum_seconds:.3f} quantum seconds, so this "
        f"reduced run fits only if effective quantum time is <= {break_even_microseconds_per_shot:.2f} microseconds/shot. "
        "If you attest yes, you are attesting account-side allowance and willingness to spend within this cap only; "
        "this still does not approve live submission or accept the exact approval phrase."
    )
    attestation_items = [
        _attestation_item(
            "reduced_scope_preregistration",
            "ready" if stage198_ready else "blocked",
            "Stage198 must preregister the reduced-scope claim boundary before credit attestation.",
            {"stage198_decision": stage198.get("decision") if isinstance(stage198, dict) else None, "scope_id": scope.get("scope_id")},
        ),
        _attestation_item(
            "reduced_cost_estimate",
            "ready_for_user_review" if total_shots and budget_cap_usd > 0 else "missing",
            "Manual attestation must include an explicit reduced-scope cost estimate.",
            {
                "estimated_total_job_count": total_jobs,
                "estimated_total_shots": total_shots,
                "budget_cap_usd": budget_cap_usd,
                "break_even_microseconds_per_shot": break_even_microseconds_per_shot,
                "scenarios": scenarios,
            },
        ),
        _attestation_item(
            "interpretation_boundary",
            "reduced_precision_boundary_attached" if isinstance(boundary, dict) and boundary else "missing",
            "User attestation does not change the preregistered reduced-precision interpretation boundary.",
            {"hardware_scope_label": boundary.get("hardware_scope_label"), "lower_precision_caveat": boundary.get("pass_fail_policy", {}).get("lower_precision_caveat")},
        ),
        _attestation_item(
            "human_credit_allowance",
            "human_verified" if human_credit_allowance_verified else "awaiting_user_attestation",
            "This gate can record whether the user has verified IBM credit/billing/Runtime allowance, but it never approves live execution.",
            {"human_credit_allowance_verified": human_credit_allowance_verified},
        ),
        _attestation_item(
            "live_execution_boundary",
            "live_run_disallowed",
            "Exact approval phrase and live-runner preparation remain later gates even after credit attestation.",
            {"exact_approval_accepted_here": False, "hardware_submitted_here": False},
        ),
    ]
    blockers: list[str] = []
    if missing_sources:
        blockers.append("source_artifacts_missing")
    if not stage198_ready:
        blockers.append("stage198_reduced_scope_not_preregistered")
    if total_shots <= 0 or total_jobs <= 0:
        blockers.append("reduced_scope_exposure_missing")
    if not human_credit_allowance_verified:
        blockers.append("human_credit_allowance_attestation_required")
    if missing_sources:
        decision = "REDUCED_SCOPE_ATTESTATION_PACKET_INCOMPLETE"
    elif any(blocker for blocker in blockers if blocker != "human_credit_allowance_attestation_required"):
        decision = "REDUCED_SCOPE_ATTESTATION_PACKET_BLOCKED"
    elif human_credit_allowance_verified:
        decision = "REDUCED_SCOPE_CREDIT_ATTESTED_READY_FOR_EXACT_APPROVAL_REVIEW"
    else:
        decision = "REDUCED_SCOPE_ATTESTATION_READY_FOR_USER_REVIEW_NOT_LIVE"
    return {
        "schema_version": STAGE199_SCHEMA_VERSION,
        "stage": "stage199_reduced_scope_attestation_packet",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": decision,
        "source_artifacts": [str(stage198_results_path.as_posix())],
        "missing_source_artifacts": missing_sources,
        "blockers": sorted(set(blockers)),
        "scope_id": scope.get("scope_id"),
        "hardware_scope_label": boundary.get("hardware_scope_label"),
        "estimated_total_job_count": total_jobs,
        "estimated_total_shots": total_shots,
        "shots_per_row": shots_per_row,
        "budget_cap_usd": budget_cap_usd,
        "ibm_doc_usd_per_quantum_second_example": IBM_DOC_USD_PER_QUANTUM_SECOND_EXAMPLE,
        "budget_quantum_seconds_at_doc_rate": budget_quantum_seconds,
        "break_even_microseconds_per_shot": break_even_microseconds_per_shot,
        "scenario_estimates": scenarios,
        "human_credit_allowance_verified": human_credit_allowance_verified,
        "manual_attestation_prompt_required": not human_credit_allowance_verified,
        "manual_attestation_prompt": attestation_prompt,
        "attestation_items": attestation_items,
        "interpretation_boundary": boundary,
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "runnable_commands_recorded": False,
        "explicit_user_approval_required": True,
        "claim_boundary": {
            "supported": [
                "explicit reduced-scope credit attestation prompt with cost estimate",
                "reduced-scope exposure and interpretation boundary are attached before asking the user",
                "credit attestation remains separate from exact approval and live-runner preparation",
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
            "Present this reduced-scope estimate to the user. If the user attests IBM credit allowance and willingness to spend "
            "within the cap, rerun Stage199 with human_credit_allowance_verified=true, then run exact approval review."
        ),
    }


def write_stage199_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
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
        "shots_per_row",
        "budget_cap_usd",
        "ibm_doc_usd_per_quantum_second_example",
        "budget_quantum_seconds_at_doc_rate",
        "break_even_microseconds_per_shot",
        "human_credit_allowance_verified",
        "manual_attestation_prompt_required",
        "manual_attestation_prompt",
        "no_hardware_submission",
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
    manifest["scenarios_csv_path"] = str((output_dir / "scenarios.csv").as_posix())
    paths = {
        "manifest": str(output_dir / "manifest.json"),
        "result": str(output_dir / "results.json"),
        "summary_csv": str(output_dir / "summary.csv"),
        "scenarios_csv": str(output_dir / "scenarios.csv"),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=("item_id", "status", "description"))
        writer.writeheader()
        for item in result["attestation_items"]:
            writer.writerow({field: item.get(field) for field in writer.fieldnames})
    with (output_dir / "scenarios.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=("microseconds_per_shot", "estimated_quantum_seconds", "estimated_usd", "within_budget_cap"))
        writer.writeheader()
        for scenario in result["scenario_estimates"]:
            writer.writerow({field: scenario.get(field) for field in writer.fieldnames})
    return paths


def print_stage199_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"scope_id: {result['scope_id']}")
    print(f"estimated_total_job_count: {result['estimated_total_job_count']}")
    print(f"estimated_total_shots: {result['estimated_total_shots']}")
    print(f"budget_cap_usd: {result['budget_cap_usd']}")
    print(f"break_even_microseconds_per_shot: {result['break_even_microseconds_per_shot']}")
    print(f"human_credit_allowance_verified: {result['human_credit_allowance_verified']}")
    print(f"blockers: {', '.join(result['blockers'])}")
    print(f"next_gate: {result['next_gate']}")
