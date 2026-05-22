from __future__ import annotations

import csv
import json
import os
from pathlib import Path
from typing import Any, Callable

from qrope.env_utils import load_local_dotenv
from qrope.stage205_reduced_scope_hardware_submission import DEFAULT_OUTPUT_DIR as STAGE205_OUTPUT_DIR
from qrope.stage99_matched_fixed_width_encoding_packet_freezer import OBJECTIVE


STAGE206_SCHEMA_VERSION = "qrope_stage206_reduced_scope_job_status_poll_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE205_RESULTS = STAGE205_OUTPUT_DIR / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage206_reduced_scope_job_status_poll_100usd"
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


def _real_fetch_status(runtime_job_id: str) -> dict[str, Any]:
    from qiskit_ibm_runtime import QiskitRuntimeService

    token = os.environ.get("IBM_QUANTUM_TOKEN") or os.environ.get("QISKIT_IBM_TOKEN")
    instance = os.environ.get("IBM_QUANTUM_INSTANCE_CRN")
    if not token or not instance:
        raise RuntimeError("IBM token or instance missing")
    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=token, instance=instance)
    job = service.job(runtime_job_id)
    status = job.status()
    return {"runtime_job_id": runtime_job_id, "status": _status_text(status)}


def run_stage206_reduced_scope_job_status_poll(
    *,
    stage205_results_path: Path = DEFAULT_STAGE205_RESULTS,
    fetch_status: Callable[[str], dict[str, Any]] | None = None,
    load_dotenv: bool = False,
) -> dict[str, Any]:
    if load_dotenv:
        load_local_dotenv(Path(".env"))
    stage205 = _load_json(stage205_results_path)
    missing_sources = [] if isinstance(stage205, dict) else [str(stage205_results_path.as_posix())]
    blockers: list[str] = []
    if missing_sources:
        blockers.append("source_artifacts_missing")
    stage205_ready = bool(isinstance(stage205, dict) and stage205.get("decision") == STAGE205_SUBMITTED)
    if not stage205_ready:
        blockers.append("stage205_submission_not_ready")
    submissions = [record for record in (stage205.get("submission_records", []) if isinstance(stage205, dict) else []) if record.get("runtime_job_id")]
    if len(submissions) != 21:
        blockers.append("stage205_runtime_job_count_mismatch")
    poll_records: list[dict[str, Any]] = []
    status_fetcher = fetch_status or _real_fetch_status
    if not blockers:
        for record in submissions:
            runtime_job_id = str(record["runtime_job_id"])
            try:
                fetched = status_fetcher(runtime_job_id)
                status = str(fetched.get("status", ""))
                poll_records.append(
                    {
                        "template_type": record.get("template_type"),
                        "packet_id": record.get("packet_id", ""),
                        "runtime_job_id": runtime_job_id,
                        "status": status,
                        "poll_error_type": "",
                    }
                )
            except Exception as exc:  # noqa: BLE001 - status polling must preserve other job IDs.
                poll_records.append(
                    {
                        "template_type": record.get("template_type"),
                        "packet_id": record.get("packet_id", ""),
                        "runtime_job_id": runtime_job_id,
                        "status": "poll_failed",
                        "poll_error_type": type(exc).__name__,
                    }
                )
                blockers.append("runtime_job_status_poll_failed")
    done_statuses = {"DONE", "COMPLETED", "JobStatus.DONE", "done", "completed"}
    failed_statuses = {"ERROR", "CANCELLED", "CANCELLED - RAN TOO LONG", "JobStatus.ERROR", "JobStatus.CANCELLED", "failed", "cancelled"}
    completed_count = sum(1 for record in poll_records if record["status"] in done_statuses)
    failed_count = sum(1 for record in poll_records if record["status"] in failed_statuses)
    if failed_count:
        blockers.append("runtime_jobs_failed_or_cancelled")
    if blockers:
        decision = "REDUCED_SCOPE_JOB_STATUS_POLL_BLOCKED_OR_INCOMPLETE"
    elif completed_count == len(poll_records) and poll_records:
        decision = "REDUCED_SCOPE_RUNTIME_JOBS_COMPLETE_READY_FOR_RESULT_COLLECTION"
    else:
        decision = "REDUCED_SCOPE_RUNTIME_JOBS_SUBMITTED_RESULTS_PENDING"
    return {
        "schema_version": STAGE206_SCHEMA_VERSION,
        "stage": "stage206_reduced_scope_job_status_poll",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": decision,
        "source_artifacts": [str(stage205_results_path.as_posix())],
        "missing_source_artifacts": missing_sources,
        "blockers": sorted(set(blockers)),
        "expected_runtime_job_count": 21,
        "observed_runtime_job_count": len(submissions),
        "polled_runtime_job_count": len(poll_records),
        "completed_runtime_job_count": completed_count,
        "failed_runtime_job_count": failed_count,
        "poll_records": poll_records,
        "no_hardware_submission": True,
        "provider_credentials_required": True,
        "secret_values_recorded": False,
        "runnable_commands_recorded": False,
        "claim_boundary": {
            "supported": [
                "status polling for submitted reduced-scope IBM Runtime jobs",
                "job completion state required before result collection",
            ],
            "excluded": [
                "new hardware job submission",
                "provider-side result counts",
                "calibration pass/fail",
                "robustness or auditability interpretation",
            ],
        },
        "next_gate": "When all Runtime jobs are complete, collect provider counts and populate reduced-scope evidence records.",
    }


def write_stage206_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
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
        "expected_runtime_job_count",
        "observed_runtime_job_count",
        "polled_runtime_job_count",
        "completed_runtime_job_count",
        "failed_runtime_job_count",
        "no_hardware_submission",
        "provider_credentials_required",
        "secret_values_recorded",
        "runnable_commands_recorded",
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
        writer = csv.DictWriter(handle, fieldnames=("template_type", "packet_id", "runtime_job_id", "status", "poll_error_type"))
        writer.writeheader()
        for record in result["poll_records"]:
            writer.writerow({field: record.get(field) for field in writer.fieldnames})
    return paths


def print_stage206_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"polled_runtime_job_count: {result['polled_runtime_job_count']}/{result['expected_runtime_job_count']}")
    print(f"completed_runtime_job_count: {result['completed_runtime_job_count']}")
    print(f"failed_runtime_job_count: {result['failed_runtime_job_count']}")
    print(f"blockers: {', '.join(result['blockers'])}")
    print(f"next_gate: {result['next_gate']}")
