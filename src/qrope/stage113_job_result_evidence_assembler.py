from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


STAGE113_SCHEMA_VERSION = "qrope_stage113_job_result_evidence_assembler_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE112_JOB_MANIFEST = DEFAULT_ARTIFACT_ROOT / "stage112_provider_execution_manifest" / "job_manifest.jsonl"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage113_job_result_evidence_assembler"
DEFAULT_PROVIDER_RESULTS = DEFAULT_OUTPUT_DIR / "provider_job_results.jsonl"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _load_jsonl(path: Path) -> list[dict[str, Any]] | None:
    if not path.exists():
        return None
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def _counts_present(counts: Any) -> bool:
    if not isinstance(counts, dict) or not counts:
        return False
    try:
        return sum(int(value) for value in counts.values()) > 0
    except (TypeError, ValueError):
        return False


def _unique(values: list[Any]) -> list[Any]:
    seen = set()
    out = []
    for value in values:
        marker = json.dumps(value, sort_keys=True) if isinstance(value, (dict, list)) else str(value)
        if marker not in seen and value not in (None, "", []):
            seen.add(marker)
            out.append(value)
    return out


def _job_result_records(jobs: list[dict[str, Any]], results: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    result_by_job = {str(record.get("job_id")): record for record in results if record.get("job_id")}
    records = []
    missing = []
    for job in jobs:
        job_id = str(job["job_id"])
        result = result_by_job.get(job_id)
        reasons = []
        if result is None:
            reasons.append("job_result_missing")
        elif not _counts_present(result.get("counts")):
            reasons.append("counts_missing")
        record = {
            "job_id": job_id,
            "provider": job.get("provider"),
            "window_id": job.get("window_id"),
            "job_kind": job.get("job_kind"),
            "target_evidence_path": job.get("target_evidence_path"),
            "target_counts_container": job.get("target_counts_container"),
            "target_counts_key": job.get("target_counts_key"),
            "ready": not reasons,
            "missing_evidence": reasons,
        }
        records.append(record)
        if reasons:
            missing.append(record)
    return records, missing


def _base_payload(template_path: Path) -> dict[str, Any]:
    payload = _load_json(template_path)
    if not isinstance(payload, dict):
        return {}
    payload = json.loads(json.dumps(payload))
    payload["status"] = "assembled_from_stage113_results"
    payload["no_hardware_submission"] = False
    return payload


def _apply_results(jobs: list[dict[str, Any]], results_by_job: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    assembled: dict[str, dict[str, Any]] = {}
    jobs_by_target: dict[str, list[dict[str, Any]]] = {}
    for job in jobs:
        jobs_by_target.setdefault(str(job["target_evidence_path"]), []).append(job)

    for target, target_jobs in jobs_by_target.items():
        first = target_jobs[0]
        payload = _base_payload(Path(str(first["template_path"])))
        job_results = [results_by_job[str(job["job_id"])] for job in target_jobs]
        payload["job_or_task_ids"] = _unique([result.get("job_or_task_id") for result in job_results] + [item for result in job_results for item in result.get("job_or_task_ids", [])])
        metadata = _unique([result.get("backend_metadata") for result in job_results])
        if metadata:
            payload["backend_metadata"] = metadata[0]
        submitted = sorted(str(result.get("submitted_at_utc")) for result in job_results if result.get("submitted_at_utc"))
        completed = sorted(str(result.get("completed_at_utc")) for result in job_results if result.get("completed_at_utc"))
        if submitted:
            payload["submitted_at_utc"] = submitted[0]
        if completed:
            payload["completed_at_utc"] = completed[-1]
        container = str(first["target_counts_container"])
        key_name = "state" if container == "raw_counts_by_state" else "row_id"
        counts_by_key = {str(job["target_counts_key"]): results_by_job[str(job["job_id"])]["counts"] for job in target_jobs}
        for row in payload.get(container, []):
            key = str(row.get(key_name))
            if key in counts_by_key:
                row["counts"] = {str(k): int(v) for k, v in counts_by_key[key].items()}
        assembled[target] = payload
    return assembled


def run_stage113_assembler(
    *,
    stage112_job_manifest_path: Path = DEFAULT_STAGE112_JOB_MANIFEST,
    provider_results_path: Path = DEFAULT_PROVIDER_RESULTS,
    write_evidence: bool = False,
    provider: str | None = None,
) -> dict[str, Any]:
    jobs = _load_jsonl(stage112_job_manifest_path)
    results = _load_jsonl(provider_results_path)
    sources = [
        (stage112_job_manifest_path, jobs),
        (provider_results_path, results),
    ]
    missing_sources = [str(path.as_posix()) for path, payload in sources if payload is None]
    selected_jobs = [job for job in jobs or [] if provider is None or job.get("provider") == provider]
    selected_job_ids = {str(job.get("job_id")) for job in selected_jobs}
    selected_results = [
        result for result in results or [] if provider is None or str(result.get("job_id")) in selected_job_ids
    ]
    job_records, missing_job_records = _job_result_records(selected_jobs, selected_results)
    ready = (
        bool(selected_jobs)
        and bool(selected_results)
        and not missing_sources
        and not missing_job_records
        and len(selected_results) >= len(selected_jobs)
    )
    assembled_paths: list[str] = []
    if ready and write_evidence:
        results_by_job = {str(record["job_id"]): record for record in selected_results}
        for path_text, payload in _apply_results(selected_jobs, results_by_job).items():
            path = Path(path_text)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
            assembled_paths.append(str(path.as_posix()))
    return {
        "schema_version": STAGE113_SCHEMA_VERSION,
        "stage": "stage113_job_result_evidence_assembler",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": (
            "JOB_RESULTS_ASSEMBLED_INTO_STAGE109_EVIDENCE"
            if ready and write_evidence
            else "JOB_RESULTS_READY_FOR_STAGE109_EVIDENCE_ASSEMBLY"
            if ready
            else "JOB_RESULT_EVIDENCE_ASSEMBLY_BLOCKED_RESULTS_MISSING"
        ),
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "write_evidence": write_evidence,
        "provider_scope": provider or "all",
        "job_count": len(selected_jobs),
        "available_job_count": len(jobs or []),
        "provider_result_count": len(selected_results),
        "available_provider_result_count": len(results or []),
        "ready_job_result_count": sum(1 for record in job_records if record["ready"]),
        "missing_job_result_count": len(missing_job_records),
        "assembled_evidence_count": len(assembled_paths),
        "assembled_evidence_paths": assembled_paths,
        "job_records": job_records,
        "missing_job_records": missing_job_records,
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "claim_boundary": {
            "supported": [
                "a deterministic assembler from Stage 112 job results into Stage 109-compatible evidence files",
                "optional provider-scoped evidence assembly for first-provider execution",
                "per-job missing count detection before evidence files are written",
                "a non-submitting bridge between provider runners and calibration/packet evidence intake",
            ],
            "excluded": [
                "hardware job submission",
                "provider credential validation",
                "Stage 101 calibration verification",
                "Stage 103 metric interpretation",
                "a noisy-hardware robustness result",
            ],
        },
        "next_gate": (
            "Produce provider_job_results.jsonl for every selected Stage 112 job, rerun this assembler with --write-evidence, "
            "then run Stage 101, Stage 103, Stage 109, and Stage 110 in order."
        ),
    }


def write_stage113_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "write_evidence": result["write_evidence"],
        "provider_scope": result["provider_scope"],
        "job_count": result["job_count"],
        "available_job_count": result["available_job_count"],
        "provider_result_count": result["provider_result_count"],
        "available_provider_result_count": result["available_provider_result_count"],
        "ready_job_result_count": result["ready_job_result_count"],
        "missing_job_result_count": result["missing_job_result_count"],
        "assembled_evidence_count": result["assembled_evidence_count"],
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
        writer = csv.DictWriter(
            handle,
            fieldnames=("job_id", "provider", "window_id", "job_kind", "ready", "target_evidence_path", "missing_evidence"),
        )
        writer.writeheader()
        for record in result["job_records"]:
            writer.writerow(
                {
                    "job_id": record["job_id"],
                    "provider": record["provider"],
                    "window_id": record["window_id"],
                    "job_kind": record["job_kind"],
                    "ready": record["ready"],
                    "target_evidence_path": record["target_evidence_path"],
                    "missing_evidence": "; ".join(record["missing_evidence"]),
                }
            )
    return paths


def print_stage113_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"provider_scope: {result['provider_scope']}")
    print(f"job_count: {result['job_count']}")
    print(f"provider_result_count: {result['provider_result_count']}")
    print(f"ready_job_result_count: {result['ready_job_result_count']}")
    print(f"missing_job_result_count: {result['missing_job_result_count']}")
    print(f"assembled_evidence_count: {result['assembled_evidence_count']}")
    print(f"next_gate: {result['next_gate']}")
