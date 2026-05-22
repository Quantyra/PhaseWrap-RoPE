from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


STAGE150_SCHEMA_VERSION = "qrope_stage150_first_provider_result_lineage_audit_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE112_JOB_MANIFEST = DEFAULT_ARTIFACT_ROOT / "stage112_provider_execution_manifest" / "job_manifest.jsonl"
DEFAULT_STAGE114_MANIFEST = DEFAULT_ARTIFACT_ROOT / "stage114_provider_result_capture_contract" / "manifest.json"
DEFAULT_STAGE145_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage145_first_provider_evidence_path_audit" / "results.json"
DEFAULT_STAGE148_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage148_first_provider_statistical_interpretation_gate" / "results.json"
DEFAULT_STAGE149_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage149_first_provider_guarded_runner_contract_audit" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage150_first_provider_result_lineage_audit"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)
REQUIRED_JOB_FIELDS = (
    "job_id",
    "job_kind",
    "openqasm3",
    "provider",
    "shots",
    "target_counts_container",
    "target_counts_key",
    "target_evidence_path",
    "template_path",
    "window_id",
)
REQUIRED_RESULT_FIELDS = ("job_id", "job_or_task_id", "backend_metadata", "submitted_at_utc", "completed_at_utc", "counts")
REQUIRED_BACKEND_METADATA_FIELDS = ("provider", "backend", "window_id", "job_kind")
VALID_JOB_KINDS = ("known_state_calibration", "matched_packet_row")


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _load_jsonl(path: Path) -> list[dict[str, Any]] | None:
    if not path.exists():
        return None
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _first_provider(stage145: dict[str, Any] | None, stage149: dict[str, Any] | None) -> str:
    for payload in (stage149, stage145):
        if isinstance(payload, dict) and payload.get("first_unlock_provider"):
            return str(payload["first_unlock_provider"])
    return ""


def _missing_job_fields(job: dict[str, Any]) -> list[str]:
    missing = [field for field in REQUIRED_JOB_FIELDS if job.get(field) in (None, "", [])]
    if job.get("provider") and job.get("provider") != "ibm_runtime":
        missing.append("provider_scope_mismatch")
    if job.get("job_kind") not in VALID_JOB_KINDS:
        missing.append("job_kind_supported")
    if not str(job.get("openqasm3", "")).startswith("OPENQASM 3.0;"):
        missing.append("openqasm3_header")
    try:
        if int(job.get("shots", 0)) <= 0:
            missing.append("shots_positive")
    except (TypeError, ValueError):
        missing.append("shots_integer")
    if job.get("job_kind") == "known_state_calibration" and not job.get("state"):
        missing.append("state")
    if job.get("job_kind") == "matched_packet_row":
        for field in ("packet_id", "row_id", "source_lane_id", "circuit_template", "encoding_family"):
            if job.get(field) in (None, "", []):
                missing.append(field)
    return sorted(set(missing))


def _stage114_shard_index(stage114: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    if not isinstance(stage114, dict):
        return {}
    indexed: dict[str, dict[str, Any]] = {}
    for shard_path_text in stage114.get("job_shard_paths", []):
        shard_path = Path(str(shard_path_text))
        shard_jobs = _load_jsonl(shard_path) or []
        for job in shard_jobs:
            job_id = str(job.get("job_id", ""))
            if job_id:
                indexed[job_id] = {
                    "job_shard_path": shard_path.as_posix(),
                    "job_shard_provider": job.get("provider"),
                    "job_shard_window_id": job.get("window_id"),
                }
    return indexed


def _stage148_windows(stage148: dict[str, Any] | None, provider: str) -> set[str]:
    if not isinstance(stage148, dict):
        return set()
    windows = {
        str(record.get("window_id"))
        for record in stage148.get("calibration_records", [])
        if record.get("provider") == provider and record.get("window_id")
    }
    windows.update(
        str(record.get("window_id"))
        for record in stage148.get("lane_records", [])
        if record.get("provider") == provider and record.get("window_id")
    )
    return windows


def _stage107_window_prefix(window_id: str) -> str:
    return f"logs/automated_stage_gates/stage107_window_execution_orchestrator/windows/{window_id}/"


def _job_records(
    jobs: list[dict[str, Any]],
    provider: str,
    *,
    stage114_shard_index: dict[str, dict[str, Any]],
    stage148_windows: set[str],
) -> list[dict[str, Any]]:
    provider_jobs = [job for job in jobs if job.get("provider") == provider]
    job_id_counts: dict[str, int] = {}
    for job in provider_jobs:
        job_id = str(job.get("job_id", ""))
        if job_id:
            job_id_counts[job_id] = job_id_counts.get(job_id, 0) + 1
    records = []
    for job in provider_jobs:
        missing = _missing_job_fields(job)
        job_id = str(job.get("job_id", ""))
        window_id = str(job.get("window_id", ""))
        shard_record = stage114_shard_index.get(job_id)
        target_evidence_path = str(job.get("target_evidence_path", ""))
        if job_id_counts.get(job_id, 0) > 1:
            missing.append("job_id_unique")
        if not shard_record:
            missing.append("stage114_shard_assignment")
        elif shard_record.get("job_shard_provider") != provider or shard_record.get("job_shard_window_id") != window_id:
            missing.append("stage114_shard_scope_match")
        if stage148_windows and window_id not in stage148_windows:
            missing.append("stage148_window_alignment")
        if window_id and not target_evidence_path.startswith(_stage107_window_prefix(window_id)):
            missing.append("stage107_window_evidence_path")
        missing = sorted(set(missing))
        records.append(
            {
                "job_id": job_id,
                "provider": job.get("provider"),
                "window_id": window_id,
                "job_kind": job.get("job_kind"),
                "target_evidence_path": target_evidence_path,
                "template_path": job.get("template_path"),
                "job_shard_path": shard_record.get("job_shard_path") if shard_record else "",
                "ready": not missing,
                "missing_evidence": missing,
            }
        )
    return records


def _window_records(job_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for record in job_records:
        grouped.setdefault(str(record.get("window_id")), []).append(record)
    out = []
    for window_id, records in sorted(grouped.items()):
        calibration_count = sum(1 for record in records if record.get("job_kind") == "known_state_calibration")
        packet_count = sum(1 for record in records if record.get("job_kind") == "matched_packet_row")
        ready_count = sum(1 for record in records if record["ready"])
        out.append(
            {
                "window_id": window_id,
                "job_count": len(records),
                "ready_job_count": ready_count,
                "calibration_job_count": calibration_count,
                "packet_job_count": packet_count,
                "ready": ready_count == len(records) and calibration_count > 0 and packet_count > 0,
            }
        )
    return out


def run_stage150_audit(
    *,
    stage112_job_manifest_path: Path = DEFAULT_STAGE112_JOB_MANIFEST,
    stage114_manifest_path: Path = DEFAULT_STAGE114_MANIFEST,
    stage145_results_path: Path = DEFAULT_STAGE145_RESULTS,
    stage148_results_path: Path = DEFAULT_STAGE148_RESULTS,
    stage149_results_path: Path = DEFAULT_STAGE149_RESULTS,
) -> dict[str, Any]:
    jobs = _load_jsonl(stage112_job_manifest_path)
    stage114 = _load_json(stage114_manifest_path)
    stage145 = _load_json(stage145_results_path)
    stage148 = _load_json(stage148_results_path)
    stage149 = _load_json(stage149_results_path)
    sources = [
        (stage112_job_manifest_path, jobs),
        (stage114_manifest_path, stage114),
        (stage145_results_path, stage145),
        (stage148_results_path, stage148),
        (stage149_results_path, stage149),
    ]
    missing_sources = [str(path.as_posix()) for path, payload in sources if payload is None]
    provider = _first_provider(stage145, stage149)
    stage114_shards = _stage114_shard_index(stage114)
    stage148_window_ids = _stage148_windows(stage148, provider)
    records = _job_records(
        jobs or [],
        provider,
        stage114_shard_index=stage114_shards,
        stage148_windows=stage148_window_ids,
    )
    windows = _window_records(records)
    ready_job_count = sum(1 for record in records if record["ready"])
    stage114_fields = list(stage114.get("required_result_fields", [])) if isinstance(stage114, dict) else []
    result_fields_ready = all(field in stage114_fields for field in REQUIRED_RESULT_FIELDS)
    stage148_bound = bool(isinstance(stage148, dict) and stage148.get("provider_scope") == provider)
    stage149_ready = bool(
        isinstance(stage149, dict)
        and stage149.get("decision") == "FIRST_PROVIDER_GUARDED_RUNNER_CONTRACT_READY_CUTOVER_BLOCKED"
        and stage149.get("synthetic_contract_ready_count") == stage149.get("synthetic_contract_check_count")
    )
    ready = (
        bool(provider)
        and bool(records)
        and not missing_sources
        and ready_job_count == len(records)
        and all(record["ready"] for record in windows)
        and result_fields_ready
        and stage148_bound
        and bool(stage148_window_ids)
        and stage149_ready
    )
    calibration_job_count = sum(1 for record in records if record.get("job_kind") == "known_state_calibration")
    packet_job_count = sum(1 for record in records if record.get("job_kind") == "matched_packet_row")
    return {
        "schema_version": STAGE150_SCHEMA_VERSION,
        "stage": "stage150_first_provider_result_lineage_audit",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": (
            "FIRST_PROVIDER_RESULT_LINEAGE_CONTRACT_READY_EXECUTION_BLOCKED"
            if ready
            else "FIRST_PROVIDER_RESULT_LINEAGE_CONTRACT_INCOMPLETE"
        ),
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "first_unlock_provider": provider,
        "job_count": len(records),
        "ready_job_count": ready_job_count,
        "calibration_job_count": calibration_job_count,
        "packet_job_count": packet_job_count,
        "window_count": len(windows),
        "ready_window_count": sum(1 for record in windows if record["ready"]),
        "stage114_shard_assignment_count": sum(1 for record in records if record.get("job_shard_path")),
        "stage114_required_result_fields": stage114_fields,
        "required_result_fields": list(REQUIRED_RESULT_FIELDS),
        "required_backend_metadata_fields": list(REQUIRED_BACKEND_METADATA_FIELDS),
        "stage114_result_fields_ready": result_fields_ready,
        "stage148_provider_bound": stage148_bound,
        "stage148_window_ids": sorted(stage148_window_ids),
        "stage149_guarded_runner_contract_ready": stage149_ready,
        "job_records": records,
        "window_records": windows,
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "claim_boundary": {
            "supported": [
                "first-provider job lineage from Stage 112 jobs to Stage 114 shards, result fields, and Stage 107 target evidence paths",
                "window-level IBM calibration and matched-packet job completeness before provider result interpretation",
                "binding of expected result lineage to Stage 148 statistical interpretation and Stage 149 guarded runner checks",
            ],
            "excluded": [
                "provider credential values",
                "hardware job submission",
                "live provider SDK client creation",
                "real provider result records",
                "a noisy-hardware robustness or auditability conclusion",
            ],
        },
        "next_gate": (
            "After IBM cutover and Stage 133 authorization, provider result records must preserve these job IDs, target "
            "evidence paths, Stage 114 result fields, and backend metadata fields "
            f"{', '.join(REQUIRED_BACKEND_METADATA_FIELDS)} before Stage 115 collection."
        ),
    }


def write_stage150_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "first_unlock_provider": result["first_unlock_provider"],
        "job_count": result["job_count"],
        "ready_job_count": result["ready_job_count"],
        "calibration_job_count": result["calibration_job_count"],
        "packet_job_count": result["packet_job_count"],
        "window_count": result["window_count"],
        "ready_window_count": result["ready_window_count"],
        "stage114_shard_assignment_count": result["stage114_shard_assignment_count"],
        "stage114_result_fields_ready": result["stage114_result_fields_ready"],
        "stage148_provider_bound": result["stage148_provider_bound"],
        "stage148_window_ids": result["stage148_window_ids"],
        "stage149_guarded_runner_contract_ready": result["stage149_guarded_runner_contract_ready"],
        "required_result_fields": result["required_result_fields"],
        "required_backend_metadata_fields": result["required_backend_metadata_fields"],
        "no_hardware_submission": result["no_hardware_submission"],
        "provider_credentials_required": result["provider_credentials_required"],
        "secret_values_recorded": result["secret_values_recorded"],
        "result_path": str((output_dir / "results.json").as_posix()),
        "summary_csv_path": str((output_dir / "summary.csv").as_posix()),
        "claim_boundary": result["claim_boundary"],
        "next_gate": result["next_gate"],
    }
    paths = {
        "manifest": str(output_dir / "manifest.json"),
        "result": str(output_dir / "results.json"),
        "summary_csv": str(output_dir / "summary.csv"),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=("window_id", "job_count", "ready_job_count", "calibration_job_count", "packet_job_count", "ready"))
        writer.writeheader()
        for record in result["window_records"]:
            writer.writerow(record)
    return paths


def print_stage150_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"first_unlock_provider: {result['first_unlock_provider']}")
    print(f"ready_job_count: {result['ready_job_count']}/{result['job_count']}")
    print(f"calibration_job_count: {result['calibration_job_count']}")
    print(f"packet_job_count: {result['packet_job_count']}")
    print(f"ready_window_count: {result['ready_window_count']}/{result['window_count']}")
    print(f"stage148_provider_bound: {result['stage148_provider_bound']}")
    print(f"stage149_guarded_runner_contract_ready: {result['stage149_guarded_runner_contract_ready']}")
    print(f"next_gate: {result['next_gate']}")
