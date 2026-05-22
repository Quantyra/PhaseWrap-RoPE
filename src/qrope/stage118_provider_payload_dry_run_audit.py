from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any


STAGE118_SCHEMA_VERSION = "qrope_stage118_provider_payload_dry_run_audit_v1"
PAYLOAD_SCHEMA_VERSION = "qrope_stage118_provider_submission_payload_dry_run_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE116_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage116_provider_runner_plan" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage118_provider_payload_dry_run_audit"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _provider_submission_kind(provider: str) -> str:
    if provider == "ibm_runtime":
        return "ibm_runtime_openqasm3_sampler"
    if provider == "amazon_braket":
        return "amazon_braket_openqasm3_task"
    return f"{provider}_openqasm3_submission"


def _payload_path(output_dir: Path, provider: str, window_id: str) -> Path:
    return output_dir / "dry_run_payloads" / provider / window_id / "submission_payloads.jsonl"


def _compile_payload(job: dict[str, Any], runner_record: dict[str, Any]) -> dict[str, Any]:
    openqasm3 = str(job.get("openqasm3", ""))
    provider = str(runner_record.get("provider", job.get("provider", "")))
    return {
        "schema_version": PAYLOAD_SCHEMA_VERSION,
        "dry_run_only": True,
        "provider": provider,
        "provider_submission_kind": _provider_submission_kind(provider),
        "window_id": runner_record.get("window_id", job.get("window_id")),
        "job_id": job.get("job_id"),
        "job_kind": job.get("job_kind"),
        "shots": job.get("shots"),
        "openqasm3": openqasm3,
        "openqasm3_sha256": hashlib.sha256(openqasm3.encode("utf-8")).hexdigest(),
        "target_counts_container": job.get("target_counts_container"),
        "target_counts_key": job.get("target_counts_key"),
        "target_evidence_path": job.get("target_evidence_path"),
        "provider_result_path": runner_record.get("provider_result_path"),
    }


def _record_missing_evidence(job: dict[str, Any], runner_record: dict[str, Any]) -> list[str]:
    missing = []
    for field in ("job_id", "job_kind", "provider", "window_id", "shots", "openqasm3", "target_evidence_path"):
        if not job.get(field):
            missing.append(f"job_missing_{field}")
    if job.get("provider") != runner_record.get("provider"):
        missing.append("job_provider_mismatch")
    if job.get("window_id") != runner_record.get("window_id"):
        missing.append("job_window_mismatch")
    if not str(job.get("openqasm3", "")).startswith("OPENQASM 3.0;"):
        missing.append("job_openqasm3_header_missing")
    try:
        if int(job.get("shots", 0)) <= 0:
            missing.append("job_shots_not_positive")
    except (TypeError, ValueError):
        missing.append("job_shots_not_integer")
    return missing


def _runner_payload_record(runner_record: dict[str, Any], *, output_dir: Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    shard_path = Path(str(runner_record.get("job_shard_path", "")))
    provider = str(runner_record.get("provider", ""))
    window_id = str(runner_record.get("window_id", ""))
    jobs = _load_jsonl(shard_path)
    payloads = [_compile_payload(job, runner_record) for job in jobs]
    job_ids = [str(job.get("job_id", "")) for job in jobs]
    duplicate_count = len(job_ids) - len(set(job_ids))
    missing = []
    if not shard_path.exists():
        missing.append("job_shard_missing")
    if int(runner_record.get("job_count", 0)) != len(jobs):
        missing.append("job_count_mismatch")
    if duplicate_count:
        missing.append("duplicate_job_ids")
    for job in jobs:
        missing.extend(_record_missing_evidence(job, runner_record))
    payload_output_path = _payload_path(output_dir, provider, window_id)
    return (
        {
            "provider": provider,
            "window_id": window_id,
            "job_shard_path": str(shard_path.as_posix()),
            "payload_output_path": str(payload_output_path.as_posix()),
            "expected_job_count": runner_record.get("job_count", 0),
            "compiled_payload_count": len(payloads),
            "calibration_payload_count": sum(1 for job in jobs if job.get("job_kind") == "known_state_calibration"),
            "packet_payload_count": sum(1 for job in jobs if job.get("job_kind") == "matched_packet_row"),
            "duplicate_job_id_count": duplicate_count,
            "missing_evidence": sorted(set(missing)),
            "ready": not missing and bool(payloads),
        },
        payloads,
    )


def run_stage118_audit(*, stage116_results_path: Path = DEFAULT_STAGE116_RESULTS, output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, Any]:
    stage116 = _load_json(stage116_results_path)
    missing_sources = [] if isinstance(stage116, dict) else [str(stage116_results_path.as_posix())]
    payload_records = []
    payloads_by_path: dict[str, list[dict[str, Any]]] = {}
    if isinstance(stage116, dict):
        for runner_record in stage116.get("runner_records", []):
            payload_record, payloads = _runner_payload_record(runner_record, output_dir=output_dir)
            payload_records.append(payload_record)
            payloads_by_path[payload_record["payload_output_path"]] = payloads
    ready = bool(payload_records) and all(record["ready"] for record in payload_records) and not missing_sources
    total_expected = sum(int(record["expected_job_count"]) for record in payload_records)
    total_compiled = sum(int(record["compiled_payload_count"]) for record in payload_records)
    return {
        "schema_version": STAGE118_SCHEMA_VERSION,
        "stage": "stage118_provider_payload_dry_run_audit",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": (
            "PROVIDER_PAYLOAD_DRY_RUN_COMPILED_EXECUTION_BLOCKED"
            if ready
            else "PROVIDER_PAYLOAD_DRY_RUN_INCOMPLETE"
        ),
        "source_artifacts": [str(stage116_results_path.as_posix())],
        "missing_source_artifacts": missing_sources,
        "stage116_decision": stage116.get("decision") if isinstance(stage116, dict) else None,
        "runner_count": len(payload_records),
        "ready_payload_record_count": sum(1 for record in payload_records if record["ready"]),
        "expected_job_count": total_expected,
        "compiled_payload_count": total_compiled,
        "payload_records": payload_records,
        "payloads_by_path": payloads_by_path,
        "no_hardware_submission": True,
        "provider_credentials_required": True,
        "secret_values_recorded": False,
        "claim_boundary": {
            "supported": [
                "offline provider-shaped payload compilation for every Stage 116 runner job",
                "stable non-secret dry-run payload files for provider-runner implementation",
                "confirmation that execution remains blocked before live provider submission",
            ],
            "excluded": [
                "hardware job submission",
                "provider credentials or secret values",
                "completed provider result records",
                "Stage 113 evidence assembly",
                "a noisy-hardware robustness result",
            ],
        },
        "next_gate": (
            "Clear Stage 106/111 provider readiness, then implement live runner submission against these payload "
            "records while preserving the Stage 114 result contract."
        ),
    }


def write_stage118_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    for payload_path_text, payloads in result["payloads_by_path"].items():
        payload_path = Path(payload_path_text)
        payload_path.parent.mkdir(parents=True, exist_ok=True)
        payload_path.write_text("".join(json.dumps(payload, sort_keys=True) + "\n" for payload in payloads), encoding="utf-8")
    result_without_payloads = {key: value for key, value in result.items() if key != "payloads_by_path"}
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "stage116_decision": result["stage116_decision"],
        "runner_count": result["runner_count"],
        "ready_payload_record_count": result["ready_payload_record_count"],
        "expected_job_count": result["expected_job_count"],
        "compiled_payload_count": result["compiled_payload_count"],
        "payload_output_paths": list(result["payloads_by_path"]),
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
    (output_dir / "results.json").write_text(json.dumps(result_without_payloads, indent=2, sort_keys=True), encoding="utf-8")
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=(
                "provider",
                "window_id",
                "expected_job_count",
                "compiled_payload_count",
                "calibration_payload_count",
                "packet_payload_count",
                "ready",
                "missing_evidence",
            ),
        )
        writer.writeheader()
        for record in result["payload_records"]:
            writer.writerow(
                {
                    "provider": record["provider"],
                    "window_id": record["window_id"],
                    "expected_job_count": record["expected_job_count"],
                    "compiled_payload_count": record["compiled_payload_count"],
                    "calibration_payload_count": record["calibration_payload_count"],
                    "packet_payload_count": record["packet_payload_count"],
                    "ready": record["ready"],
                    "missing_evidence": "; ".join(record["missing_evidence"]),
                }
            )
    return paths


def print_stage118_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"compiled_payload_count: {result['compiled_payload_count']}/{result['expected_job_count']}")
    print(f"ready_payload_record_count: {result['ready_payload_record_count']}/{result['runner_count']}")
    print(f"next_gate: {result['next_gate']}")
