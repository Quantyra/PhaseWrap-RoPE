from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


STAGE156_SCHEMA_VERSION = "qrope_stage156_first_provider_live_run_pause_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE133_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage133_authorized_runner_command_packet" / "results.json"
DEFAULT_STAGE152_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage152_first_provider_live_execution_guard" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage156_first_provider_live_run_pause"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)
STAGE152_READY = "FIRST_PROVIDER_LIVE_EXECUTION_GUARD_READY_FOR_GUARDED_RUNNER"


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def run_stage156_live_run_pause(
    *,
    stage133_results_path: Path = DEFAULT_STAGE133_RESULTS,
    stage152_results_path: Path = DEFAULT_STAGE152_RESULTS,
) -> dict[str, Any]:
    stage133 = _load_json(stage133_results_path)
    stage152 = _load_json(stage152_results_path)
    missing_sources = [
        str(path.as_posix())
        for path, payload in ((stage133_results_path, stage133), (stage152_results_path, stage152))
        if not isinstance(payload, dict)
    ]
    first_provider = stage152.get("first_unlock_provider") if isinstance(stage152, dict) else None
    authorized_commands = [
        record
        for record in (stage133.get("command_records", []) if isinstance(stage133, dict) else [])
        if record.get("provider") == first_provider and record.get("command_authorized") is True
    ]
    ready_for_guarded_runner = bool(isinstance(stage152, dict) and stage152.get("decision") == STAGE152_READY)
    command_records = [
        {
            "provider": record.get("provider"),
            "window_id": record.get("window_id"),
            "job_count": record.get("job_count"),
            "command_authorized": record.get("command_authorized") is True,
            "live_submit_command_available": record.get("live_submit_command_available") is True,
        }
        for record in authorized_commands
    ]
    if missing_sources:
        decision = "FIRST_PROVIDER_LIVE_RUN_PAUSE_INCOMPLETE"
    elif ready_for_guarded_runner and authorized_commands:
        decision = "FIRST_PROVIDER_LIVE_RUN_READY_AWAITING_EXPLICIT_APPROVAL"
    else:
        decision = "FIRST_PROVIDER_LIVE_RUN_PAUSE_BLOCKED_GUARD_NOT_READY"
    return {
        "schema_version": STAGE156_SCHEMA_VERSION,
        "stage": "stage156_first_provider_live_run_pause",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": decision,
        "source_artifacts": [str(stage133_results_path.as_posix()), str(stage152_results_path.as_posix())],
        "missing_source_artifacts": missing_sources,
        "stage133_decision": stage133.get("decision") if isinstance(stage133, dict) else None,
        "stage152_decision": stage152.get("decision") if isinstance(stage152, dict) else None,
        "first_unlock_provider": first_provider,
        "stage152_ready_for_guarded_runner": ready_for_guarded_runner,
        "authorized_first_provider_runner_count": len(authorized_commands),
        "authorized_first_provider_job_count": sum(int(record.get("job_count") or 0) for record in authorized_commands),
        "authorized_command_records": command_records,
        "explicit_user_approval_required": True,
        "no_hardware_submission": True,
        "provider_credentials_required": True,
        "secret_values_recorded": False,
        "claim_boundary": {
            "supported": [
                "non-live checkpoint that IBM first-provider guarded-runner readiness has cleared",
                "explicit pause before running any Stage 133 live-submit command",
                "non-secret authorized command counts and job counts",
            ],
            "excluded": [
                "hardware job submission",
                "provider credential values",
                "provider result records",
                "credit balance verification",
                "a noisy-hardware robustness or auditability conclusion",
            ],
        },
        "next_gate": (
            "After explicit approval to spend hardware budget, execute only the authorized first-provider Stage 133 "
            "live-submit commands, then collect provider result shards through Stage 115 and assemble evidence through Stage 113."
        ),
    }


def write_stage156_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
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
        "stage152_decision": result["stage152_decision"],
        "first_unlock_provider": result["first_unlock_provider"],
        "stage152_ready_for_guarded_runner": result["stage152_ready_for_guarded_runner"],
        "authorized_first_provider_runner_count": result["authorized_first_provider_runner_count"],
        "authorized_first_provider_job_count": result["authorized_first_provider_job_count"],
        "explicit_user_approval_required": result["explicit_user_approval_required"],
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
            fieldnames=("provider", "window_id", "job_count", "command_authorized", "live_submit_command_available"),
        )
        writer.writeheader()
        for record in result["authorized_command_records"]:
            writer.writerow({field: record.get(field) for field in writer.fieldnames})
    return paths


def print_stage156_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"first_unlock_provider: {result['first_unlock_provider']}")
    print(f"authorized_first_provider_runner_count: {result['authorized_first_provider_runner_count']}")
    print(f"authorized_first_provider_job_count: {result['authorized_first_provider_job_count']}")
    print(f"next_gate: {result['next_gate']}")
