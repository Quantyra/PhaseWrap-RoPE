from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any


STAGE163_SCHEMA_VERSION = "qrope_stage163_first_provider_prerun_lock_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE157_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage157_first_provider_live_run_approval_packet" / "results.json"
DEFAULT_STAGE162_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage162_first_provider_approval_dossier" / "results.json"
DEFAULT_STAGE114_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage114_provider_result_capture_contract"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage163_first_provider_prerun_lock"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)
STAGE157_READY = "FIRST_PROVIDER_LIVE_RUN_APPROVAL_PACKET_READY"
STAGE162_READY = "FIRST_PROVIDER_APPROVAL_DOSSIER_READY_FOR_HUMAN_GO_NO_GO"
PROVIDER = "ibm_runtime"


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _line_count(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def _int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _job_shard_path(root: Path, provider: str, window_id: str) -> Path:
    return root / "job_shards" / provider / window_id / "jobs.jsonl"


def _result_path(root: Path, provider: str, window_id: str) -> Path:
    return root / "provider_results" / provider / window_id / "provider_job_results.jsonl"


def _approved_records(stage157: dict[str, Any] | None, provider: str) -> list[dict[str, Any]]:
    if not isinstance(stage157, dict):
        return []
    return [
        record
        for record in stage157.get("approval_records", [])
        if isinstance(record, dict)
        and record.get("provider") == provider
        and record.get("command_authorized") is True
        and record.get("live_submit_command_available") is True
    ]


def _window_lock(stage114_output_dir: Path, provider: str, approval: dict[str, Any]) -> dict[str, Any]:
    window_id = str(approval.get("window_id") or "")
    job_shard = _job_shard_path(stage114_output_dir, provider, window_id)
    result_path = _result_path(stage114_output_dir, provider, window_id)
    jobs = _load_jsonl(job_shard)
    result_line_count = _line_count(result_path)
    blockers = []
    if not job_shard.exists():
        blockers.append("job_shard_missing")
    if _int(approval.get("job_count")) != len(jobs):
        blockers.append("approved_job_count_mismatch")
    if result_line_count > 0:
        blockers.append("provider_results_not_empty")
    return {
        "provider": provider,
        "window_id": window_id,
        "approved_job_count": approval.get("job_count"),
        "job_shard_path": str(job_shard.as_posix()),
        "job_shard_exists": job_shard.exists(),
        "job_shard_sha256": _sha256(job_shard) if job_shard.exists() else "",
        "job_count": len(jobs),
        "total_shots": sum(_int(job.get("shots")) for job in jobs),
        "provider_results_path": str(result_path.as_posix()),
        "provider_results_file_exists": result_path.exists(),
        "provider_results_line_count": result_line_count,
        "ready": not blockers,
        "blockers": sorted(set(blockers)),
    }


def run_stage163_prerun_lock(
    *,
    stage157_results_path: Path = DEFAULT_STAGE157_RESULTS,
    stage162_results_path: Path = DEFAULT_STAGE162_RESULTS,
    stage114_output_dir: Path = DEFAULT_STAGE114_OUTPUT_DIR,
) -> dict[str, Any]:
    stage157 = _load_json(stage157_results_path)
    stage162 = _load_json(stage162_results_path)
    sources = [(stage157_results_path, stage157), (stage162_results_path, stage162)]
    missing_sources = [str(path.as_posix()) for path, payload in sources if not isinstance(payload, dict)]
    provider = str(stage157.get("first_unlock_provider") if isinstance(stage157, dict) else PROVIDER)
    approval_records = _approved_records(stage157, provider)
    window_locks = [_window_lock(stage114_output_dir, provider, record) for record in approval_records]
    blockers = []
    if missing_sources:
        blockers.append("source_artifacts_missing")
    if provider != PROVIDER:
        blockers.append("first_provider_not_ibm_runtime")
    if not isinstance(stage157, dict) or stage157.get("decision") != STAGE157_READY:
        blockers.append("stage157_not_ready")
    if not isinstance(stage162, dict) or stage162.get("decision") != STAGE162_READY:
        blockers.append("stage162_dossier_not_ready")
    if not window_locks:
        blockers.append("approved_window_locks_missing")
    if any(not record["ready"] for record in window_locks):
        blockers.append("window_lock_blockers_present")
    approved_jobs = sum(_int(record.get("approved_job_count")) for record in window_locks)
    locked_jobs = sum(record["job_count"] for record in window_locks)
    if approved_jobs != locked_jobs:
        blockers.append("approved_job_count_lock_mismatch")
    expected_jobs = _int(stage162.get("authorized_first_provider_job_count")) if isinstance(stage162, dict) else 0
    if expected_jobs and locked_jobs != expected_jobs:
        blockers.append("stage162_job_count_lock_mismatch")
    aggregate_input = "|".join(record["job_shard_sha256"] for record in window_locks)
    aggregate_hash = hashlib.sha256(aggregate_input.encode("utf-8")).hexdigest() if aggregate_input else ""
    decision = (
        "FIRST_PROVIDER_PRERUN_LOCK_INCOMPLETE"
        if missing_sources
        else "FIRST_PROVIDER_PRERUN_LOCK_READY_AWAITING_APPROVAL"
        if not blockers
        else "FIRST_PROVIDER_PRERUN_LOCK_BLOCKED"
    )
    return {
        "schema_version": STAGE163_SCHEMA_VERSION,
        "stage": "stage163_first_provider_prerun_lock",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": decision,
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "stage157_decision": stage157.get("decision") if isinstance(stage157, dict) else None,
        "stage162_decision": stage162.get("decision") if isinstance(stage162, dict) else None,
        "first_unlock_provider": provider,
        "approval_phrase_required": stage157.get("approval_phrase_required") if isinstance(stage157, dict) else None,
        "window_count": len(window_locks),
        "approved_job_count": approved_jobs,
        "locked_job_count": locked_jobs,
        "locked_total_shots": sum(record["total_shots"] for record in window_locks),
        "aggregate_job_shard_lock_sha256": aggregate_hash,
        "window_locks": window_locks,
        "blockers": sorted(set(blockers)),
        "no_hardware_submission": True,
        "explicit_user_approval_required": True,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "runnable_commands_recorded": False,
        "claim_boundary": {
            "supported": [
                "pre-run immutable hash lock for the approved IBM Runtime Stage114 job shards",
                "expected provider-result file paths and empty-result checks before live execution",
                "job and shot totals tied to Stage157 approval and Stage162 dossier readiness",
            ],
            "excluded": [
                "hardware job submission",
                "runnable Stage133 command strings",
                "provider credentials or secret values",
                "IBM credit balance or dollar cost verification",
                "real provider result records",
                "a noisy-hardware robustness or auditability conclusion",
            ],
        },
        "next_gate": (
            "If the exact approval phrase is provided and live execution occurs, compare later result collection "
            "against this lock before accepting Stage115/Stage113 evidence."
        ),
    }


def write_stage163_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "stage157_decision": result["stage157_decision"],
        "stage162_decision": result["stage162_decision"],
        "first_unlock_provider": result["first_unlock_provider"],
        "window_count": result["window_count"],
        "approved_job_count": result["approved_job_count"],
        "locked_job_count": result["locked_job_count"],
        "locked_total_shots": result["locked_total_shots"],
        "aggregate_job_shard_lock_sha256": result["aggregate_job_shard_lock_sha256"],
        "blockers": result["blockers"],
        "no_hardware_submission": result["no_hardware_submission"],
        "explicit_user_approval_required": result["explicit_user_approval_required"],
        "provider_credentials_required": result["provider_credentials_required"],
        "secret_values_recorded": result["secret_values_recorded"],
        "runnable_commands_recorded": result["runnable_commands_recorded"],
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
            fieldnames=(
                "provider",
                "window_id",
                "job_count",
                "total_shots",
                "job_shard_sha256",
                "provider_results_path",
                "provider_results_line_count",
                "ready",
                "blockers",
            ),
        )
        writer.writeheader()
        for record in result["window_locks"]:
            writer.writerow({**{field: record.get(field) for field in writer.fieldnames}, "blockers": "; ".join(record["blockers"])})
    return paths


def print_stage163_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"first_unlock_provider: {result['first_unlock_provider']}")
    print(f"window_count: {result['window_count']}")
    print(f"locked_job_count: {result['locked_job_count']}")
    print(f"locked_total_shots: {result['locked_total_shots']}")
    print(f"aggregate_job_shard_lock_sha256: {result['aggregate_job_shard_lock_sha256']}")
    print(f"blockers: {', '.join(result['blockers'])}")
    print(f"next_gate: {result['next_gate']}")
