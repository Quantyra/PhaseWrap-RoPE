from __future__ import annotations

import csv
import json
import os
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

from qrope.env_utils import load_local_dotenv
from qrope.ibm_runtime_utils import ibm_runtime_service_kwargs
from qrope.provider_adapters.common import canonicalize_counts
from qrope.stage207_reduced_scope_result_collector import _extract_counts_list, _status_text
from qrope.stage99_matched_fixed_width_encoding_packet_freezer import OBJECTIVE


STAGE214_SCHEMA_VERSION = "qrope_stage214_full_replacement_result_collector_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE212_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage212_full_replacement_hardware_submission_250usd" / "results.json"
DEFAULT_STAGE190_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage190_replacement_execution_package" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage214_full_replacement_result_collector_250usd"
STAGE212_SUBMITTED = "FULL_REPLACEMENT_HARDWARE_SUBMITTED_AWAITING_RESULTS"


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _real_fetch_result(runtime_job_id: str) -> dict[str, Any]:
    from qiskit_ibm_runtime import QiskitRuntimeService

    service = QiskitRuntimeService(**ibm_runtime_service_kwargs())
    job = service.job(runtime_job_id)
    status = _status_text(job.status())
    if status not in {"DONE", "COMPLETED", "done", "completed"}:
        return {"runtime_job_id": runtime_job_id, "status": status, "counts_by_circuit": []}
    return {"runtime_job_id": runtime_job_id, "status": status, "counts_by_circuit": _extract_counts_list(job.result())}


def _template_key(template: dict[str, Any]) -> str:
    return str(template.get("packet_id") or "__calibration__")


def run_stage214_full_replacement_result_collector(
    *,
    stage212_results_path: Path = DEFAULT_STAGE212_RESULTS,
    stage190_results_path: Path = DEFAULT_STAGE190_RESULTS,
    fetch_result: Callable[[str], dict[str, Any]] | None = None,
    load_dotenv: bool = False,
) -> dict[str, Any]:
    if load_dotenv:
        load_local_dotenv(Path(".env"))
    stage212 = _load_json(stage212_results_path)
    stage190 = _load_json(stage190_results_path)
    sources = [(stage212_results_path, stage212), (stage190_results_path, stage190)]
    missing_sources = [str(path.as_posix()) for path, payload in sources if not isinstance(payload, dict)]
    blockers: list[str] = []
    if missing_sources:
        blockers.append("source_artifacts_missing")
    if not (isinstance(stage212, dict) and stage212.get("decision") == STAGE212_SUBMITTED):
        blockers.append("stage212_submission_not_ready")
    templates = [deepcopy(template) for template in (stage190.get("execution_templates", []) if isinstance(stage190, dict) else [])]
    calibration = deepcopy(stage190.get("calibration_template", {})) if isinstance(stage190, dict) else {}
    if calibration:
        templates.append(calibration)
    if len(templates) != 21:
        blockers.append("stage190_template_count_mismatch")
    submissions = stage212.get("submission_records", []) if isinstance(stage212, dict) else []
    submission_by_key = {str(record.get("packet_id") or "__calibration__"): record for record in submissions if record.get("runtime_job_id")}
    fetcher = fetch_result or _real_fetch_result
    collection_records: list[dict[str, Any]] = []
    collected_templates: list[dict[str, Any]] = []
    if not blockers:
        for template in templates:
            key = _template_key(template)
            submission = submission_by_key.get(key)
            if not submission:
                blockers.append("submission_record_missing")
                collection_records.append({"packet_id": template.get("packet_id", ""), "runtime_job_id": "", "status": "missing_submission", "counts_recorded": False, "error_type": ""})
                continue
            runtime_job_id = str(submission["runtime_job_id"])
            try:
                fetched = fetcher(runtime_job_id)
                status = str(fetched.get("status", ""))
                counts_by_circuit = fetched.get("counts_by_circuit", [])
                rows_key = "raw_counts_by_state" if template.get("template_type") == "replacement_known_state_calibration_counts" else "raw_counts_by_row"
                rows = template.get(rows_key, [])
                counts_ready = status in {"DONE", "COMPLETED", "done", "completed"} and len(counts_by_circuit) == len(rows)
                if counts_ready:
                    completed_at = datetime.now(UTC).isoformat()
                    for row, counts in zip(rows, counts_by_circuit, strict=True):
                        row["counts"] = canonicalize_counts(counts)
                    template["job_or_task_ids"] = [runtime_job_id]
                    template["backend_metadata"] = submission.get("backend_metadata", {})
                    template["submitted_at_utc"] = submission.get("submitted_at_utc", "")
                    template["completed_at_utc"] = completed_at
                    template["status"] = "counts_collected"
                    collected_templates.append(template)
                else:
                    blockers.append("runtime_jobs_not_complete")
                collection_records.append(
                    {
                        "packet_id": template.get("packet_id", ""),
                        "runtime_job_id": runtime_job_id,
                        "status": status,
                        "counts_recorded": counts_ready,
                        "error_type": "",
                    }
                )
            except Exception as exc:  # noqa: BLE001
                blockers.append("runtime_result_collection_failed")
                collection_records.append({"packet_id": template.get("packet_id", ""), "runtime_job_id": runtime_job_id, "status": "collection_failed", "counts_recorded": False, "error_type": type(exc).__name__})
    collected_count = sum(1 for record in collection_records if record["counts_recorded"])
    decision = "FULL_REPLACEMENT_RESULT_COUNTS_COLLECTED_READY_FOR_CALIBRATION" if not blockers else "FULL_REPLACEMENT_RESULT_COLLECTION_PENDING_OR_BLOCKED"
    return {
        "schema_version": STAGE214_SCHEMA_VERSION,
        "stage": "stage214_full_replacement_result_collector",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": decision,
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "blockers": sorted(set(blockers)),
        "expected_template_count": 21,
        "collected_template_count": collected_count,
        "collection_records": collection_records,
        "collected_templates": collected_templates,
        "no_hardware_submission": True,
        "provider_credentials_required": True,
        "secret_values_recorded": False,
        "runnable_commands_recorded": False,
        "claim_boundary": {
            "supported": ["provider result-count collection for completed full replacement Stage212 jobs"],
            "excluded": ["new hardware submission", "calibration pass/fail", "robustness or auditability interpretation"],
        },
        "next_gate": "After all counts are collected, validate known-state calibration before computing full 4096-shot hardware metrics.",
    }


def write_stage214_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_keys = (
        "schema_version", "stage", "status", "objective", "decision", "source_artifacts",
        "missing_source_artifacts", "blockers", "expected_template_count", "collected_template_count",
        "no_hardware_submission", "provider_credentials_required", "secret_values_recorded",
        "runnable_commands_recorded", "claim_boundary", "next_gate",
    )
    manifest = {key: result[key] for key in manifest_keys}
    manifest["result_path"] = str((output_dir / "results.json").as_posix())
    manifest["summary_csv_path"] = str((output_dir / "summary.csv").as_posix())
    paths = {"manifest": str(output_dir / "manifest.json"), "result": str(output_dir / "results.json"), "summary_csv": str(output_dir / "summary.csv")}
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=("packet_id", "runtime_job_id", "status", "counts_recorded", "error_type"))
        writer.writeheader()
        for record in result["collection_records"]:
            writer.writerow({field: record.get(field) for field in writer.fieldnames})
    return paths


def print_stage214_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"collected_template_count: {result['collected_template_count']}/{result['expected_template_count']}")
    print(f"blockers: {', '.join(result['blockers'])}")
    print(f"next_gate: {result['next_gate']}")
