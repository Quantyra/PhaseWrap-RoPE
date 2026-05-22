from __future__ import annotations

import argparse
import importlib
import json
from pathlib import Path
from typing import Any


DEFAULT_STAGE111_RESULTS = Path("logs") / "automated_stage_gates" / "stage111_provider_sdk_backend_discovery" / "results.json"
DEFAULT_STAGE118_RESULTS = Path("logs") / "automated_stage_gates" / "stage118_provider_payload_dry_run_audit" / "results.json"


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(record, sort_keys=True) + "\n" for record in records), encoding="utf-8")


def _provider_record(stage111: dict[str, Any] | None, provider: str) -> dict[str, Any] | None:
    if not stage111:
        return None
    for record in stage111.get("provider_records", []):
        if record.get("provider") == provider:
            return record
    return None


def _payload_record(stage118: dict[str, Any] | None, provider: str, window_id: str) -> dict[str, Any] | None:
    if not stage118:
        return None
    for record in stage118.get("payload_records", []):
        if record.get("provider") == provider and record.get("window_id") == window_id:
            return record
    return None


def _window_id_from_jobs(jobs: list[dict[str, Any]]) -> str:
    window_ids = {str(job.get("window_id", "")) for job in jobs if job.get("window_id")}
    if len(window_ids) == 1:
        return next(iter(window_ids))
    return ""


def _validate_result_record(record: dict[str, Any], expected_job_ids: set[str]) -> list[str]:
    missing = []
    for field in ("job_id", "job_or_task_id", "backend_metadata", "submitted_at_utc", "completed_at_utc", "counts"):
        if field not in record or record.get(field) in (None, "", []):
            missing.append(field)
    if record.get("job_id") not in expected_job_ids:
        missing.append("unknown_job_id")
    counts = record.get("counts")
    if not isinstance(counts, dict) or not counts:
        missing.append("counts")
    else:
        try:
            if sum(int(value) for value in counts.values()) <= 0:
                missing.append("counts")
        except (TypeError, ValueError):
            missing.append("counts")
    return sorted(set(missing))


def _load_submitter(import_path: str) -> Any:
    module_name, separator, attr_name = import_path.partition(":")
    if not separator or not module_name or not attr_name:
        raise ValueError("submitter import path must use module:callable")
    module = importlib.import_module(module_name)
    submitter = getattr(module, attr_name)
    if not callable(submitter):
        raise TypeError(f"submitter is not callable: {import_path}")
    return submitter


def run_guarded_provider_runner(provider: str, argv: list[str] | None = None, submitter: Any | None = None) -> int:
    parser = argparse.ArgumentParser(description=f"Guarded no-submit runner for {provider} Stage 112 jobs.")
    parser.add_argument("--job-shard", type=Path, required=True)
    parser.add_argument("--provider-results", type=Path, required=True)
    parser.add_argument("--stage111-results", type=Path, default=DEFAULT_STAGE111_RESULTS)
    parser.add_argument("--stage118-results", type=Path, default=DEFAULT_STAGE118_RESULTS)
    parser.add_argument("--allow-live-submit", action="store_true")
    parser.add_argument("--submitter", help="Import path for a provider submitter callable, formatted as module:callable.")
    args = parser.parse_args(argv)

    stage111 = _load_json(args.stage111_results)
    stage118 = _load_json(args.stage118_results)
    jobs = _load_jsonl(args.job_shard)
    record = _provider_record(stage111, provider)
    window_id = _window_id_from_jobs(jobs)
    print(f"provider: {provider}")
    print(f"job_shard: {args.job_shard}")
    print(f"provider_results: {args.provider_results}")
    print(f"window_id: {window_id}")
    print(f"job_count: {len(jobs)}")
    if record is None:
        print("decision: PROVIDER_RUNNER_BLOCKED_STAGE111_RECORD_MISSING")
        return 2
    if record.get("status") != "ready":
        print("decision: PROVIDER_RUNNER_BLOCKED_STAGE111_NOT_READY")
        print(f"blockers: {', '.join(str(item) for item in record.get('blockers', []))}")
        return 2
    if not args.allow_live_submit:
        print("decision: PROVIDER_RUNNER_READY_LIVE_SUBMIT_FLAG_REQUIRED")
        return 3
    payload_record = _payload_record(stage118, provider, window_id)
    if payload_record is None:
        print("decision: PROVIDER_RUNNER_BLOCKED_STAGE118_PAYLOAD_RECORD_MISSING")
        return 4
    payloads = _load_jsonl(Path(str(payload_record.get("payload_output_path", ""))))
    if len(payloads) != len(jobs):
        print("decision: PROVIDER_RUNNER_BLOCKED_STAGE118_PAYLOAD_COUNT_MISMATCH")
        print(f"payload_count: {len(payloads)}")
        return 4
    if submitter is None and args.submitter:
        try:
            submitter = _load_submitter(args.submitter)
        except (ImportError, AttributeError, TypeError, ValueError) as exc:
            print("decision: PROVIDER_RUNNER_BLOCKED_SUBMITTER_IMPORT_FAILED")
            print(f"submitter_error: {exc}")
            return 4
    if submitter is None:
        print("decision: PROVIDER_RUNNER_LIVE_SUBMISSION_ADAPTER_REQUIRED")
        return 4
    results = submitter(provider=provider, jobs=jobs, payloads=payloads)
    if not isinstance(results, list):
        print("decision: PROVIDER_RUNNER_BLOCKED_SUBMITTER_RETURNED_NON_LIST")
        return 5
    expected_job_ids = {str(job.get("job_id")) for job in jobs}
    invalid = []
    seen = set()
    for result in results:
        job_id = str(result.get("job_id", ""))
        if job_id in seen:
            invalid.append({"job_id": job_id, "missing_evidence": ["duplicate_job_id"]})
        seen.add(job_id)
        problems = _validate_result_record(result, expected_job_ids)
        if problems:
            invalid.append({"job_id": job_id, "missing_evidence": problems})
    missing_job_ids = sorted(expected_job_ids - seen)
    if len(results) != len(jobs) or missing_job_ids or invalid:
        print("decision: PROVIDER_RUNNER_BLOCKED_SUBMITTER_RESULT_CONTRACT_INVALID")
        print(f"result_count: {len(results)}")
        print(f"missing_job_count: {len(missing_job_ids)}")
        print(f"invalid_result_count: {len(invalid)}")
        return 5
    _write_jsonl(args.provider_results, results)
    print("decision: PROVIDER_RUNNER_RESULTS_WRITTEN")
    print(f"result_count: {len(results)}")
    return 0
