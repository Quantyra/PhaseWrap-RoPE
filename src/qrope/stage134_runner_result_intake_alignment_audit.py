from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


STAGE134_SCHEMA_VERSION = "qrope_stage134_runner_result_intake_alignment_audit_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE115_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage115_provider_result_collector" / "results.json"
DEFAULT_STAGE133_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage133_authorized_runner_command_packet" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage134_runner_result_intake_alignment_audit"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _collector_record(stage115: dict[str, Any] | None, provider: str, window_id: str) -> dict[str, Any]:
    if not isinstance(stage115, dict):
        return {}
    for record in stage115.get("shard_records", []):
        if record.get("provider") == provider and record.get("window_id") == window_id:
            return record
    return {}


def _command_output_path(record: dict[str, Any]) -> str:
    command = str(record.get("live_submit_command") or record.get("runner_command") or "")
    parts = command.split()
    for index, part in enumerate(parts):
        if part == "--provider-results" and index + 1 < len(parts):
            return parts[index + 1]
    return ""


def _int_field(payload: dict[str, Any] | None, key: str) -> int:
    if not isinstance(payload, dict):
        return 0
    try:
        return int(payload.get(key) or 0)
    except (TypeError, ValueError):
        return 0


def _stage115_handoff_blockers(stage115: dict[str, Any] | None, provider: str) -> list[str]:
    if not isinstance(stage115, dict):
        return ["stage115_results_missing"]
    blockers = []
    if str(stage115.get("provider_scope", "")) != provider:
        blockers.append("stage115_provider_scope_mismatch")
    if stage115.get("decision") != "PROVIDER_RESULTS_COLLECTED_FOR_STAGE113":
        blockers.append("stage115_not_collected_for_stage113")
    if stage115.get("wrote_stage113_input") is not True:
        blockers.append("stage115_did_not_write_stage113_input")
    if stage115.get("stage152_write_ready") is not True:
        blockers.append("stage115_stage152_write_not_ready")
    if stage115.get("stage152_write_blockers"):
        blockers.append("stage115_stage152_write_blockers_present")
    if stage115.get("stage152_all_first_provider_commands_authorized") is not True:
        blockers.append("stage115_stage152_commands_not_all_authorized")
    if stage115.get("stage152_all_first_provider_commands_live_submit_ready") is not True:
        blockers.append("stage115_stage152_commands_not_all_live_submit_ready")
    runner_count = _int_field(stage115, "stage152_first_provider_runner_command_count")
    authorized_count = _int_field(stage115, "stage152_first_provider_authorized_runner_count")
    live_submit_ready_count = _int_field(stage115, "stage152_first_provider_live_submit_ready_count")
    if runner_count <= 0:
        blockers.append("stage115_stage152_runner_commands_missing")
    if runner_count > 0 and authorized_count != runner_count:
        blockers.append("stage115_stage152_authorized_runner_count_incomplete")
    if runner_count > 0 and live_submit_ready_count != runner_count:
        blockers.append("stage115_stage152_live_submit_ready_count_incomplete")
    return sorted(set(blockers))


def _intake_record(command: dict[str, Any], stage115: dict[str, Any] | None) -> dict[str, Any]:
    provider = str(command.get("provider"))
    window_id = str(command.get("window_id"))
    collector = _collector_record(stage115, provider, window_id)
    command_output_path = _command_output_path(command)
    collector_result_path = str(collector.get("result_path", ""))
    blockers = []
    command_authorized = command.get("command_authorized") is True
    live_submit_available = command.get("live_submit_command_available") is True
    live_submit_command = str(command.get("live_submit_command", ""))
    stage115_handoff_blockers = _stage115_handoff_blockers(stage115, provider)
    if not command_output_path:
        blockers.append("command_output_path_missing")
    if not collector_result_path:
        blockers.append("collector_result_path_missing")
    if command_output_path and collector_result_path and command_output_path != collector_result_path:
        blockers.append("command_output_path_mismatch_collector")
    if command.get("job_count") != collector.get("expected_job_count"):
        blockers.append("job_count_mismatch_collector")
    if not command_authorized:
        blockers.append("stage133_command_not_authorized")
    if command_authorized and (not live_submit_available or not live_submit_command):
        blockers.append("stage133_authorized_command_missing_live_submit_command")
    if not command_authorized and (live_submit_available or live_submit_command):
        blockers.append("stage133_blocked_command_exposes_live_submit_command")
    if collector.get("ready") is not True:
        blockers.extend(f"stage115:{item}" for item in collector.get("missing_evidence", ["collector_shard_not_ready"]))
    blockers.extend(stage115_handoff_blockers)
    return {
        "provider": provider,
        "window_id": window_id,
        "job_count": command.get("job_count"),
        "command_authorized": command_authorized,
        "live_submit_command_available": live_submit_available,
        "live_submit_command_present": bool(live_submit_command),
        "collector_ready": collector.get("ready"),
        "collector_missing_job_count": collector.get("missing_job_count"),
        "command_output_path": command_output_path,
        "collector_result_path": collector_result_path,
        "stage115_handoff_ready": not stage115_handoff_blockers,
        "stage113_ready_after_collection": command.get("command_authorized") is True and collector.get("ready") is True and not blockers,
        "blockers": sorted(set(blockers)),
    }


def run_stage134_audit(
    *,
    stage115_results_path: Path = DEFAULT_STAGE115_RESULTS,
    stage133_results_path: Path = DEFAULT_STAGE133_RESULTS,
) -> dict[str, Any]:
    stage115 = _load_json(stage115_results_path)
    stage133 = _load_json(stage133_results_path)
    sources = [(stage115_results_path, stage115), (stage133_results_path, stage133)]
    missing_sources = [str(path.as_posix()) for path, payload in sources if payload is None]
    records = [
        _intake_record(command, stage115)
        for command in (stage133.get("command_records", []) if isinstance(stage133, dict) else [])
    ]
    ready_count = sum(1 for record in records if record["stage113_ready_after_collection"])
    return {
        "schema_version": STAGE134_SCHEMA_VERSION,
        "stage": "stage134_runner_result_intake_alignment_audit",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": (
            "RUNNER_RESULT_INTAKE_READY_FOR_STAGE113"
            if records and ready_count == len(records) and not missing_sources
            else "RUNNER_RESULT_INTAKE_ALIGNED_EXECUTION_BLOCKED"
        ),
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "stage115_decision": stage115.get("decision") if isinstance(stage115, dict) else None,
        "stage133_decision": stage133.get("decision") if isinstance(stage133, dict) else None,
        "stage115_wrote_stage113_input": stage115.get("wrote_stage113_input") if isinstance(stage115, dict) else None,
        "stage115_stage152_write_ready": stage115.get("stage152_write_ready") if isinstance(stage115, dict) else None,
        "stage115_stage152_write_blockers": stage115.get("stage152_write_blockers") if isinstance(stage115, dict) else None,
        "runner_count": len(records),
        "ready_intake_count": ready_count,
        "expected_job_count": sum(int(record.get("job_count") or 0) for record in records),
        "missing_job_count": sum(int(record.get("collector_missing_job_count") or 0) for record in records),
        "intake_records": records,
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "claim_boundary": {
            "supported": [
                "Stage 133 provider result output paths align with Stage 115 collector shard paths",
                "post-run intake remains blocked until command_authorized=true and every collector shard is ready",
                "Stage 133 live-submit command availability is consistent with command authorization before Stage 113",
                "the Stage 115 to Stage 113 handoff remains blocked until Stage 115 writes the Stage 113 input through the Stage 152 guard",
            ],
            "excluded": [
                "hardware job submission",
                "provider credentials or secret values",
                "live provider SDK client creation",
                "Stage 113 evidence assembly",
                "a noisy-hardware robustness result",
            ],
        },
        "next_gate": (
            "Execute only Stage 133 authorized commands, rerun Stage 115 with --write-stage113-input after result shards "
            "are complete, then rerun this audit before Stage 113 --write-evidence."
        ),
    }


def write_stage134_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "stage115_decision": result["stage115_decision"],
        "stage133_decision": result["stage133_decision"],
        "stage115_wrote_stage113_input": result["stage115_wrote_stage113_input"],
        "stage115_stage152_write_ready": result["stage115_stage152_write_ready"],
        "stage115_stage152_write_blockers": result["stage115_stage152_write_blockers"],
        "runner_count": result["runner_count"],
        "ready_intake_count": result["ready_intake_count"],
        "expected_job_count": result["expected_job_count"],
        "missing_job_count": result["missing_job_count"],
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
            fieldnames=(
                "provider",
                "window_id",
                "job_count",
                "command_authorized",
                "live_submit_command_available",
                "live_submit_command_present",
                "collector_ready",
                "collector_missing_job_count",
                "stage115_handoff_ready",
                "stage113_ready_after_collection",
                "blockers",
            ),
        )
        writer.writeheader()
        for record in result["intake_records"]:
            writer.writerow(
                {
                    "provider": record["provider"],
                    "window_id": record["window_id"],
                    "job_count": record["job_count"],
                    "command_authorized": record["command_authorized"],
                    "live_submit_command_available": record["live_submit_command_available"],
                    "live_submit_command_present": record["live_submit_command_present"],
                    "collector_ready": record["collector_ready"],
                    "collector_missing_job_count": record["collector_missing_job_count"],
                    "stage115_handoff_ready": record["stage115_handoff_ready"],
                    "stage113_ready_after_collection": record["stage113_ready_after_collection"],
                    "blockers": "; ".join(record["blockers"]),
                }
            )
    return paths


def print_stage134_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"ready_intake_count: {result['ready_intake_count']}/{result['runner_count']}")
    print(f"expected_job_count: {result['expected_job_count']}")
    print(f"missing_job_count: {result['missing_job_count']}")
    print(f"next_gate: {result['next_gate']}")
