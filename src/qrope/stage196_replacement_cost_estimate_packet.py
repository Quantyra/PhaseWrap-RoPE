from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from qrope.stage194_replacement_credit_allowance_decision_packet import DEFAULT_OUTPUT_DIR as STAGE194_OUTPUT_DIR
from qrope.stage99_matched_fixed_width_encoding_packet_freezer import OBJECTIVE


STAGE196_SCHEMA_VERSION = "qrope_stage196_replacement_cost_estimate_packet_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE194_RESULTS = STAGE194_OUTPUT_DIR / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage196_replacement_cost_estimate_packet"
IBM_DOC_QUANTUM_SECONDS_PER_1000_USD_EXAMPLE = 1000.0 / 1600.0
IBM_DOC_USD_PER_QUANTUM_SECOND_EXAMPLE = 1600.0 / 1000.0
SCENARIO_MICROSECONDS_PER_SHOT: tuple[float, ...] = (5.0, 10.0, 11.9, 25.0, 50.0, 100.0)


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _scenario_record(microseconds_per_shot: float, total_shots: int, budget_cap_usd: float) -> dict[str, Any]:
    quantum_seconds = total_shots * microseconds_per_shot / 1_000_000.0
    estimated_usd = quantum_seconds * IBM_DOC_USD_PER_QUANTUM_SECOND_EXAMPLE
    return {
        "microseconds_per_shot": microseconds_per_shot,
        "estimated_quantum_seconds": quantum_seconds,
        "estimated_usd": estimated_usd,
        "within_budget_cap": estimated_usd <= budget_cap_usd,
    }


def _estimate_item(item_id: str, status: str, description: str, evidence: Any) -> dict[str, Any]:
    return {"item_id": item_id, "status": status, "description": description, "evidence": evidence}


def run_stage196_replacement_cost_estimate_packet(
    *,
    stage194_results_path: Path = DEFAULT_STAGE194_RESULTS,
) -> dict[str, Any]:
    stage194 = _load_json(stage194_results_path)
    missing_sources = [] if isinstance(stage194, dict) else [str(stage194_results_path.as_posix())]
    total_shots = int(stage194.get("estimated_total_shots") or 0) if isinstance(stage194, dict) else 0
    total_jobs = int(stage194.get("estimated_total_job_count") or 0) if isinstance(stage194, dict) else 0
    budget_cap_usd = float(stage194.get("budget_cap_usd") or 0.0) if isinstance(stage194, dict) else 0.0
    budget_quantum_seconds = budget_cap_usd * IBM_DOC_QUANTUM_SECONDS_PER_1000_USD_EXAMPLE if budget_cap_usd > 0 else 0.0
    break_even_microseconds_per_shot = (budget_quantum_seconds / total_shots) * 1_000_000.0 if total_shots > 0 else 0.0
    scenarios = [_scenario_record(value, total_shots, budget_cap_usd) for value in SCENARIO_MICROSECONDS_PER_SHOT]
    conservative_scenarios_over_budget = [record for record in scenarios if record["microseconds_per_shot"] >= 25.0 and not record["within_budget_cap"]]
    optimistic_margin_record = next((record for record in scenarios if record["microseconds_per_shot"] == 10.0), None)
    estimate_items = [
        _estimate_item(
            "replacement_exposure",
            "recorded" if total_shots and total_jobs else "missing",
            "Replacement workload exposure must be known before manual credit attestation.",
            {"estimated_total_job_count": total_jobs, "estimated_total_shots": total_shots},
        ),
        _estimate_item(
            "local_budget_cap",
            "recorded" if budget_cap_usd > 0 else "missing",
            "Local budget cap bounds the requested manual attestation.",
            {"budget_cap_usd": budget_cap_usd, "budget_quantum_seconds_at_doc_rate": budget_quantum_seconds},
        ),
        _estimate_item(
            "break_even_quantum_time",
            "tight_budget" if 0 < break_even_microseconds_per_shot < 25.0 else "unbounded_or_missing",
            "The full run fits the local cap only if effective quantum time per shot is below this break-even value.",
            {"break_even_microseconds_per_shot": break_even_microseconds_per_shot},
        ),
        _estimate_item(
            "scenario_estimates",
            "mixed" if optimistic_margin_record and optimistic_margin_record["within_budget_cap"] and conservative_scenarios_over_budget else "review_required",
            "Scenario estimates use IBM's documented quantum-second cost example and do not include provider-side overhead unknowns.",
            {"scenarios": scenarios},
        ),
        _estimate_item(
            "attestation_request_state",
            "do_not_request_attestation_until_user_reviews_estimate",
            "Manual credit attestation must cite this estimate and must not be requested as a blank credit check.",
            {"cost_estimate_ready_for_review": True},
        ),
    ]
    blockers = []
    if missing_sources:
        blockers.append("source_artifacts_missing")
    if total_shots <= 0 or total_jobs <= 0:
        blockers.append("replacement_exposure_missing")
    if budget_cap_usd <= 0:
        blockers.append("local_budget_cap_missing")
    if break_even_microseconds_per_shot > 0 and break_even_microseconds_per_shot < 25.0:
        blockers.append("budget_likely_tight_for_full_run")
    if missing_sources:
        decision = "REPLACEMENT_COST_ESTIMATE_PACKET_INCOMPLETE"
    elif "replacement_exposure_missing" in blockers or "local_budget_cap_missing" in blockers:
        decision = "REPLACEMENT_COST_ESTIMATE_PACKET_BLOCKED"
    else:
        decision = "REPLACEMENT_COST_ESTIMATE_READY_BUDGET_LIKELY_TIGHT_NOT_LIVE"
    return {
        "schema_version": STAGE196_SCHEMA_VERSION,
        "stage": "stage196_replacement_cost_estimate_packet",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": decision,
        "source_artifacts": [str(stage194_results_path.as_posix())],
        "missing_source_artifacts": missing_sources,
        "blockers": sorted(set(blockers)),
        "estimated_total_job_count": total_jobs,
        "estimated_total_shots": total_shots,
        "budget_cap_usd": budget_cap_usd,
        "ibm_doc_usd_per_quantum_second_example": IBM_DOC_USD_PER_QUANTUM_SECOND_EXAMPLE,
        "budget_quantum_seconds_at_doc_rate": budget_quantum_seconds,
        "break_even_microseconds_per_shot": break_even_microseconds_per_shot,
        "scenario_estimates": scenarios,
        "cost_posture": (
            "not_over_budget_if_effective_quantum_time_is_below_break_even_but_likely_tight_for_full_run"
            if break_even_microseconds_per_shot > 0
            else "unknown"
        ),
        "manual_attestation_prompt_required": True,
        "manual_attestation_prompt": (
            "Please verify in IBM that the selected instance has enough remaining credit/billing/Runtime allowance for a run "
            f"estimated at {total_jobs} row-level jobs and {total_shots} shots. Using IBM's documented $1600/1000-quantum-second "
            f"example, the local ${budget_cap_usd:.2f} cap allows about {budget_quantum_seconds:.3f} quantum seconds, so the "
            f"full run fits only if effective quantum time is <= {break_even_microseconds_per_shot:.2f} microseconds/shot. "
            "If you attest yes, you are attesting IBM account allowance and willingness to spend within the local cap; this "
            "still does not approve live submission."
        ),
        "estimate_items": estimate_items,
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "runnable_commands_recorded": False,
        "explicit_user_approval_required": True,
        "claim_boundary": {
            "supported": [
                "explicit pre-attestation cost estimate using IBM's documented quantum-second cost example",
                "break-even quantum-time-per-shot threshold for the local budget cap",
                "scenario estimates that show whether the full replacement run is budget-tight",
            ],
            "excluded": [
                "hardware job submission",
                "provider credentials, token values, CRN values, or account secrets",
                "provider-side IBM credit balance verification",
                "actual quantum_seconds from completed jobs",
                "acceptance of credit attestation or exact live-run approval",
                "a noisy-hardware robustness or auditability conclusion",
            ],
        },
        "source_notes": [
            "IBM docs describe Standard Plan cost limits in USD converted to runtime seconds and give 1000 seconds as $1600.",
            "IBM docs state quantum time, not wall-clock time, drives max execution time/cost behavior for QPU jobs.",
            "IBM docs state quantum time and cost scale with shots.",
        ],
        "source_urls": [
            "https://docs.quantum.ibm.com/guides/manage-cost",
            "https://docs.quantum.ibm.com/guides/max-execution-time",
            "https://docs.quantum.ibm.com/guides/minimize-time",
        ],
        "next_gate": (
            "Present this estimate to the user before credit attestation. If the user attests IBM allowance despite the tight "
            "budget posture, rerun Stage194 with human_credit_allowance_verified=true; otherwise reduce run scope or raise the cap."
        ),
    }


def write_stage196_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
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
        "estimated_total_job_count",
        "estimated_total_shots",
        "budget_cap_usd",
        "ibm_doc_usd_per_quantum_second_example",
        "budget_quantum_seconds_at_doc_rate",
        "break_even_microseconds_per_shot",
        "cost_posture",
        "manual_attestation_prompt_required",
        "no_hardware_submission",
        "provider_credentials_required",
        "secret_values_recorded",
        "runnable_commands_recorded",
        "explicit_user_approval_required",
        "claim_boundary",
        "source_notes",
        "source_urls",
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
        for item in result["estimate_items"]:
            writer.writerow({field: item.get(field) for field in writer.fieldnames})
    with (output_dir / "scenarios.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=("microseconds_per_shot", "estimated_quantum_seconds", "estimated_usd", "within_budget_cap"))
        writer.writeheader()
        for scenario in result["scenario_estimates"]:
            writer.writerow({field: scenario.get(field) for field in writer.fieldnames})
    return paths


def print_stage196_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"estimated_total_job_count: {result['estimated_total_job_count']}")
    print(f"estimated_total_shots: {result['estimated_total_shots']}")
    print(f"budget_cap_usd: {result['budget_cap_usd']}")
    print(f"budget_quantum_seconds_at_doc_rate: {result['budget_quantum_seconds_at_doc_rate']}")
    print(f"break_even_microseconds_per_shot: {result['break_even_microseconds_per_shot']}")
    print(f"cost_posture: {result['cost_posture']}")
    print(f"blockers: {', '.join(result['blockers'])}")
    print(f"next_gate: {result['next_gate']}")
