from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


STAGE114_SCHEMA_VERSION = "qrope_stage114_provider_result_capture_contract_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE112_JOB_MANIFEST = DEFAULT_ARTIFACT_ROOT / "stage112_provider_execution_manifest" / "job_manifest.jsonl"
DEFAULT_STAGE113_MANIFEST = DEFAULT_ARTIFACT_ROOT / "stage113_job_result_evidence_assembler" / "manifest.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage114_provider_result_capture_contract"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)
REQUIRED_RESULT_FIELDS = (
    "job_id",
    "job_or_task_id",
    "backend_metadata",
    "submitted_at_utc",
    "completed_at_utc",
    "counts",
)


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _load_jsonl(path: Path) -> list[dict[str, Any]] | None:
    if not path.exists():
        return None
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _capture_stub(job: dict[str, Any]) -> dict[str, Any]:
    return {
        "job_id": job["job_id"],
        "job_or_task_id": "",
        "backend_metadata": {
            "provider": job.get("provider"),
            "backend": "",
            "window_id": job.get("window_id"),
            "job_kind": job.get("job_kind"),
        },
        "submitted_at_utc": "",
        "completed_at_utc": "",
        "counts": {},
    }


def _group_jobs(jobs: list[dict[str, Any]]) -> dict[tuple[str, str], list[dict[str, Any]]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for job in jobs:
        key = (str(job.get("provider")), str(job.get("window_id")))
        grouped.setdefault(key, []).append(job)
    return grouped


def run_stage114_contract(
    *,
    stage112_job_manifest_path: Path = DEFAULT_STAGE112_JOB_MANIFEST,
    stage113_manifest_path: Path = DEFAULT_STAGE113_MANIFEST,
) -> dict[str, Any]:
    jobs = _load_jsonl(stage112_job_manifest_path)
    stage113 = _load_json(stage113_manifest_path)
    sources = [
        (stage112_job_manifest_path, jobs),
        (stage113_manifest_path, stage113),
    ]
    missing_sources = [str(path.as_posix()) for path, payload in sources if payload is None]
    grouped = _group_jobs(jobs or [])
    shard_records = []
    for (provider, window_id), shard_jobs in sorted(grouped.items()):
        shard_records.append(
            {
                "provider": provider,
                "window_id": window_id,
                "job_count": len(shard_jobs),
                "job_manifest_shard_path": f"job_shards/{provider}/{window_id}/jobs.jsonl",
                "result_stub_path": f"result_stubs/{provider}/{window_id}/provider_job_results.stub.jsonl",
                "result_output_path": f"provider_results/{provider}/{window_id}/provider_job_results.jsonl",
            }
        )
    return {
        "schema_version": STAGE114_SCHEMA_VERSION,
        "stage": "stage114_provider_result_capture_contract",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": (
            "PROVIDER_RESULT_CAPTURE_CONTRACT_PREPARED_RESULTS_REQUIRED"
            if not missing_sources and shard_records
            else "PROVIDER_RESULT_CAPTURE_CONTRACT_INCOMPLETE"
        ),
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "stage113_decision": stage113.get("decision") if isinstance(stage113, dict) else None,
        "job_count": len(jobs or []),
        "shard_count": len(shard_records),
        "required_result_fields": list(REQUIRED_RESULT_FIELDS),
        "shard_records": shard_records,
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "claim_boundary": {
            "supported": [
                "a provider result JSONL contract for Stage 112 jobs",
                "per-provider/window job shards and fillable result stubs",
                "a no-submission handoff format for provider runners before Stage 113 assembly",
            ],
            "excluded": [
                "hardware job submission",
                "provider credentials or secret values",
                "completed provider results",
                "Stage 101 calibration verification",
                "a noisy-hardware robustness result",
            ],
        },
        "next_gate": (
            "Run provider execution against the job shards, write result JSONL records with the required fields, concatenate "
            "validated results into Stage 113 provider_job_results.jsonl, then assemble evidence."
        ),
    }


def write_stage114_outputs(result: dict[str, Any], jobs: list[dict[str, Any]] | None = None, output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    jobs_by_key = _group_jobs(jobs or [])
    shard_paths: list[str] = []
    stub_paths: list[str] = []
    for record in result["shard_records"]:
        key = (record["provider"], record["window_id"])
        shard_jobs = jobs_by_key.get(key, [])
        shard_path = output_dir / record["job_manifest_shard_path"]
        stub_path = output_dir / record["result_stub_path"]
        shard_path.parent.mkdir(parents=True, exist_ok=True)
        stub_path.parent.mkdir(parents=True, exist_ok=True)
        shard_path.write_text("".join(json.dumps(job, sort_keys=True) + "\n" for job in shard_jobs), encoding="utf-8")
        stub_path.write_text("".join(json.dumps(_capture_stub(job), sort_keys=True) + "\n" for job in shard_jobs), encoding="utf-8")
        shard_paths.append(str(shard_path.as_posix()))
        stub_paths.append(str(stub_path.as_posix()))

    schema_payload = {
        "schema_version": STAGE114_SCHEMA_VERSION,
        "record_type": "provider_job_result",
        "required_fields": list(REQUIRED_RESULT_FIELDS),
        "field_notes": {
            "job_id": "Must match exactly one Stage 112 job_id.",
            "job_or_task_id": "Provider job/task identifier; do not include secrets.",
            "backend_metadata": "Non-secret provider/backend/window metadata.",
            "submitted_at_utc": "ISO-8601 UTC timestamp.",
            "completed_at_utc": "ISO-8601 UTC timestamp.",
            "counts": "Non-empty bitstring count mapping using provider output decoded into canonical keys expected by the job.",
        },
    }
    (output_dir / "provider_job_result_schema.json").write_text(json.dumps(schema_payload, indent=2, sort_keys=True), encoding="utf-8")
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "stage113_decision": result["stage113_decision"],
        "job_count": result["job_count"],
        "shard_count": result["shard_count"],
        "required_result_fields": result["required_result_fields"],
        "job_shard_paths": shard_paths,
        "result_stub_paths": stub_paths,
        "provider_job_result_schema_path": str((output_dir / "provider_job_result_schema.json").as_posix()),
        "result_path": str((output_dir / "results.json").as_posix()),
        "summary_csv_path": str((output_dir / "summary.csv").as_posix()),
        "no_hardware_submission": result["no_hardware_submission"],
        "provider_credentials_required": result["provider_credentials_required"],
        "secret_values_recorded": result["secret_values_recorded"],
        "claim_boundary": result["claim_boundary"],
        "next_gate": result["next_gate"],
    }
    paths = {
        "manifest": str(output_dir / "manifest.json"),
        "result": str(output_dir / "results.json"),
        "summary_csv": str(output_dir / "summary.csv"),
        "schema": str(output_dir / "provider_job_result_schema.json"),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=("provider", "window_id", "job_count", "job_manifest_shard_path", "result_stub_path", "result_output_path"))
        writer.writeheader()
        for record in result["shard_records"]:
            writer.writerow(record)
    return paths


def print_stage114_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"job_count: {result['job_count']}")
    print(f"shard_count: {result['shard_count']}")
    print(f"next_gate: {result['next_gate']}")
