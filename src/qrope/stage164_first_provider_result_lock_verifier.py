from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any


STAGE164_SCHEMA_VERSION = "qrope_stage164_first_provider_result_lock_verifier_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE163_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage163_first_provider_prerun_lock" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage164_first_provider_result_lock_verifier"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)
STAGE163_READY = "FIRST_PROVIDER_PRERUN_LOCK_READY_AWAITING_APPROVAL"


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


def _counts_present(counts: Any) -> bool:
    if not isinstance(counts, dict) or not counts:
        return False
    try:
        return sum(int(value) for value in counts.values()) > 0
    except (TypeError, ValueError):
        return False


def _window_verification(lock: dict[str, Any]) -> dict[str, Any]:
    job_shard_path = Path(str(lock.get("job_shard_path") or ""))
    provider_results_path = Path(str(lock.get("provider_results_path") or ""))
    expected_job_count = int(lock.get("job_count") or 0)
    expected_hash = str(lock.get("job_shard_sha256") or "")
    current_hash = _sha256(job_shard_path) if job_shard_path.exists() else ""
    results = _load_jsonl(provider_results_path)
    result_ids = [str(record.get("job_id") or "") for record in results]
    duplicate_ids = sorted({job_id for job_id in result_ids if job_id and result_ids.count(job_id) > 1})
    invalid_count = sum(1 for record in results if not record.get("job_id") or not _counts_present(record.get("counts")))
    blockers = []
    if not job_shard_path.exists():
        blockers.append("job_shard_missing")
    if current_hash != expected_hash:
        blockers.append("job_shard_hash_mismatch")
    if not provider_results_path.exists():
        blockers.append("provider_results_missing")
    if len(results) != expected_job_count:
        blockers.append("provider_result_count_mismatch")
    if duplicate_ids:
        blockers.append("duplicate_result_job_ids")
    if invalid_count:
        blockers.append("invalid_result_records")
    return {
        "provider": lock.get("provider"),
        "window_id": lock.get("window_id"),
        "job_shard_path": str(job_shard_path.as_posix()),
        "expected_job_shard_sha256": expected_hash,
        "current_job_shard_sha256": current_hash,
        "job_shard_hash_matches": bool(current_hash and current_hash == expected_hash),
        "provider_results_path": str(provider_results_path.as_posix()),
        "expected_result_record_count": expected_job_count,
        "provider_results_file_exists": provider_results_path.exists(),
        "provider_result_record_count": len(results),
        "duplicate_result_job_count": len(duplicate_ids),
        "invalid_result_record_count": invalid_count,
        "ready": not blockers,
        "blockers": sorted(set(blockers)),
    }


def run_stage164_result_lock_verifier(
    *,
    stage163_results_path: Path = DEFAULT_STAGE163_RESULTS,
) -> dict[str, Any]:
    stage163 = _load_json(stage163_results_path)
    missing_sources = [] if isinstance(stage163, dict) else [str(stage163_results_path.as_posix())]
    locks = stage163.get("window_locks", []) if isinstance(stage163, dict) else []
    verifications = [_window_verification(lock) for lock in locks if isinstance(lock, dict)]
    blockers = []
    if missing_sources:
        blockers.append("stage163_lock_missing")
    if not isinstance(stage163, dict) or stage163.get("decision") != STAGE163_READY:
        blockers.append("stage163_lock_not_ready")
    if not verifications:
        blockers.append("window_locks_missing")
    if any(not record["ready"] for record in verifications):
        blockers.append("window_result_lock_verification_blockers_present")
    expected_result_count = sum(int(record.get("expected_result_record_count") or 0) for record in verifications)
    provider_result_count = sum(int(record.get("provider_result_record_count") or 0) for record in verifications)
    hash_match_count = sum(1 for record in verifications if record["job_shard_hash_matches"])
    all_ready = not blockers
    decision = (
        "FIRST_PROVIDER_RESULT_LOCK_VERIFICATION_INCOMPLETE"
        if missing_sources
        else "FIRST_PROVIDER_RESULT_LOCK_VERIFIED_READY_FOR_STAGE115"
        if all_ready
        else "FIRST_PROVIDER_RESULT_LOCK_VERIFICATION_BLOCKED_RESULTS_MISSING"
        if set(blockers) == {"window_result_lock_verification_blockers_present"}
        and provider_result_count < expected_result_count
        else "FIRST_PROVIDER_RESULT_LOCK_VERIFICATION_BLOCKED"
    )
    return {
        "schema_version": STAGE164_SCHEMA_VERSION,
        "stage": "stage164_first_provider_result_lock_verifier",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": decision,
        "source_artifacts": [str(stage163_results_path.as_posix())],
        "missing_source_artifacts": missing_sources,
        "stage163_decision": stage163.get("decision") if isinstance(stage163, dict) else None,
        "first_unlock_provider": stage163.get("first_unlock_provider") if isinstance(stage163, dict) else None,
        "aggregate_job_shard_lock_sha256": stage163.get("aggregate_job_shard_lock_sha256") if isinstance(stage163, dict) else None,
        "window_count": len(verifications),
        "hash_match_count": hash_match_count,
        "expected_result_record_count": expected_result_count,
        "provider_result_record_count": provider_result_count,
        "missing_result_record_count": max(expected_result_count - provider_result_count, 0),
        "window_verifications": verifications,
        "blockers": sorted(set(blockers)),
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "runnable_commands_recorded": False,
        "claim_boundary": {
            "supported": [
                "verification that current Stage114 IBM job shards still match the Stage163 pre-run lock",
                "verification that provider result record counts match the locked job counts before Stage115/Stage113 acceptance",
                "duplicate and empty-count result detection at the lock-verification boundary",
            ],
            "excluded": [
                "hardware job submission",
                "provider credentials or secret values",
                "Stage115 collection or Stage113 evidence assembly",
                "a noisy-hardware robustness or auditability conclusion",
            ],
        },
        "next_gate": (
            "After live execution, require this verifier to pass before treating Stage115 provider result collection "
            "and Stage113 evidence assembly as lock-consistent."
        ),
    }


def write_stage164_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "stage163_decision": result["stage163_decision"],
        "first_unlock_provider": result["first_unlock_provider"],
        "aggregate_job_shard_lock_sha256": result["aggregate_job_shard_lock_sha256"],
        "window_count": result["window_count"],
        "hash_match_count": result["hash_match_count"],
        "expected_result_record_count": result["expected_result_record_count"],
        "provider_result_record_count": result["provider_result_record_count"],
        "missing_result_record_count": result["missing_result_record_count"],
        "blockers": result["blockers"],
        "no_hardware_submission": result["no_hardware_submission"],
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
                "job_shard_hash_matches",
                "expected_result_record_count",
                "provider_result_record_count",
                "ready",
                "blockers",
            ),
        )
        writer.writeheader()
        for record in result["window_verifications"]:
            writer.writerow({**{field: record.get(field) for field in writer.fieldnames}, "blockers": "; ".join(record["blockers"])})
    return paths


def print_stage164_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"hash_match_count: {result['hash_match_count']}/{result['window_count']}")
    print(f"provider_result_record_count: {result['provider_result_record_count']}/{result['expected_result_record_count']}")
    print(f"missing_result_record_count: {result['missing_result_record_count']}")
    print(f"blockers: {', '.join(result['blockers'])}")
    print(f"next_gate: {result['next_gate']}")
