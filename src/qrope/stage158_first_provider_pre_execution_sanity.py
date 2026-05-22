from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


STAGE158_SCHEMA_VERSION = "qrope_stage158_first_provider_pre_execution_sanity_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE133_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage133_authorized_runner_command_packet" / "results.json"
DEFAULT_STAGE157_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage157_first_provider_live_run_approval_packet" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage158_first_provider_pre_execution_sanity"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)
APPROVAL_READY = "FIRST_PROVIDER_LIVE_RUN_APPROVAL_PACKET_READY"


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _arg_value(command: str, flag: str) -> str:
    parts = command.split()
    try:
        index = parts.index(flag)
    except ValueError:
        return ""
    if index + 1 >= len(parts):
        return ""
    return parts[index + 1]


def _line_count(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def _stage133_records(stage133: dict[str, Any], provider: str) -> list[dict[str, Any]]:
    return [
        record
        for record in stage133.get("command_records", [])
        if record.get("provider") == provider
        and record.get("command_authorized") is True
        and record.get("live_submit_command_available") is True
    ]


def run_stage158_pre_execution_sanity(
    *,
    stage133_results_path: Path = DEFAULT_STAGE133_RESULTS,
    stage157_results_path: Path = DEFAULT_STAGE157_RESULTS,
) -> dict[str, Any]:
    stage133 = _load_json(stage133_results_path)
    stage157 = _load_json(stage157_results_path)
    missing_sources = [
        str(path.as_posix())
        for path, payload in ((stage133_results_path, stage133), (stage157_results_path, stage157))
        if not isinstance(payload, dict)
    ]
    provider = stage157.get("first_unlock_provider") if isinstance(stage157, dict) else None
    approval_records = stage157.get("approval_records", []) if isinstance(stage157, dict) else []
    stage133_records = _stage133_records(stage133, str(provider)) if isinstance(stage133, dict) and provider else []
    approval_by_window = {str(record.get("window_id")): record for record in approval_records}
    stage133_by_window = {str(record.get("window_id")): record for record in stage133_records}
    windows = sorted(set(approval_by_window) | set(stage133_by_window))
    records = []
    for window_id in windows:
        approval = approval_by_window.get(window_id, {})
        command_record = stage133_by_window.get(window_id, {})
        command = str(command_record.get("live_submit_command") or "")
        provider_results = _arg_value(command, "--provider-results")
        job_shard = _arg_value(command, "--job-shard")
        result_path = Path(provider_results) if provider_results else None
        job_shard_path = Path(job_shard) if job_shard else None
        result_exists = bool(result_path and result_path.exists())
        result_line_count = _line_count(result_path) if result_path else 0
        blockers = []
        if not approval:
            blockers.append("missing_stage157_approval_record")
        if not command_record:
            blockers.append("missing_stage133_authorized_command")
        if approval and command_record and int(approval.get("job_count") or 0) != int(command_record.get("job_count") or 0):
            blockers.append("job_count_mismatch")
        if not job_shard:
            blockers.append("job_shard_argument_missing")
        elif not job_shard_path or not job_shard_path.exists():
            blockers.append("job_shard_missing")
        if not provider_results:
            blockers.append("provider_results_argument_missing")
        if result_exists and result_line_count > 0:
            blockers.append("provider_results_file_not_empty")
        records.append(
            {
                "provider": provider,
                "window_id": window_id,
                "approved_job_count": approval.get("job_count"),
                "stage133_job_count": command_record.get("job_count"),
                "job_shard_path": job_shard,
                "job_shard_exists": bool(job_shard_path and job_shard_path.exists()),
                "provider_results_path": provider_results,
                "provider_results_file_exists": result_exists,
                "provider_results_line_count": result_line_count,
                "ready": not blockers,
                "blockers": sorted(set(blockers)),
            }
        )
    blockers = []
    if missing_sources:
        blockers.append("missing_source_artifacts")
    if not isinstance(stage157, dict) or stage157.get("decision") != APPROVAL_READY:
        blockers.append("stage157_approval_packet_not_ready")
    if not records:
        blockers.append("no_first_provider_command_records")
    if any(not record["ready"] for record in records):
        blockers.append("pre_execution_record_blockers_present")
    ready = not blockers
    return {
        "schema_version": STAGE158_SCHEMA_VERSION,
        "stage": "stage158_first_provider_pre_execution_sanity",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": (
            "FIRST_PROVIDER_PRE_EXECUTION_SANITY_READY_AWAITING_APPROVAL"
            if ready
            else "FIRST_PROVIDER_PRE_EXECUTION_SANITY_BLOCKED"
        ),
        "source_artifacts": [str(stage133_results_path.as_posix()), str(stage157_results_path.as_posix())],
        "missing_source_artifacts": missing_sources,
        "stage133_decision": stage133.get("decision") if isinstance(stage133, dict) else None,
        "stage157_decision": stage157.get("decision") if isinstance(stage157, dict) else None,
        "first_unlock_provider": provider,
        "approval_phrase_required": stage157.get("approval_phrase_required") if isinstance(stage157, dict) else None,
        "record_count": len(records),
        "ready_record_count": sum(1 for record in records if record["ready"]),
        "authorized_job_count": sum(int(record.get("stage133_job_count") or 0) for record in records),
        "pre_execution_records": records,
        "blockers": sorted(set(blockers)),
        "no_hardware_submission": True,
        "explicit_user_approval_required": True,
        "provider_credentials_required": True,
        "secret_values_recorded": False,
        "runnable_commands_recorded": False,
        "claim_boundary": {
            "supported": [
                "non-live parity check between Stage 157 approval records and Stage 133 authorized commands",
                "pre-execution check that target provider-result files are absent or empty",
                "non-secret job-shard and result-path readiness for the first-provider live run",
            ],
            "excluded": [
                "hardware job submission",
                "runnable live-submit command strings",
                "provider credential values",
                "provider result records",
                "credit balance verification",
                "a noisy-hardware robustness or auditability conclusion",
            ],
        },
        "next_gate": (
            "Only after explicit approval, execute the authorized Stage 133 live-submit commands whose Stage 158 "
            "records are ready; after execution, rerun Stage 115 with provider_scope=ibm_runtime."
        ),
    }


def write_stage158_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "stage133_decision": result["stage133_decision"],
        "stage157_decision": result["stage157_decision"],
        "first_unlock_provider": result["first_unlock_provider"],
        "approval_phrase_required": result["approval_phrase_required"],
        "record_count": result["record_count"],
        "ready_record_count": result["ready_record_count"],
        "authorized_job_count": result["authorized_job_count"],
        "blockers": result["blockers"],
        "no_hardware_submission": result["no_hardware_submission"],
        "explicit_user_approval_required": result["explicit_user_approval_required"],
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
                "stage133_job_count",
                "job_shard_path",
                "job_shard_exists",
                "provider_results_path",
                "provider_results_file_exists",
                "provider_results_line_count",
                "ready",
                "blockers",
            ),
        )
        writer.writeheader()
        for record in result["pre_execution_records"]:
            writer.writerow({**{field: record.get(field) for field in writer.fieldnames}, "blockers": "; ".join(record["blockers"])})
    return paths


def print_stage158_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"first_unlock_provider: {result['first_unlock_provider']}")
    print(f"ready_record_count: {result['ready_record_count']}/{result['record_count']}")
    print(f"authorized_job_count: {result['authorized_job_count']}")
    print(f"blockers: {', '.join(result['blockers'])}")
    print(f"next_gate: {result['next_gate']}")
