from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from qrope.stage197_replacement_cost_constrained_scope_review import DEFAULT_OUTPUT_DIR as STAGE197_OUTPUT_DIR
from qrope.stage99_matched_fixed_width_encoding_packet_freezer import OBJECTIVE


STAGE198_SCHEMA_VERSION = "qrope_stage198_reduced_scope_preregistration_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE197_RESULTS = STAGE197_OUTPUT_DIR / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage198_reduced_scope_preregistration"
STAGE197_RECOMMENDED = "REPLACEMENT_REDUCED_SCOPE_RECOMMENDED_BEFORE_CREDIT_ATTESTATION"
SELECTED_SCOPE_ID = "all_lanes_half_shots_2048"


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _scope_by_id(stage197: dict[str, Any], scope_id: str) -> dict[str, Any] | None:
    for scope in stage197.get("scope_options", []):
        if isinstance(scope, dict) and scope.get("scope_id") == scope_id:
            return scope
    return None


def _prereg_item(item_id: str, status: str, description: str, evidence: Any) -> dict[str, Any]:
    return {"item_id": item_id, "status": status, "description": description, "evidence": evidence}


def _interpretation_boundary(scope: dict[str, Any]) -> dict[str, Any]:
    return {
        "scope_id": scope["scope_id"],
        "hardware_scope_label": "reduced_precision_all_lanes_2048_shots_v1",
        "selected_lanes": "all four Stage189/190 IBM replacement lanes",
        "required_families": ["phasewrap", "rope_like", "sinusoidal_like", "alibi_like", "matched_nonzero_null_control"],
        "required_templates": ["two_ry_product_state_z_readout_v1", "two_ry_cx_parity_z_readout_v1"],
        "required_seed_pairs": ["ibm:314", "ibm:577"],
        "row_count_per_packet": scope["row_count_per_packet"],
        "shots_per_row": scope["shots_per_row"],
        "calibration_states": ["00", "01", "10", "11"],
        "calibration_shots_per_state": 1000,
        "primary_metric": "normalized_noise_sensitivity_delta_v1",
        "required_reported_metrics": [
            "mean_absolute_score_error",
            "normalized_noise_sensitivity_delta",
            "slope_retention",
            "rank_retention",
            "matched_null_control_margin",
            "shot_quantum_margin",
        ],
        "pass_fail_policy": {
            "minimum_stable_seed_pairs": 2,
            "minimum_stable_templates_per_seed_pair": 2,
            "minimum_scaled_best_positional_margin_shot_quanta": 2.0,
            "minimum_scaled_matched_null_margin_shot_quanta": 2.0,
            "must_pass_phasewrap_vs_all_positional_comparators": True,
            "must_pass_phasewrap_vs_matched_nonzero_null_control": True,
            "lower_precision_caveat": (
                "A win at 2048 shots can support a reduced-precision hardware positive, but it cannot be described as the "
                "original 4096-shot evidentiary run. Any marginal result below 2 shot quanta is inconclusive, not a loss or win."
            ),
        },
        "cost_context": {
            "estimated_total_jobs": scope["estimated_total_job_count"],
            "estimated_total_shots": scope["estimated_total_shots"],
            "estimated_usd_at_10us_per_shot": scope["estimated_usd_at_10us_per_shot"],
            "estimated_usd_at_50us_per_shot": scope["estimated_usd_at_50us_per_shot"],
            "estimated_usd_at_100us_per_shot": scope["estimated_usd_at_100us_per_shot"],
        },
        "disallowed_interpretations": [
            "claiming equivalence to the full 4096-shot Stage190 package",
            "dropping any comparator family after hardware results are known",
            "using the 512-shot scout boundary for robustness claims",
            "treating directional seed577-only evidence as independent-seed replication",
            "changing thresholds after hardware counts are collected",
        ],
    }


def run_stage198_reduced_scope_preregistration(
    *,
    stage197_results_path: Path = DEFAULT_STAGE197_RESULTS,
) -> dict[str, Any]:
    stage197 = _load_json(stage197_results_path)
    missing_sources = [] if isinstance(stage197, dict) else [str(stage197_results_path.as_posix())]
    stage197_ready = bool(isinstance(stage197, dict) and stage197.get("decision") == STAGE197_RECOMMENDED)
    recommended_scope_id = stage197.get("recommended_scope_id") if isinstance(stage197, dict) else None
    scope = _scope_by_id(stage197, SELECTED_SCOPE_ID) if isinstance(stage197, dict) else None
    preregistration = _interpretation_boundary(scope) if isinstance(scope, dict) else None
    prereg_items = [
        _prereg_item(
            "stage197_scope_review",
            "ready" if stage197_ready else "blocked",
            "Reduced-scope preregistration requires Stage197 to recommend a reduced scope before credit attestation.",
            {"stage197_decision": stage197.get("decision") if isinstance(stage197, dict) else None, "recommended_scope_id": recommended_scope_id},
        ),
        _prereg_item(
            "selected_scope",
            "frozen" if isinstance(scope, dict) else "missing",
            "Selected reduced scope must be frozen before any credit attestation or live-runner preparation.",
            scope or {},
        ),
        _prereg_item(
            "interpretation_boundary",
            "preregistered" if isinstance(preregistration, dict) else "missing",
            "Reduced precision claim boundary, thresholds, and exclusions are frozen before hardware results exist.",
            preregistration or {},
        ),
        _prereg_item(
            "attestation_boundary",
            "still_required",
            "This preregistration does not verify IBM credit allowance and does not accept exact live-run approval.",
            {"credit_attestation_accepted_here": False, "exact_approval_accepted_here": False},
        ),
    ]
    blockers = []
    if missing_sources:
        blockers.append("source_artifacts_missing")
    if not stage197_ready:
        blockers.append("stage197_reduced_scope_not_recommended")
    if recommended_scope_id != SELECTED_SCOPE_ID:
        blockers.append("recommended_scope_mismatch")
    if not isinstance(scope, dict):
        blockers.append("selected_scope_missing")
    if missing_sources:
        decision = "REDUCED_SCOPE_PREREGISTRATION_INCOMPLETE"
    elif blockers:
        decision = "REDUCED_SCOPE_PREREGISTRATION_BLOCKED"
    else:
        decision = "REDUCED_SCOPE_PREREGISTERED_READY_FOR_COST_ATTESTATION_REVIEW"
    return {
        "schema_version": STAGE198_SCHEMA_VERSION,
        "stage": "stage198_reduced_scope_preregistration",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": decision,
        "source_artifacts": [str(stage197_results_path.as_posix())],
        "missing_source_artifacts": missing_sources,
        "blockers": sorted(set(blockers)),
        "selected_scope_id": SELECTED_SCOPE_ID,
        "recommended_scope_id": recommended_scope_id,
        "selected_scope": scope,
        "interpretation_boundary": preregistration,
        "preregistration_items": prereg_items,
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "runnable_commands_recorded": False,
        "explicit_user_approval_required": True,
        "claim_boundary": {
            "supported": [
                "reduced-scope all-lanes 2048-shot interpretation boundary is preregistered before credit attestation",
                "all comparator families, both IBM seeds, both templates, and all rows remain required",
                "lower-precision caveats and disallowed interpretations are explicit before hardware results exist",
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
            "Use this reduced-scope boundary in the next cost/attestation packet. If the user attests credit allowance, rerun "
            "Stage194/195 against the reduced scope before preparing any live runner."
        ),
    }


def write_stage198_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
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
        "selected_scope_id",
        "recommended_scope_id",
        "selected_scope",
        "interpretation_boundary",
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
        for item in result["preregistration_items"]:
            writer.writerow({field: item.get(field) for field in writer.fieldnames})
    return paths


def print_stage198_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"selected_scope_id: {result['selected_scope_id']}")
    scope = result["selected_scope"] or {}
    print(f"estimated_total_job_count: {scope.get('estimated_total_job_count')}")
    print(f"estimated_total_shots: {scope.get('estimated_total_shots')}")
    print(f"shots_per_row: {scope.get('shots_per_row')}")
    print(f"blockers: {', '.join(result['blockers'])}")
    print(f"next_gate: {result['next_gate']}")
