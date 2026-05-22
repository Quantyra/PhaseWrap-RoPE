from __future__ import annotations

import csv
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

from qrope.stage190_replacement_execution_package import CALIBRATION_STATES, DEFAULT_OUTPUT_DIR as STAGE190_OUTPUT_DIR
from qrope.stage198_reduced_scope_preregistration import DEFAULT_OUTPUT_DIR as STAGE198_OUTPUT_DIR
from qrope.stage202_reduced_scope_live_runner_preparation_review import DEFAULT_OUTPUT_DIR as STAGE202_OUTPUT_DIR
from qrope.stage99_matched_fixed_width_encoding_packet_freezer import OBJECTIVE


STAGE203_SCHEMA_VERSION = "qrope_stage203_reduced_scope_execution_package_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE202_RESULTS = STAGE202_OUTPUT_DIR / "results.json"
DEFAULT_STAGE198_RESULTS = STAGE198_OUTPUT_DIR / "results.json"
DEFAULT_STAGE190_RESULTS = STAGE190_OUTPUT_DIR / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage203_reduced_scope_execution_package_100usd"
STAGE202_READY = "REDUCED_SCOPE_LIVE_RUNNER_PREPARATION_REVIEW_READY_TO_BUILD_PACKAGE_NOT_LIVE"
STAGE198_READY = "REDUCED_SCOPE_PREREGISTERED_READY_FOR_COST_ATTESTATION_REVIEW"
STAGE190_READY = "REPLACEMENT_EXECUTION_PACKAGE_PREPARED_COUNTS_AND_CALIBRATION_REQUIRED"


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _reduced_packet_id(packet_id: str, shots_per_row: int) -> str:
    replaced = packet_id.replace("shots4096", f"shots{shots_per_row}")
    if replaced == packet_id:
        replaced = f"{packet_id}__reduced_shots{shots_per_row}"
    return replaced


def _convert_template(template: dict[str, Any], *, shots_per_row: int, backend: str, stage190_path: Path) -> dict[str, Any]:
    reduced = deepcopy(template)
    reduced["schema_version"] = STAGE203_SCHEMA_VERSION
    reduced["template_type"] = "reduced_scope_packet_execution_counts"
    reduced["original_stage190_packet_id"] = template.get("packet_id")
    reduced["original_stage190_packet_hash"] = template.get("packet_hash")
    reduced["packet_id"] = _reduced_packet_id(str(template.get("packet_id")), shots_per_row)
    reduced["source_lane_id"] = _reduced_packet_id(str(template.get("source_lane_id")), shots_per_row)
    reduced["backend"] = backend
    reduced["shot_count"] = shots_per_row
    reduced["status"] = "template_counts_required_reduced_scope"
    reduced["no_hardware_submission"] = True
    reduced["job_or_task_ids"] = []
    reduced["submitted_at_utc"] = ""
    reduced["completed_at_utc"] = ""
    metadata = reduced.setdefault("backend_metadata", {})
    metadata["backend"] = ""
    metadata["provider"] = template.get("provider")
    metadata["calibration_timestamp_utc"] = ""
    metadata["stage190_result_path"] = str(stage190_path.as_posix())
    metadata["stage203_reduced_scope_result_path"] = ""
    metadata.setdefault("additional_metadata", {})
    for row in reduced.get("raw_counts_by_row", []):
        row["counts"] = {}
    return reduced


def _convert_calibration(calibration: dict[str, Any], *, backend: str, shots_per_state: int, stage190_path: Path) -> dict[str, Any]:
    reduced = deepcopy(calibration)
    reduced["schema_version"] = STAGE203_SCHEMA_VERSION
    reduced["template_type"] = "reduced_scope_known_state_calibration_counts"
    reduced["backend"] = backend
    reduced["status"] = "template_counts_required_reduced_scope"
    reduced["no_hardware_submission"] = True
    reduced["job_or_task_ids"] = []
    reduced["submitted_at_utc"] = ""
    reduced["completed_at_utc"] = ""
    reduced["shots_per_state"] = shots_per_state
    metadata = reduced.setdefault("backend_metadata", {})
    metadata["backend"] = ""
    metadata["stage190_result_path"] = str(stage190_path.as_posix())
    metadata["stage203_reduced_scope_result_path"] = ""
    metadata.setdefault("additional_metadata", {})
    for state in reduced.get("raw_counts_by_state", []):
        state["counts"] = {}
    return reduced


def _evidence_records(execution_templates: list[dict[str, Any]], calibration_template: dict[str, Any]) -> list[dict[str, Any]]:
    records = [
        {
            "template_type": "reduced_scope_packet_execution_counts",
            "packet_id": template["packet_id"],
            "original_stage190_packet_id": template["original_stage190_packet_id"],
            "source_lane_id": template["source_lane_id"],
            "encoding_family": template["encoding_family"],
            "circuit_template": template["circuit_template"],
            "row_count": len(template["raw_counts_by_row"]),
            "shot_count": template["shot_count"],
            "ready_for_interpretation": False,
            "missing_evidence": "job_or_task_ids; backend_metadata; submitted_at_utc; completed_at_utc; raw_counts_by_row",
        }
        for template in execution_templates
    ]
    records.append(
        {
            "template_type": "reduced_scope_known_state_calibration_counts",
            "packet_id": "",
            "original_stage190_packet_id": "",
            "source_lane_id": "",
            "encoding_family": "",
            "circuit_template": "known_state_calibration",
            "row_count": len(calibration_template["raw_counts_by_state"]),
            "shot_count": calibration_template["shots_per_state"],
            "ready_for_interpretation": False,
            "missing_evidence": "job_or_task_ids; backend_metadata; submitted_at_utc; completed_at_utc; raw_counts_by_state",
        }
    )
    return records


def run_stage203_reduced_scope_execution_package(
    *,
    stage202_results_path: Path = DEFAULT_STAGE202_RESULTS,
    stage198_results_path: Path = DEFAULT_STAGE198_RESULTS,
    stage190_results_path: Path = DEFAULT_STAGE190_RESULTS,
) -> dict[str, Any]:
    stage202 = _load_json(stage202_results_path)
    stage198 = _load_json(stage198_results_path)
    stage190 = _load_json(stage190_results_path)
    sources = [(stage202_results_path, stage202), (stage198_results_path, stage198), (stage190_results_path, stage190)]
    missing_sources = [str(path.as_posix()) for path, payload in sources if not isinstance(payload, dict)]
    blockers: list[str] = []
    if missing_sources:
        blockers.append("missing_source_artifacts")
    stage202_ready = bool(isinstance(stage202, dict) and stage202.get("decision") == STAGE202_READY and stage202.get("exact_approval_ready") is True)
    stage198_ready = bool(isinstance(stage198, dict) and stage198.get("decision") == STAGE198_READY)
    stage190_ready = bool(isinstance(stage190, dict) and stage190.get("decision") == STAGE190_READY)
    if not stage202_ready:
        blockers.append("stage202_live_runner_preparation_not_ready")
    if not stage198_ready:
        blockers.append("stage198_reduced_scope_not_preregistered")
    if not stage190_ready:
        blockers.append("stage190_replacement_package_not_ready")
    scope = stage198.get("selected_scope", {}) if isinstance(stage198, dict) else {}
    boundary = stage198.get("interpretation_boundary", {}) if isinstance(stage198, dict) else {}
    shots_per_row = int(scope.get("shots_per_row") or boundary.get("shots_per_row") or 0)
    calibration_shots = int(boundary.get("calibration_shots_per_state") or 0)
    if shots_per_row != 2048:
        blockers.append("reduced_scope_shots_per_row_not_2048")
    if calibration_shots != 1000:
        blockers.append("calibration_shots_per_state_not_1000")
    backend_metadata = stage202.get("backend_metadata", {}) if isinstance(stage202, dict) else {}
    backend = str(backend_metadata.get("backend") or "PREREGISTERED_IBM_BACKEND_TO_BE_SELECTED")
    source_templates = stage190.get("execution_templates", []) if isinstance(stage190, dict) else []
    source_calibration = stage190.get("calibration_template", {}) if isinstance(stage190, dict) else {}
    execution_templates = [
        _convert_template(template, shots_per_row=shots_per_row, backend=backend, stage190_path=stage190_results_path)
        for template in source_templates
        if isinstance(template, dict)
    ]
    calibration_template = _convert_calibration(source_calibration, backend=backend, shots_per_state=calibration_shots, stage190_path=stage190_results_path) if isinstance(source_calibration, dict) else {}
    packet_row_jobs = sum(len(template.get("raw_counts_by_row", [])) for template in execution_templates)
    calibration_jobs = len(CALIBRATION_STATES)
    packet_shots = packet_row_jobs * shots_per_row
    calibration_shots_total = calibration_jobs * calibration_shots
    total_jobs = packet_row_jobs + calibration_jobs
    total_shots = packet_shots + calibration_shots_total
    if len(execution_templates) != 20:
        blockers.append("reduced_scope_packet_template_count_mismatch")
    if packet_row_jobs != int(scope.get("packet_row_job_count") or 320):
        blockers.append("reduced_scope_packet_row_job_count_mismatch")
    if total_jobs != int(scope.get("estimated_total_job_count") or 324):
        blockers.append("reduced_scope_total_job_count_mismatch")
    if total_shots != int(scope.get("estimated_total_shots") or 659360):
        blockers.append("reduced_scope_total_shot_count_mismatch")
    evidence_records = _evidence_records(execution_templates, calibration_template) if calibration_template else []
    decision = "REDUCED_SCOPE_EXECUTION_PACKAGE_INCOMPLETE" if blockers else "REDUCED_SCOPE_EXECUTION_PACKAGE_PREPARED_COUNTS_AND_CALIBRATION_REQUIRED_NOT_LIVE"
    return {
        "schema_version": STAGE203_SCHEMA_VERSION,
        "stage": "stage203_reduced_scope_execution_package",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": decision,
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "blockers": sorted(set(blockers)),
        "scope_id": scope.get("scope_id"),
        "hardware_scope_label": boundary.get("hardware_scope_label"),
        "backend": backend,
        "budget_cap_usd": stage202.get("budget_cap_usd") if isinstance(stage202, dict) else None,
        "shot_count_transformation": {"source_stage190_shots_per_row": 4096, "reduced_scope_shots_per_row": shots_per_row},
        "packet_template_count": len(execution_templates),
        "calibration_template_count": 1 if calibration_template else 0,
        "estimated_packet_row_job_count": packet_row_jobs,
        "estimated_calibration_job_count": calibration_jobs,
        "estimated_total_job_count": total_jobs,
        "estimated_packet_shots": packet_shots,
        "estimated_calibration_shots": calibration_shots_total,
        "estimated_total_shots": total_shots,
        "required_execution_fields": ["job_or_task_ids", "backend_metadata", "submitted_at_utc", "completed_at_utc", "raw_counts_by_row"],
        "required_calibration_states": list(CALIBRATION_STATES),
        "execution_templates": execution_templates,
        "calibration_template": calibration_template,
        "evidence_records": evidence_records,
        "no_hardware_submission": True,
        "live_submit_command_created": False,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "runnable_commands_recorded": False,
        "claim_boundary": {
            "supported": [
                "approved reduced-scope 2048-shot execution templates are prepared without submitting hardware",
                "Stage190 4096-shot templates are transformed into a preregistered 2048-shot contract",
                "result-ingestion fields and calibration counts are required before interpretation",
            ],
            "excluded": [
                "hardware job submission",
                "creation of a runnable live-submit command",
                "provider-side result retrieval",
                "calibration pass/fail or robustness interpretation",
                "a noisy-hardware robustness or auditability conclusion",
            ],
        },
        "next_gate": (
            "Prepare the guarded reduced-scope runner from this package, with a fresh read-only backend refresh and no "
            "secret or runnable command recording before the final execution step."
        ),
    }


def write_stage203_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    template_dir = output_dir / "execution_templates"
    template_dir.mkdir(parents=True, exist_ok=True)
    template_paths = []
    for template in result["execution_templates"]:
        path = template_dir / f"{template['packet_id']}.json"
        path.write_text(json.dumps(template, indent=2, sort_keys=True), encoding="utf-8")
        template_paths.append(str(path.as_posix()))
    calibration_path = template_dir / "ibm_runtime_reduced_scope_known_state_calibration.json"
    calibration_path.write_text(json.dumps(result["calibration_template"], indent=2, sort_keys=True), encoding="utf-8")
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
        "backend",
        "budget_cap_usd",
        "shot_count_transformation",
        "packet_template_count",
        "calibration_template_count",
        "estimated_packet_row_job_count",
        "estimated_calibration_job_count",
        "estimated_total_job_count",
        "estimated_packet_shots",
        "estimated_calibration_shots",
        "estimated_total_shots",
        "required_execution_fields",
        "required_calibration_states",
        "no_hardware_submission",
        "live_submit_command_created",
        "provider_credentials_required",
        "secret_values_recorded",
        "runnable_commands_recorded",
        "claim_boundary",
        "next_gate",
    )
    manifest = {key: result[key] for key in manifest_keys}
    manifest["template_paths"] = template_paths
    manifest["calibration_template_path"] = str(calibration_path.as_posix())
    manifest["result_path"] = str((output_dir / "results.json").as_posix())
    manifest["summary_csv_path"] = str((output_dir / "summary.csv").as_posix())
    paths = {
        "manifest": str(output_dir / "manifest.json"),
        "result": str(output_dir / "results.json"),
        "summary_csv": str(output_dir / "summary.csv"),
        "template_dir": str(template_dir),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=(
                "template_type",
                "packet_id",
                "original_stage190_packet_id",
                "source_lane_id",
                "encoding_family",
                "circuit_template",
                "row_count",
                "shot_count",
                "missing_evidence",
                "ready_for_interpretation",
            ),
        )
        writer.writeheader()
        for record in result["evidence_records"]:
            writer.writerow({field: record.get(field) for field in writer.fieldnames})
    return paths


def print_stage203_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"scope_id: {result['scope_id']}")
    print(f"backend: {result['backend']}")
    print(f"budget_cap_usd: {result['budget_cap_usd']}")
    print(f"packet_template_count: {result['packet_template_count']}")
    print(f"estimated_total_job_count: {result['estimated_total_job_count']}")
    print(f"estimated_total_shots: {result['estimated_total_shots']}")
    print(f"blockers: {', '.join(result['blockers'])}")
    print(f"next_gate: {result['next_gate']}")
