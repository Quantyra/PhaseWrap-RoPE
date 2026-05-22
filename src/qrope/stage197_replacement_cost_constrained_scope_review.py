from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from qrope.stage188_replacement_semantics_packet_screen import DEFAULT_OUTPUT_DIR as STAGE188_OUTPUT_DIR
from qrope.stage196_replacement_cost_estimate_packet import (
    DEFAULT_OUTPUT_DIR as STAGE196_OUTPUT_DIR,
    IBM_DOC_USD_PER_QUANTUM_SECOND_EXAMPLE,
)
from qrope.stage99_matched_fixed_width_encoding_packet_freezer import OBJECTIVE


STAGE197_SCHEMA_VERSION = "qrope_stage197_replacement_cost_constrained_scope_review_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE188_RESULTS = STAGE188_OUTPUT_DIR / "results.json"
DEFAULT_STAGE196_RESULTS = STAGE196_OUTPUT_DIR / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage197_replacement_cost_constrained_scope_review"
STAGE188_POSITIVE = "REPLACEMENT_SEMANTICS_SIM_SUPPORTS_HARDWARE_REOPEN"
STAGE196_READY = "REPLACEMENT_COST_ESTIMATE_READY_BUDGET_LIKELY_TIGHT_NOT_LIVE"
REQUIRED_FAMILIES = ("phasewrap", "rope_like", "sinusoidal_like", "alibi_like", "matched_nonzero_null_control")
CALIBRATION_SHOTS = 4000


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _scenario_cost(total_shots: int, microseconds_per_shot: float) -> float:
    return total_shots * microseconds_per_shot / 1_000_000.0 * IBM_DOC_USD_PER_QUANTUM_SECOND_EXAMPLE


def _scope_record(
    *,
    scope_id: str,
    description: str,
    lane_count: int,
    row_count_per_packet: int,
    family_count: int,
    shots_per_row: int,
    calibration_shots: int,
    evidentiary_status: str,
    rationale: str,
    min_positional_margin_shot_quanta_at_4096: float,
    min_matched_null_margin_shot_quanta_at_4096: float,
) -> dict[str, Any]:
    packet_rows = lane_count * family_count * row_count_per_packet
    packet_shots = packet_rows * shots_per_row
    total_shots = packet_shots + calibration_shots
    scale = shots_per_row / 4096.0
    return {
        "scope_id": scope_id,
        "description": description,
        "lane_count": lane_count,
        "row_count_per_packet": row_count_per_packet,
        "family_count": family_count,
        "shots_per_row": shots_per_row,
        "packet_row_job_count": packet_rows,
        "calibration_job_count": 4,
        "estimated_total_job_count": packet_rows + 4,
        "estimated_packet_shots": packet_shots,
        "estimated_calibration_shots": calibration_shots,
        "estimated_total_shots": total_shots,
        "estimated_usd_at_10us_per_shot": _scenario_cost(total_shots, 10.0),
        "estimated_usd_at_50us_per_shot": _scenario_cost(total_shots, 50.0),
        "estimated_usd_at_100us_per_shot": _scenario_cost(total_shots, 100.0),
        "scaled_min_positional_margin_shot_quanta": min_positional_margin_shot_quanta_at_4096 * scale,
        "scaled_min_matched_null_margin_shot_quanta": min_matched_null_margin_shot_quanta_at_4096 * scale,
        "evidentiary_status": evidentiary_status,
        "rationale": rationale,
    }


def _ibm_candidate_records(stage188: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        record
        for record in stage188.get("candidate_records", [])
        if isinstance(record, dict) and record.get("provider_family") == "ibm" and record.get("reopen_candidate") is True
    ]


def _review_item(item_id: str, status: str, description: str, evidence: Any) -> dict[str, Any]:
    return {"item_id": item_id, "status": status, "description": description, "evidence": evidence}


def run_stage197_replacement_cost_constrained_scope_review(
    *,
    stage188_results_path: Path = DEFAULT_STAGE188_RESULTS,
    stage196_results_path: Path = DEFAULT_STAGE196_RESULTS,
) -> dict[str, Any]:
    stage188 = _load_json(stage188_results_path)
    stage196 = _load_json(stage196_results_path)
    sources = [(stage188_results_path, stage188), (stage196_results_path, stage196)]
    missing_sources = [str(path.as_posix()) for path, payload in sources if not isinstance(payload, dict)]
    stage188_positive = bool(isinstance(stage188, dict) and stage188.get("decision") == STAGE188_POSITIVE)
    stage196_ready = bool(isinstance(stage196, dict) and stage196.get("decision") == STAGE196_READY)
    budget_cap = float(stage196.get("budget_cap_usd") or 0.0) if isinstance(stage196, dict) else 0.0
    ibm_candidates = _ibm_candidate_records(stage188) if isinstance(stage188, dict) else []
    min_positional_margin = min((float(record.get("min_positional_margin_shot_quanta") or 0.0) for record in ibm_candidates), default=0.0)
    min_null_margin = min((float(record.get("min_matched_null_margin_shot_quanta") or 0.0) for record in ibm_candidates), default=0.0)
    full_scope = _scope_record(
        scope_id="full_evidentiary_scope_4096",
        description="All selected IBM lanes, all five families, all 16 rows, 4096 shots per row.",
        lane_count=4,
        row_count_per_packet=16,
        family_count=len(REQUIRED_FAMILIES),
        shots_per_row=4096,
        calibration_shots=CALIBRATION_SHOTS,
        evidentiary_status="claim_capable_if_credit_and_approval_resolved",
        rationale="Preserves both IBM seeds, both circuit templates, all comparators, full row coverage, and original Stage188 shot resolution.",
        min_positional_margin_shot_quanta_at_4096=min_positional_margin,
        min_matched_null_margin_shot_quanta_at_4096=min_null_margin,
    )
    half_scope = _scope_record(
        scope_id="all_lanes_half_shots_2048",
        description="All selected IBM lanes and families, all 16 rows, 2048 shots per row.",
        lane_count=4,
        row_count_per_packet=16,
        family_count=len(REQUIRED_FAMILIES),
        shots_per_row=2048,
        calibration_shots=CALIBRATION_SHOTS,
        evidentiary_status="borderline_claim_capable_requires_predeclared_lower_precision",
        rationale="Preserves coverage but halves shot resolution; weakest simulated positional margin falls near 2.6 shot quanta.",
        min_positional_margin_shot_quanta_at_4096=min_positional_margin,
        min_matched_null_margin_shot_quanta_at_4096=min_null_margin,
    )
    scout_scope = _scope_record(
        scope_id="all_lanes_scout_512",
        description="All selected IBM lanes and families, all 16 rows, 512 shots per row.",
        lane_count=4,
        row_count_per_packet=16,
        family_count=len(REQUIRED_FAMILIES),
        shots_per_row=512,
        calibration_shots=CALIBRATION_SHOTS,
        evidentiary_status="scouting_only_not_claim_capable",
        rationale="Preserves structure but weakens shot resolution too much for the weakest Stage188 margin; useful only to test operational viability and gross direction.",
        min_positional_margin_shot_quanta_at_4096=min_positional_margin,
        min_matched_null_margin_shot_quanta_at_4096=min_null_margin,
    )
    strong_lane_scope = _scope_record(
        scope_id="strong_seed577_lanes_4096",
        description="Only seed577 product and CX lanes, all five families, all 16 rows, 4096 shots per row.",
        lane_count=2,
        row_count_per_packet=16,
        family_count=len(REQUIRED_FAMILIES),
        shots_per_row=4096,
        calibration_shots=CALIBRATION_SHOTS,
        evidentiary_status="directional_not_full_claim_capable",
        rationale="Keeps strongest seed and both templates but drops independent seed replication; useful for de-risking before full run, not final evidence.",
        min_positional_margin_shot_quanta_at_4096=17.410303,
        min_matched_null_margin_shot_quanta_at_4096=5.006154,
    )
    scope_options = [full_scope, half_scope, scout_scope, strong_lane_scope]
    recommended = "all_lanes_half_shots_2048"
    review_items = [
        _review_item(
            "simulation_evidence",
            "positive" if stage188_positive else "blocked",
            "Reduced scope review requires the Stage188 replacement simulation to be positive.",
            {"stage188_decision": stage188.get("decision") if isinstance(stage188, dict) else None, "ibm_reopen_candidate_count": len(ibm_candidates)},
        ),
        _review_item(
            "full_run_cost_posture",
            "budget_tight" if stage196_ready else "blocked",
            "Stage196 must establish the full run cost posture before selecting a reduced scope.",
            {
                "stage196_decision": stage196.get("decision") if isinstance(stage196, dict) else None,
                "budget_cap_usd": budget_cap,
                "full_estimated_usd_at_50us": full_scope["estimated_usd_at_50us_per_shot"],
                "full_estimated_usd_at_100us": full_scope["estimated_usd_at_100us_per_shot"],
            },
        ),
        _review_item(
            "recommended_scope",
            "pre_attestation_review_ready",
            "The recommended reduced scope preserves all lanes/families/rows while reducing shot count, but must be preregistered before any attestation.",
            {"recommended_scope_id": recommended, "recommended_scope": half_scope},
        ),
        _review_item(
            "claim_boundary",
            "reduced_scope_not_final_without_preregistration",
            "Only the full 4096-shot plan directly inherits the Stage188 evidentiary thresholds; reduced plans need a preregistered lower-precision interpretation boundary.",
            {"full_scope_id": full_scope["scope_id"], "scouting_scope_id": scout_scope["scope_id"]},
        ),
    ]
    blockers: list[str] = []
    if missing_sources:
        blockers.append("source_artifacts_missing")
    if not stage188_positive:
        blockers.append("stage188_replacement_sim_not_positive")
    if not stage196_ready:
        blockers.append("stage196_cost_estimate_not_ready")
    if full_scope["estimated_usd_at_50us_per_shot"] > budget_cap:
        blockers.append("full_scope_exceeds_budget_at_50us_scenario")
    if missing_sources:
        decision = "REPLACEMENT_COST_CONSTRAINED_SCOPE_REVIEW_INCOMPLETE"
    elif any(blocker in blockers for blocker in ("stage188_replacement_sim_not_positive", "stage196_cost_estimate_not_ready")):
        decision = "REPLACEMENT_COST_CONSTRAINED_SCOPE_REVIEW_BLOCKED"
    else:
        decision = "REPLACEMENT_REDUCED_SCOPE_RECOMMENDED_BEFORE_CREDIT_ATTESTATION"
    return {
        "schema_version": STAGE197_SCHEMA_VERSION,
        "stage": "stage197_replacement_cost_constrained_scope_review",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": decision,
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "blockers": sorted(set(blockers)),
        "budget_cap_usd": budget_cap,
        "ibm_candidate_count": len(ibm_candidates),
        "min_ibm_positional_margin_shot_quanta_at_4096": min_positional_margin,
        "min_ibm_matched_null_margin_shot_quanta_at_4096": min_null_margin,
        "recommended_scope_id": recommended,
        "scope_options": scope_options,
        "review_items": review_items,
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "runnable_commands_recorded": False,
        "explicit_user_approval_required": True,
        "claim_boundary": {
            "supported": [
                "cost-constrained comparison of full, reduced-shot, scout, and strong-lane hardware scopes",
                "explicit distinction between claim-capable and scouting-only scope reductions",
                "pre-attestation recommendation to avoid asking the user to approve a likely-over-budget full run",
            ],
            "excluded": [
                "hardware job submission",
                "provider-side IBM credit balance verification",
                "acceptance of credit attestation or exact live-run approval",
                "creation of a runnable live-submit command",
                "a noisy-hardware robustness or auditability conclusion",
            ],
        },
        "next_gate": (
            "Preregister the selected reduced-scope interpretation boundary before asking for credit attestation. "
            "Recommended default is all_lanes_half_shots_2048; use scout_512 only for operational smoke testing."
        ),
    }


def write_stage197_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
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
        "budget_cap_usd",
        "ibm_candidate_count",
        "min_ibm_positional_margin_shot_quanta_at_4096",
        "min_ibm_matched_null_margin_shot_quanta_at_4096",
        "recommended_scope_id",
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
    manifest["scope_csv_path"] = str((output_dir / "scope_options.csv").as_posix())
    paths = {
        "manifest": str(output_dir / "manifest.json"),
        "result": str(output_dir / "results.json"),
        "summary_csv": str(output_dir / "summary.csv"),
        "scope_csv": str(output_dir / "scope_options.csv"),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=("item_id", "status", "description"))
        writer.writeheader()
        for item in result["review_items"]:
            writer.writerow({field: item.get(field) for field in writer.fieldnames})
    scope_fields = (
        "scope_id",
        "evidentiary_status",
        "estimated_total_job_count",
        "estimated_total_shots",
        "shots_per_row",
        "estimated_usd_at_10us_per_shot",
        "estimated_usd_at_50us_per_shot",
        "estimated_usd_at_100us_per_shot",
        "scaled_min_positional_margin_shot_quanta",
        "scaled_min_matched_null_margin_shot_quanta",
    )
    with (output_dir / "scope_options.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=scope_fields)
        writer.writeheader()
        for scope in result["scope_options"]:
            writer.writerow({field: scope.get(field) for field in scope_fields})
    return paths


def print_stage197_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"budget_cap_usd: {result['budget_cap_usd']}")
    print(f"recommended_scope_id: {result['recommended_scope_id']}")
    print(f"blockers: {', '.join(result['blockers'])}")
    print(f"next_gate: {result['next_gate']}")
