from __future__ import annotations

import csv
import importlib
import json
from pathlib import Path
from typing import Any


STAGE123_SCHEMA_VERSION = "qrope_stage123_provider_submission_plan_audit_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE118_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage118_provider_payload_dry_run_audit" / "results.json"
DEFAULT_STAGE122_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage122_provider_adapter_skeleton_audit" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage123_provider_submission_plan_audit"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)
ADAPTER_MODULES = {
    "amazon_braket": "qrope.provider_adapters.amazon_braket",
    "ibm_runtime": "qrope.provider_adapters.ibm_runtime",
}


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _job_path_from_payload_path(payload_path: Path) -> Path:
    text = str(payload_path.as_posix())
    return Path(
        text.replace("stage118_provider_payload_dry_run_audit/dry_run_payloads", "stage114_provider_result_capture_contract/job_shards")
        .replace("/submission_payloads.jsonl", "/jobs.jsonl")
    )


def _plan_record(payload_record: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    provider = str(payload_record.get("provider", ""))
    payload_path = Path(str(payload_record.get("payload_output_path", "")))
    job_path = _job_path_from_payload_path(payload_path)
    payloads = _load_jsonl(payload_path)
    jobs = _load_jsonl(job_path)
    missing = []
    plans: list[dict[str, Any]] = []
    if not payload_path.exists():
        missing.append("payload_file_missing")
    if not job_path.exists():
        missing.append("job_shard_missing")
    if len(payloads) != len(jobs):
        missing.append("job_payload_count_mismatch")
    module_name = ADAPTER_MODULES.get(provider, "")
    try:
        module = importlib.import_module(module_name)
        builder = getattr(module, "build_submission_plan")
    except Exception as exc:  # noqa: BLE001 - audit reports adapter contract failures.
        missing.append(f"plan_builder_missing:{exc}")
        builder = None
    if builder and not missing:
        try:
            plans = builder(jobs=jobs, payloads=payloads)
        except Exception as exc:  # noqa: BLE001
            missing.append(f"plan_builder_failed:{exc}")
    plan_ids = [str(plan.get("job_id", "")) for plan in plans]
    job_ids = [str(job.get("job_id", "")) for job in jobs]
    if plans and plan_ids != job_ids:
        missing.append("plan_job_order_mismatch")
    if any(plan.get("no_hardware_submission") is not True for plan in plans):
        missing.append("plan_no_submit_marker_missing")
    if any(not plan.get("openqasm3_sha256") for plan in plans):
        missing.append("plan_openqasm3_hash_missing")
    return (
        {
            "provider": provider,
            "window_id": payload_record.get("window_id"),
            "payload_output_path": str(payload_path.as_posix()),
            "job_shard_path": str(job_path.as_posix()),
            "expected_payload_count": payload_record.get("compiled_payload_count", 0),
            "job_count": len(jobs),
            "payload_count": len(payloads),
            "submission_plan_count": len(plans),
            "missing_evidence": sorted(set(missing)),
            "ready": not missing and bool(plans),
        },
        plans,
    )


def run_stage123_audit(
    *,
    stage118_results_path: Path = DEFAULT_STAGE118_RESULTS,
    stage122_results_path: Path = DEFAULT_STAGE122_RESULTS,
) -> dict[str, Any]:
    stage118 = _load_json(stage118_results_path)
    stage122 = _load_json(stage122_results_path)
    sources = [(stage118_results_path, stage118), (stage122_results_path, stage122)]
    missing_sources = [str(path.as_posix()) for path, payload in sources if payload is None]
    plan_records = []
    plans_by_window: dict[str, list[dict[str, Any]]] = {}
    if isinstance(stage118, dict):
        for payload_record in stage118.get("payload_records", []):
            record, plans = _plan_record(payload_record)
            plan_records.append(record)
            plans_by_window[f"{record['provider']}::{record['window_id']}"] = plans
    ready = bool(plan_records) and all(record["ready"] for record in plan_records) and not missing_sources
    return {
        "schema_version": STAGE123_SCHEMA_VERSION,
        "stage": "stage123_provider_submission_plan_audit",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": (
            "PROVIDER_SUBMISSION_PLANS_READY_EXECUTION_BLOCKED"
            if ready
            else "PROVIDER_SUBMISSION_PLANS_INCOMPLETE"
        ),
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "stage118_decision": stage118.get("decision") if isinstance(stage118, dict) else None,
        "stage122_decision": stage122.get("decision") if isinstance(stage122, dict) else None,
        "runner_count": len(plan_records),
        "ready_plan_record_count": sum(1 for record in plan_records if record["ready"]),
        "job_count": sum(record["job_count"] for record in plan_records),
        "submission_plan_count": sum(record["submission_plan_count"] for record in plan_records),
        "plan_records": plan_records,
        "plans_by_window": plans_by_window,
        "no_hardware_submission": True,
        "provider_credentials_required": True,
        "secret_values_recorded": False,
        "claim_boundary": {
            "supported": [
                "provider adapters can deterministically map Stage 118 payloads into SDK submission plans",
                "submission plans preserve job IDs, provider/window identity, shots, OpenQASM hashes, and result-field expectations",
                "all plans remain no-submit artifacts before live SDK execution",
            ],
            "excluded": [
                "hardware job submission",
                "provider credentials or secret values",
                "live provider SDK submission",
                "real provider result records",
                "Stage 113 evidence assembly",
                "a noisy-hardware robustness result",
            ],
        },
        "next_gate": (
            "Use the Stage 123 submission plans to implement guarded SDK submitters that replace no-submit plans "
            "with real provider job IDs and measured counts only after Stage 106/111 readiness clears."
        ),
    }


def write_stage123_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    plans_dir = output_dir / "submission_plans"
    plan_paths = []
    for key, plans in result["plans_by_window"].items():
        provider, window_id = key.split("::", 1)
        path = plans_dir / provider / window_id / "submission_plans.jsonl"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("".join(json.dumps(plan, sort_keys=True) + "\n" for plan in plans), encoding="utf-8")
        plan_paths.append(str(path.as_posix()))
    result_without_plans = {key: value for key, value in result.items() if key != "plans_by_window"}
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "stage118_decision": result["stage118_decision"],
        "stage122_decision": result["stage122_decision"],
        "runner_count": result["runner_count"],
        "ready_plan_record_count": result["ready_plan_record_count"],
        "job_count": result["job_count"],
        "submission_plan_count": result["submission_plan_count"],
        "submission_plan_paths": plan_paths,
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
    (output_dir / "results.json").write_text(json.dumps(result_without_plans, indent=2, sort_keys=True), encoding="utf-8")
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=("provider", "window_id", "job_count", "payload_count", "submission_plan_count", "ready", "missing_evidence"),
        )
        writer.writeheader()
        for record in result["plan_records"]:
            writer.writerow(
                {
                    "provider": record["provider"],
                    "window_id": record["window_id"],
                    "job_count": record["job_count"],
                    "payload_count": record["payload_count"],
                    "submission_plan_count": record["submission_plan_count"],
                    "ready": record["ready"],
                    "missing_evidence": "; ".join(record["missing_evidence"]),
                }
            )
    return paths


def print_stage123_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"submission_plan_count: {result['submission_plan_count']}/{result['job_count']}")
    print(f"ready_plan_record_count: {result['ready_plan_record_count']}/{result['runner_count']}")
    print(f"next_gate: {result['next_gate']}")
