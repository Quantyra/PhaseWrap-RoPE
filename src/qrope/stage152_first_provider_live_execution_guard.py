from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


STAGE152_SCHEMA_VERSION = "qrope_stage152_first_provider_live_execution_guard_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE133_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage133_authorized_runner_command_packet" / "results.json"
DEFAULT_STAGE151_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage151_first_provider_result_metadata_guard_audit" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage152_first_provider_live_execution_guard"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _commands_for_provider(stage133: dict[str, Any] | None, provider: str) -> list[dict[str, Any]]:
    if not isinstance(stage133, dict):
        return []
    return [record for record in stage133.get("command_records", []) if record.get("provider") == provider]


def run_stage152_guard(
    *,
    stage133_results_path: Path = DEFAULT_STAGE133_RESULTS,
    stage151_results_path: Path = DEFAULT_STAGE151_RESULTS,
) -> dict[str, Any]:
    stage133 = _load_json(stage133_results_path)
    stage151 = _load_json(stage151_results_path)
    sources = [(stage133_results_path, stage133), (stage151_results_path, stage151)]
    missing_sources = [str(path.as_posix()) for path, payload in sources if payload is None]
    provider = str(stage151.get("first_unlock_provider", "")) if isinstance(stage151, dict) else ""
    metadata_guard_ready = bool(
        isinstance(stage151, dict)
        and stage151.get("decision") == "FIRST_PROVIDER_RESULT_METADATA_GUARD_READY_EXECUTION_BLOCKED"
    )
    commands = _commands_for_provider(stage133, provider)
    authorized_commands = [record for record in commands if record.get("command_authorized") is True]
    ready = bool(provider) and metadata_guard_ready and bool(authorized_commands) and not missing_sources
    blockers = []
    if not provider:
        blockers.append("first_unlock_provider_missing")
    if not metadata_guard_ready:
        blockers.append("stage151_metadata_guard_not_ready")
    if not authorized_commands:
        blockers.append("stage133_no_authorized_first_provider_commands")
    return {
        "schema_version": STAGE152_SCHEMA_VERSION,
        "stage": "stage152_first_provider_live_execution_guard",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": (
            "FIRST_PROVIDER_LIVE_EXECUTION_GUARD_READY_FOR_GUARDED_RUNNER"
            if ready
            else "FIRST_PROVIDER_LIVE_EXECUTION_GUARD_PREPARED_EXECUTION_BLOCKED"
        ),
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "first_unlock_provider": provider,
        "stage151_metadata_guard_ready": metadata_guard_ready,
        "first_provider_runner_command_count": len(commands),
        "first_provider_authorized_runner_count": len(authorized_commands),
        "blockers": sorted(set(blockers)),
        "command_records": commands,
        "no_hardware_submission": True,
        "provider_credentials_required": True,
        "secret_values_recorded": False,
        "claim_boundary": {
            "supported": [
                "final non-live guard tying Stage 133 first-provider command authorization to Stage 151 metadata write-path readiness",
                "blocked outcome unless first-provider commands are authorized and the result metadata guard is ready",
                "explicit separation between command preparation and permission to run guarded live provider execution",
            ],
            "excluded": [
                "provider credential values",
                "hardware job submission",
                "live provider SDK client creation",
                "real provider result records",
                "a noisy-hardware robustness or auditability conclusion",
            ],
        },
        "next_gate": (
            "Only after this guard reports READY_FOR_GUARDED_RUNNER should a Stage 133 live-submit command be executed; "
            "after execution, collect result shards through Stage 115 and assemble evidence through Stage 113."
        ),
    }


def write_stage152_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "first_unlock_provider": result["first_unlock_provider"],
        "stage151_metadata_guard_ready": result["stage151_metadata_guard_ready"],
        "first_provider_runner_command_count": result["first_provider_runner_command_count"],
        "first_provider_authorized_runner_count": result["first_provider_authorized_runner_count"],
        "blockers": result["blockers"],
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
        writer = csv.DictWriter(handle, fieldnames=("provider", "window_id", "job_count", "command_authorized", "blockers"))
        writer.writeheader()
        for record in result["command_records"]:
            writer.writerow(
                {
                    "provider": record.get("provider"),
                    "window_id": record.get("window_id"),
                    "job_count": record.get("job_count"),
                    "command_authorized": record.get("command_authorized"),
                    "blockers": "; ".join(str(item) for item in record.get("blockers", [])),
                }
            )
    return paths


def print_stage152_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"first_unlock_provider: {result['first_unlock_provider']}")
    print(f"stage151_metadata_guard_ready: {result['stage151_metadata_guard_ready']}")
    print(f"first_provider_authorized_runner_count: {result['first_provider_authorized_runner_count']}/{result['first_provider_runner_command_count']}")
    print(f"blockers: {', '.join(result['blockers'])}")
    print(f"next_gate: {result['next_gate']}")
