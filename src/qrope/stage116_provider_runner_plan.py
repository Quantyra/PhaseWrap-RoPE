from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


STAGE116_SCHEMA_VERSION = "qrope_stage116_provider_runner_plan_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE111_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage111_provider_sdk_backend_discovery" / "results.json"
DEFAULT_STAGE114_MANIFEST = DEFAULT_ARTIFACT_ROOT / "stage114_provider_result_capture_contract" / "manifest.json"
DEFAULT_STAGE118_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage118_provider_payload_dry_run_audit" / "results.json"
DEFAULT_STAGE129_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage129_live_cutover_authorization_audit" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage116_provider_runner_plan"
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


def _provider_status(stage111: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    if not stage111:
        return {}
    return {str(record.get("provider")): record for record in stage111.get("provider_records", [])}


def _provider_command(provider: str, shard_path: str, result_path: str, stage111_path: Path, stage118_path: Path, stage129_path: Path) -> str:
    if provider == "ibm_runtime":
        return (
            "python scripts/provider_runners/run_ibm_runtime_stage112_jobs.py "
            f"--job-shard {shard_path} --provider-results {result_path} "
            f"--stage111-results {stage111_path.as_posix()} --stage118-results {stage118_path.as_posix()} "
            f"--stage129-results {stage129_path.as_posix()}"
        )
    if provider == "amazon_braket":
        return (
            "python scripts/provider_runners/run_amazon_braket_stage112_jobs.py "
            f"--job-shard {shard_path} --provider-results {result_path} "
            f"--stage111-results {stage111_path.as_posix()} --stage118-results {stage118_path.as_posix()} "
            f"--stage129-results {stage129_path.as_posix()}"
        )
    return f"UNSUPPORTED_PROVIDER {provider}"


def _runner_record(
    shard_path: str,
    stage114_manifest: dict[str, Any],
    provider_records: dict[str, dict[str, Any]],
    *,
    stage111_results_path: Path,
    stage118_results_path: Path,
    stage129_results_path: Path,
) -> dict[str, Any]:
    shard = Path(shard_path)
    parts = shard.parts
    provider = parts[-3] if len(parts) >= 4 else ""
    window_id = parts[-2] if len(parts) >= 3 else shard.parent.name
    output_root = Path("logs") / "automated_stage_gates" / "stage114_provider_result_capture_contract"
    result_path = str((output_root / "provider_results" / provider / window_id / "provider_job_results.jsonl").as_posix())
    jobs = _load_jsonl(shard)
    provider_record = provider_records.get(provider, {})
    provider_ready = provider_record.get("status") == "ready"
    blockers = [] if provider_ready else ["stage111_provider_not_ready"]
    blockers.extend(str(item) for item in provider_record.get("blockers", []))
    return {
        "provider": provider,
        "window_id": window_id,
        "job_shard_path": str(shard.as_posix()),
        "provider_result_path": result_path,
        "job_count": len(jobs),
        "calibration_job_count": sum(1 for job in jobs if job.get("job_kind") == "known_state_calibration"),
        "packet_job_count": sum(1 for job in jobs if job.get("job_kind") == "matched_packet_row"),
        "provider_ready": provider_ready,
        "status": "ready_to_run" if provider_ready else "blocked",
        "blockers": sorted(set(blockers)),
        "runner_command": _provider_command(
            provider,
            str(shard.as_posix()),
            result_path,
            stage111_results_path,
            stage118_results_path,
            stage129_results_path,
        ),
        "required_result_fields": stage114_manifest.get("required_result_fields", []),
    }


def run_stage116_runner_plan(
    *,
    stage111_results_path: Path = DEFAULT_STAGE111_RESULTS,
    stage114_manifest_path: Path = DEFAULT_STAGE114_MANIFEST,
    stage118_results_path: Path = DEFAULT_STAGE118_RESULTS,
    stage129_results_path: Path = DEFAULT_STAGE129_RESULTS,
) -> dict[str, Any]:
    stage111 = _load_json(stage111_results_path)
    stage114 = _load_json(stage114_manifest_path)
    stage118 = _load_json(stage118_results_path)
    stage129 = _load_json(stage129_results_path)
    sources = [
        (stage111_results_path, stage111),
        (stage114_manifest_path, stage114),
        (stage118_results_path, stage118),
        (stage129_results_path, stage129),
    ]
    missing_sources = [str(path.as_posix()) for path, payload in sources if payload is None]
    provider_records = _provider_status(stage111 if isinstance(stage111, dict) else None)
    runner_records = [
        _runner_record(
            str(path),
            stage114,
            provider_records,
            stage111_results_path=stage111_results_path,
            stage118_results_path=stage118_results_path,
            stage129_results_path=stage129_results_path,
        )
        for path in (stage114.get("job_shard_paths", []) if isinstance(stage114, dict) else [])
    ]
    ready_count = sum(1 for record in runner_records if record["status"] == "ready_to_run")
    return {
        "schema_version": STAGE116_SCHEMA_VERSION,
        "stage": "stage116_provider_runner_plan",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": (
            "PROVIDER_RUNNER_PLAN_READY_FOR_EXECUTION"
            if runner_records and ready_count == len(runner_records) and not missing_sources
            else "PROVIDER_RUNNER_PLAN_PREPARED_EXECUTION_BLOCKED"
        ),
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "stage111_decision": stage111.get("decision") if isinstance(stage111, dict) else None,
        "stage114_decision": stage114.get("decision") if isinstance(stage114, dict) else None,
        "stage118_decision": stage118.get("decision") if isinstance(stage118, dict) else None,
        "stage129_decision": stage129.get("decision") if isinstance(stage129, dict) else None,
        "runner_count": len(runner_records),
        "ready_runner_count": ready_count,
        "job_count": sum(record["job_count"] for record in runner_records),
        "runner_records": runner_records,
        "no_hardware_submission": True,
        "provider_credentials_required": True,
        "secret_values_recorded": False,
        "claim_boundary": {
            "supported": [
                "a provider/window runner plan over Stage 114 job shards",
                "explicit execution blockers inherited from Stage 111 provider readiness",
                "stable provider result output paths for Stage 115 collection",
                "runner commands carry explicit Stage 111, Stage 118, and Stage 129 evidence paths",
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
            "Clear Stage 111 provider readiness and Stage 129 cutover authorization, then execute only Stage 133 "
            "authorized command records and collect their result files through Stage 115."
        ),
    }


def write_stage116_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "stage111_decision": result["stage111_decision"],
        "stage114_decision": result["stage114_decision"],
        "stage118_decision": result["stage118_decision"],
        "stage129_decision": result["stage129_decision"],
        "runner_count": result["runner_count"],
        "ready_runner_count": result["ready_runner_count"],
        "job_count": result["job_count"],
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
            fieldnames=("provider", "window_id", "status", "job_count", "calibration_job_count", "packet_job_count", "provider_result_path", "blockers", "runner_command"),
        )
        writer.writeheader()
        for record in result["runner_records"]:
            writer.writerow(
                {
                    "provider": record["provider"],
                    "window_id": record["window_id"],
                    "status": record["status"],
                    "job_count": record["job_count"],
                    "calibration_job_count": record["calibration_job_count"],
                    "packet_job_count": record["packet_job_count"],
                    "provider_result_path": record["provider_result_path"],
                    "blockers": "; ".join(record["blockers"]),
                    "runner_command": record["runner_command"],
                }
            )
    return paths


def print_stage116_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"ready_runner_count: {result['ready_runner_count']}/{result['runner_count']}")
    print(f"job_count: {result['job_count']}")
    print(f"next_gate: {result['next_gate']}")
