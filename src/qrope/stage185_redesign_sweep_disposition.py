from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from qrope.stage181_fixed_width_target_redesign_plan import DEFAULT_OUTPUT_DIR as STAGE181_OUTPUT_DIR
from qrope.stage182_balanced_phase_window_candidate_screen import DEFAULT_OUTPUT_DIR as STAGE182_OUTPUT_DIR
from qrope.stage183_contrast_amplified_delta_candidate_screen import DEFAULT_OUTPUT_DIR as STAGE183_OUTPUT_DIR
from qrope.stage184_error_orthogonalized_components_candidate_screen import DEFAULT_OUTPUT_DIR as STAGE184_OUTPUT_DIR
from qrope.stage99_matched_fixed_width_encoding_packet_freezer import OBJECTIVE


STAGE185_SCHEMA_VERSION = "qrope_stage185_redesign_sweep_disposition_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE181_RESULTS = STAGE181_OUTPUT_DIR / "results.json"
DEFAULT_STAGE182_RESULTS = STAGE182_OUTPUT_DIR / "results.json"
DEFAULT_STAGE183_RESULTS = STAGE183_OUTPUT_DIR / "results.json"
DEFAULT_STAGE184_RESULTS = STAGE184_OUTPUT_DIR / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage185_redesign_sweep_disposition"
STAGE181_READY = "FIXED_WIDTH_TARGET_REDESIGN_PLAN_READY"
EXPECTED_CANDIDATE_DECISIONS = {
    "pw_balanced_phase_window_v1": "BALANCED_PHASE_WINDOW_CANDIDATE_DOES_NOT_SUPPORT_HARDWARE_REOPEN",
    "pw_contrast_amplified_delta_v1": "CONTRAST_AMPLIFIED_DELTA_CANDIDATE_DOES_NOT_SUPPORT_HARDWARE_REOPEN",
    "pw_error_orthogonalized_components_v1": "ERROR_ORTHOGONALIZED_COMPONENTS_CANDIDATE_DOES_NOT_SUPPORT_HARDWARE_REOPEN",
}


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _candidate_record(path: Path, payload: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {
            "result_path": str(path.as_posix()),
            "design_family_id": None,
            "decision": None,
            "status": "missing",
            "packet_count": 0,
            "comparison_group_count": 0,
            "reopen_candidate_count": 0,
            "hardware_reopen_supported": False,
            "expected_no_reopen_decision": False,
        }
    design_family_id = str(payload.get("design_family_id"))
    decision = str(payload.get("decision"))
    return {
        "result_path": str(path.as_posix()),
        "design_family_id": design_family_id,
        "decision": decision,
        "status": payload.get("status"),
        "packet_count": int(payload.get("packet_count") or 0),
        "comparison_group_count": int(payload.get("comparison_group_count") or 0),
        "reopen_candidate_count": int(payload.get("reopen_candidate_count") or 0),
        "hardware_reopen_supported": decision.endswith("_SUPPORTS_HARDWARE_REOPEN"),
        "expected_no_reopen_decision": decision == EXPECTED_CANDIDATE_DECISIONS.get(design_family_id),
    }


def run_stage185_redesign_sweep_disposition(
    *,
    stage181_results_path: Path = DEFAULT_STAGE181_RESULTS,
    stage182_results_path: Path = DEFAULT_STAGE182_RESULTS,
    stage183_results_path: Path = DEFAULT_STAGE183_RESULTS,
    stage184_results_path: Path = DEFAULT_STAGE184_RESULTS,
) -> dict[str, Any]:
    stage181 = _load_json(stage181_results_path)
    candidate_sources = [
        (stage182_results_path, _load_json(stage182_results_path)),
        (stage183_results_path, _load_json(stage183_results_path)),
        (stage184_results_path, _load_json(stage184_results_path)),
    ]
    sources = [(stage181_results_path, stage181)] + candidate_sources
    missing_sources = [str(path.as_posix()) for path, payload in sources if not isinstance(payload, dict)]
    blockers = []
    if missing_sources:
        blockers.append("missing_source_artifacts")
    if isinstance(stage181, dict) and stage181.get("decision") != STAGE181_READY:
        blockers.append("stage181_redesign_plan_not_ready")

    design_family_ids = {
        str(family.get("family_id"))
        for family in stage181.get("design_families", [])
        if isinstance(stage181, dict) and isinstance(family, dict)
    }
    missing_planned_families = sorted(set(EXPECTED_CANDIDATE_DECISIONS) - design_family_ids)
    if missing_planned_families:
        blockers.append("stage181_expected_design_families_missing")

    candidate_records = [_candidate_record(path, payload if isinstance(payload, dict) else None) for path, payload in candidate_sources]
    tested_family_ids = {str(record.get("design_family_id")) for record in candidate_records if record.get("design_family_id")}
    missing_candidate_families = sorted(set(EXPECTED_CANDIDATE_DECISIONS) - tested_family_ids)
    if missing_candidate_families:
        blockers.append("redesign_candidate_family_results_missing")

    supported = [record for record in candidate_records if record.get("hardware_reopen_supported") is True]
    unexpected = [record for record in candidate_records if record.get("expected_no_reopen_decision") is not True]
    if unexpected:
        blockers.append("redesign_candidate_decision_not_no_reopen")

    total_packets = sum(int(record["packet_count"]) for record in candidate_records)
    total_comparison_groups = sum(int(record["comparison_group_count"]) for record in candidate_records)
    total_reopen_candidates = sum(int(record["reopen_candidate_count"]) for record in candidate_records)
    if blockers:
        decision = "REDESIGN_SWEEP_DISPOSITION_INCOMPLETE"
    elif supported:
        decision = "REDESIGN_SWEEP_FOUND_HARDWARE_REOPEN_CANDIDATE"
    else:
        decision = "REDESIGN_SWEEP_EXHAUSTED_NO_HARDWARE_REOPEN"

    return {
        "schema_version": STAGE185_SCHEMA_VERSION,
        "stage": "stage185_redesign_sweep_disposition",
        "status": "completed" if not blockers else "incomplete",
        "objective": OBJECTIVE,
        "decision": decision,
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "blockers": sorted(set(blockers)),
        "planned_design_family_count": len(design_family_ids),
        "expected_design_families": sorted(EXPECTED_CANDIDATE_DECISIONS),
        "missing_planned_families": missing_planned_families,
        "missing_candidate_families": missing_candidate_families,
        "candidate_family_count": len(candidate_records),
        "candidate_records": candidate_records,
        "hardware_reopen_candidate_count": len(supported),
        "total_packet_count": total_packets,
        "total_comparison_group_count": total_comparison_groups,
        "total_reopen_candidate_count": total_reopen_candidates,
        "simulated_only": True,
        "ibm_backend_properties_informed": True,
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "runnable_commands_recorded": False,
        "hardware_path_status": "current_ibm_328_job_run_remains_archived",
        "disposition": (
            "archive_current_fixed_width_ibm_hardware_path_and_do_not_reopen_without_new_target_control_semantics_or_material_calibration_evidence"
            if decision == "REDESIGN_SWEEP_EXHAUSTED_NO_HARDWARE_REOPEN"
            else "do_not_change_hardware_path_until_incomplete_redesign_sweep_is_resolved"
        ),
        "claim_boundary": {
            "supported": [
                "all three Stage181 preregistered redesign families were screened under the Stage177 primary IBM-informed models",
                "none of the screened redesign families produced a hardware reopen candidate",
                "the current archived IBM 328-job path remains unsupported by simulated IBM-informed evidence",
            ],
            "excluded": [
                "hardware job submission",
                "a final noisy-hardware robustness or auditability conclusion",
                "a proof that PhaseWrap-RoPE cannot show value under any future target, control, backend, or calibration model",
                "credit, billing, or provider-account validation",
            ],
        },
        "next_gate": (
            "Revise target/control semantics with a new preregistration, obtain materially different calibration evidence, "
            "or stop pursuing the current fixed-width IBM hardware path before any hardware approval is considered."
        ),
    }


def write_stage185_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
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
        "planned_design_family_count",
        "expected_design_families",
        "missing_planned_families",
        "missing_candidate_families",
        "candidate_family_count",
        "hardware_reopen_candidate_count",
        "total_packet_count",
        "total_comparison_group_count",
        "total_reopen_candidate_count",
        "simulated_only",
        "ibm_backend_properties_informed",
        "no_hardware_submission",
        "provider_credentials_required",
        "secret_values_recorded",
        "runnable_commands_recorded",
        "hardware_path_status",
        "disposition",
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
        writer = csv.DictWriter(
            handle,
            fieldnames=(
                "design_family_id",
                "decision",
                "packet_count",
                "comparison_group_count",
                "reopen_candidate_count",
                "hardware_reopen_supported",
                "expected_no_reopen_decision",
            ),
        )
        writer.writeheader()
        for record in result["candidate_records"]:
            writer.writerow({field: record.get(field) for field in writer.fieldnames})
    return paths


def print_stage185_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"blockers: {', '.join(result['blockers'])}")
    print(f"candidate_family_count: {result['candidate_family_count']}")
    print(f"hardware_reopen_candidate_count: {result['hardware_reopen_candidate_count']}")
    print(f"disposition: {result['disposition']}")
    print(f"next_gate: {result['next_gate']}")
