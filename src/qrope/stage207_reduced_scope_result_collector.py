from __future__ import annotations

import csv
import json
import os
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

from qrope.env_utils import load_local_dotenv
from qrope.provider_adapters.common import canonicalize_counts
from qrope.stage203_reduced_scope_execution_package import DEFAULT_OUTPUT_DIR as STAGE203_OUTPUT_DIR
from qrope.stage205_reduced_scope_hardware_submission import DEFAULT_OUTPUT_DIR as STAGE205_OUTPUT_DIR
from qrope.stage99_matched_fixed_width_encoding_packet_freezer import OBJECTIVE


STAGE207_SCHEMA_VERSION = "qrope_stage207_reduced_scope_result_collector_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE205_RESULTS = STAGE205_OUTPUT_DIR / "results.json"
DEFAULT_STAGE203_RESULTS = STAGE203_OUTPUT_DIR / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage207_reduced_scope_result_collector_100usd"
STAGE205_SUBMITTED = "REDUCED_SCOPE_HARDWARE_SUBMITTED_AWAITING_RESULTS"


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _status_text(status: Any) -> str:
    value = getattr(status, "value", None)
    if value:
        return str(value)
    name = getattr(status, "name", None)
    if name:
        return str(name)
    return str(status)


def _extract_counts_list(result: Any) -> list[dict[str, int]]:
    records = []
    for pub_result in result:
        data = getattr(pub_result, "data", None)
        if data is None:
            raise RuntimeError("IBM result pub has no data")
        for register_name in ("c", "cr", "meas"):
            register = getattr(data, register_name, None)
            if register is not None and callable(getattr(register, "get_counts", None)):
                records.append(canonicalize_counts(register.get_counts()))
                break
        else:
            if callable(getattr(data, "get_counts", None)):
                records.append(canonicalize_counts(data.get_counts()))
            else:
                raise RuntimeError("IBM result pub has no counts register")
    return records


def _real_fetch_result(runtime_job_id: str) -> dict[str, Any]:
    from qiskit_ibm_runtime import QiskitRuntimeService

    token = os.environ.get("IBM_QUANTUM_TOKEN") or os.environ.get("QISKIT_IBM_TOKEN")
    instance = os.environ.get("IBM_QUANTUM_INSTANCE_CRN")
    if not token or not instance:
        raise RuntimeError("IBM token or instance missing")
    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=token, instance=instance)
    job = service.job(runtime_job_id)
    status = _status_text(job.status())
    if status not in {"DONE", "COMPLETED", "done", "completed"}:
        return {"runtime_job_id": runtime_job_id, "status": status, "counts_by_circuit": []}
    return {"runtime_job_id": runtime_job_id, "status": status, "counts_by_circuit": _extract_counts_list(job.result())}


def _template_key(template: dict[str, Any]) -> str:
    return str(template.get("packet_id") or "__calibration__")


def run_stage207_reduced_scope_result_collector(
    *,
    stage205_results_path: Path = DEFAULT_STAGE205_RESULTS,
    stage203_results_path: Path = DEFAULT_STAGE203_RESULTS,
    fetch_result: Callable[[str], dict[str, Any]] | None = None,
    load_dotenv: bool = False,
) -> dict[str, Any]:
    if load_dotenv:
        load_local_dotenv(Path(".env"))
    stage205 = _load_json(stage205_results_path)
    stage203 = _load_json(stage203_results_path)
    sources = [(stage205_results_path, stage205), (stage203_results_path, stage203)]
    missing_sources = [str(path.as_posix()) for path, payload in sources if not isinstance(payload, dict)]
    blockers: list[str] = []
    if missing_sources:
        blockers.append("source_artifacts_missing")
    if not (isinstance(stage205, dict) and stage205.get("decision") == STAGE205_SUBMITTED):
        blockers.append("stage205_submission_not_ready")
    templates = [deepcopy(template) for template in (stage203.get("execution_templates", []) if isinstance(stage203, dict) else [])]
    calibration = deepcopy(stage203.get("calibration_template", {})) if isinstance(stage203, dict) else {}
    if calibration:
        templates.append(calibration)
    if len(templates) != 21:
        blockers.append("stage203_template_count_mismatch")
    submissions = stage205.get("submission_records", []) if isinstance(stage205, dict) else []
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
                rows_key = "raw_counts_by_state" if template.get("template_type") == "reduced_scope_known_state_calibration_counts" else "raw_counts_by_row"
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
    if blockers:
        decision = "REDUCED_SCOPE_RESULT_COLLECTION_PENDING_OR_BLOCKED"
    else:
        decision = "REDUCED_SCOPE_RESULT_COUNTS_COLLECTED_READY_FOR_CALIBRATION"
    return {
        "schema_version": STAGE207_SCHEMA_VERSION,
        "stage": "stage207_reduced_scope_result_collector",
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
            "supported": ["provider result-count collection for completed Stage205 jobs"],
            "excluded": ["new hardware submission", "calibration pass/fail", "robustness or auditability interpretation"],
        },
        "next_gate": "After all counts are collected, validate known-state calibration before computing hardware robustness and auditability metrics.",
    }


def write_stage207_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
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


def print_stage207_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"collected_template_count: {result['collected_template_count']}/{result['expected_template_count']}")
    print(f"blockers: {', '.join(result['blockers'])}")
    print(f"next_gate: {result['next_gate']}")
