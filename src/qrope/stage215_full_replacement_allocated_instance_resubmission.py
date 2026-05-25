from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Callable

from qrope.env_utils import load_local_dotenv
from qrope.stage190_replacement_execution_package import DEFAULT_OUTPUT_DIR as STAGE190_OUTPUT_DIR
from qrope.stage212_full_replacement_hardware_submission import (
    _estimated_total_shots,
    _load_templates,
    _real_submit_template,
    _submission_record,
)
from qrope.stage213_full_replacement_job_status_poll import DEFAULT_OUTPUT_DIR as STAGE213_OUTPUT_DIR, STAGE212_SUBMITTED
from qrope.stage99_matched_fixed_width_encoding_packet_freezer import OBJECTIVE


STAGE215_SCHEMA_VERSION = "qrope_stage215_full_replacement_allocated_instance_resubmission_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE212_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage212_full_replacement_hardware_submission_250usd" / "results.json"
DEFAULT_STAGE213_RESULTS = STAGE213_OUTPUT_DIR / "results.json"
DEFAULT_STAGE190_RESULTS = STAGE190_OUTPUT_DIR / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage215_full_replacement_allocated_instance_resubmission_250usd"
DONE_STATUSES = {"DONE", "COMPLETED", "JobStatus.DONE", "done", "completed"}


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _template_key(record: dict[str, Any]) -> str:
    return str(record.get("packet_id") or "__calibration__")


def _template_shots(template: dict[str, Any]) -> int:
    return int(template.get("shots_per_state") or template.get("shot_count") or 0)


def _template_circuit_count(template: dict[str, Any]) -> int:
    rows_key = "raw_counts_by_state" if template.get("template_type") == "replacement_known_state_calibration_counts" else "raw_counts_by_row"
    return len(template.get(rows_key, []))


def _pending_keys_from_stage213(stage213: dict[str, Any]) -> set[str]:
    pending: set[str] = set()
    for record in stage213.get("poll_records", []):
        if not isinstance(record, dict):
            continue
        if str(record.get("status", "")) not in DONE_STATUSES:
            pending.add(_template_key(record))
    return pending


def run_stage215_full_replacement_allocated_instance_resubmission(
    *,
    stage212_results_path: Path = DEFAULT_STAGE212_RESULTS,
    stage213_results_path: Path = DEFAULT_STAGE213_RESULTS,
    stage190_results_path: Path = DEFAULT_STAGE190_RESULTS,
    allow_live_submit: bool = False,
    submit_template: Callable[..., dict[str, Any]] | None = None,
    load_dotenv: bool = False,
) -> dict[str, Any]:
    if load_dotenv:
        load_local_dotenv(Path(".env"))
    stage212 = _load_json(stage212_results_path)
    stage213 = _load_json(stage213_results_path)
    stage190 = _load_json(stage190_results_path)
    sources = [(stage212_results_path, stage212), (stage213_results_path, stage213), (stage190_results_path, stage190)]
    missing_sources = [str(path.as_posix()) for path, payload in sources if not isinstance(payload, dict)]
    blockers: list[str] = []
    if missing_sources:
        blockers.append("source_artifacts_missing")
    if not (isinstance(stage212, dict) and stage212.get("decision") == STAGE212_SUBMITTED):
        blockers.append("stage212_submission_not_ready")
    if not isinstance(stage213, dict):
        blockers.append("stage213_poll_missing")
    if not allow_live_submit:
        blockers.append("allow_live_submit_flag_required")

    templates = _load_templates(stage190) if isinstance(stage190, dict) else []
    if len(templates) != 21:
        blockers.append("stage190_template_count_mismatch")
    template_by_key = {_template_key(template): template for template in templates}
    original_records = [record for record in (stage212.get("submission_records", []) if isinstance(stage212, dict) else []) if isinstance(record, dict)]
    original_by_key = {_template_key(record): record for record in original_records}
    pending_keys = _pending_keys_from_stage213(stage213) if isinstance(stage213, dict) else set()
    if not pending_keys:
        blockers.append("no_pending_runtime_jobs_to_replace")
    missing_templates = sorted(key for key in pending_keys if key not in template_by_key)
    if missing_templates:
        blockers.append("pending_template_missing_from_stage190")

    submitter = submit_template or _real_submit_template
    backend_name = str(stage212.get("backend") if isinstance(stage212, dict) else "" or "")
    if not backend_name:
        blockers.append("backend_missing")

    replacement_records: list[dict[str, Any]] = []
    merged_by_key = dict(original_by_key)
    attempted = False
    template_order = [_template_key(template) for template in templates]
    if not blockers:
        attempted = True
        for key in [template_key for template_key in template_order if template_key in pending_keys]:
            template = template_by_key[key]
            superseded = original_by_key.get(key, {})
            try:
                submit_result = submitter(template=template, backend_name=backend_name)
                record = _submission_record(template, submit_result, status="submitted_awaiting_results")
                record["superseded_runtime_job_id"] = str(superseded.get("runtime_job_id", ""))
                record["resubmission_reason"] = "open_instance_quota_exhausted_allocated_instance_replacement"
                replacement_records.append(record)
                merged_by_key[key] = record
            except Exception as exc:  # noqa: BLE001
                blockers.append("replacement_template_submission_failed")
                failed = _submission_record(template, None, status="submission_failed", error_type=type(exc).__name__)
                failed["superseded_runtime_job_id"] = str(superseded.get("runtime_job_id", ""))
                replacement_records.append(failed)
                break

    merged_records = [merged_by_key[key] for key in template_order if key in merged_by_key]
    submitted_replacement_count = sum(1 for record in replacement_records if record.get("status") == "submitted_awaiting_results" and record.get("runtime_job_id"))
    if attempted and submitted_replacement_count != len(pending_keys):
        blockers.append("not_all_replacements_submitted")
    estimated_replacement_shots = sum(_template_shots(template_by_key[key]) * _template_circuit_count(template_by_key[key]) for key in pending_keys if key in template_by_key)
    decision = STAGE212_SUBMITTED if not blockers else "FULL_REPLACEMENT_ALLOCATED_INSTANCE_RESUBMISSION_BLOCKED_OR_PARTIAL"
    return {
        "schema_version": STAGE215_SCHEMA_VERSION,
        "stage": "stage215_full_replacement_allocated_instance_resubmission",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": decision,
        "replacement_decision": "FULL_REPLACEMENT_ALLOCATED_INSTANCE_REPLACEMENTS_SUBMITTED_AWAITING_RESULTS" if not blockers else "FULL_REPLACEMENT_ALLOCATED_INSTANCE_RESUBMISSION_BLOCKED_OR_PARTIAL",
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "blockers": sorted(set(blockers)),
        "backend": backend_name,
        "budget_cap_usd": stage212.get("budget_cap_usd") if isinstance(stage212, dict) else None,
        "allow_live_submit": allow_live_submit,
        "replacement_attempted": attempted,
        "pending_replacement_runtime_job_count": len(pending_keys),
        "submitted_replacement_runtime_job_count": submitted_replacement_count,
        "expected_runtime_job_count": 21,
        "submitted_runtime_job_count": sum(1 for record in merged_records if record.get("runtime_job_id")),
        "estimated_total_job_count": stage190.get("estimated_total_job_count") if isinstance(stage190, dict) else None,
        "estimated_total_shots": _estimated_total_shots(stage190),
        "estimated_replacement_shots": estimated_replacement_shots,
        "pending_replacement_keys": sorted(pending_keys),
        "replacement_records": replacement_records,
        "submission_records": merged_records,
        "no_hardware_submission": not attempted,
        "hardware_submission_performed": attempted and submitted_replacement_count > 0,
        "provider_credentials_required": True,
        "secret_values_recorded": False,
        "runnable_commands_recorded": False,
        "claim_boundary": {
            "supported": [
                "guarded resubmission of only pending full 4096-shot replacement templates to the currently configured IBM Runtime instance",
                "merged Stage212-compatible submission records for later status polling and result collection",
            ],
            "excluded": [
                "provider-side result counts unless a later collector retrieves them",
                "calibration pass/fail",
                "robustness or auditability interpretation",
            ],
        },
        "next_gate": "Poll the merged submission records; when all Runtime jobs are complete, collect provider counts and validate calibration.",
    }


def write_stage215_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_keys = (
        "schema_version", "stage", "status", "objective", "decision", "replacement_decision",
        "source_artifacts", "missing_source_artifacts", "blockers", "backend", "budget_cap_usd",
        "allow_live_submit", "replacement_attempted", "pending_replacement_runtime_job_count",
        "submitted_replacement_runtime_job_count", "expected_runtime_job_count",
        "submitted_runtime_job_count", "estimated_total_job_count", "estimated_total_shots",
        "estimated_replacement_shots", "no_hardware_submission", "hardware_submission_performed",
        "provider_credentials_required", "secret_values_recorded", "runnable_commands_recorded",
        "claim_boundary", "next_gate",
    )
    manifest = {key: result[key] for key in manifest_keys}
    manifest["result_path"] = str((output_dir / "results.json").as_posix())
    manifest["summary_csv_path"] = str((output_dir / "summary.csv").as_posix())
    paths = {"manifest": str(output_dir / "manifest.json"), "result": str(output_dir / "results.json"), "summary_csv": str(output_dir / "summary.csv")}
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=("template_type", "packet_id", "runtime_job_id", "superseded_runtime_job_id", "status", "error_type"))
        writer.writeheader()
        for record in result["replacement_records"]:
            writer.writerow({field: record.get(field, "") for field in writer.fieldnames})
    return paths


def print_stage215_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['replacement_decision']}")
    print(f"backend: {result['backend']}")
    print(f"budget_cap_usd: {result['budget_cap_usd']}")
    print(f"replacement_attempted: {result['replacement_attempted']}")
    print(f"submitted_replacement_runtime_job_count: {result['submitted_replacement_runtime_job_count']}/{result['pending_replacement_runtime_job_count']}")
    print(f"estimated_replacement_shots: {result['estimated_replacement_shots']}")
    print(f"blockers: {', '.join(result['blockers'])}")
    print(f"next_gate: {result['next_gate']}")
