from __future__ import annotations

import csv
import json
import shlex
from pathlib import Path
from typing import Any


STAGE117_SCHEMA_VERSION = "qrope_stage117_provider_runner_guard_audit_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE116_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage116_provider_runner_plan" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage117_provider_runner_guard_audit"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _script_path(command: str) -> Path | None:
    parts = shlex.split(command, posix=False)
    for part in parts:
        if part.endswith(".py"):
            return Path(part)
    return None


def _runner_record(record: dict[str, Any]) -> dict[str, Any]:
    command = str(record.get("runner_command", ""))
    script_path = _script_path(command)
    exists = bool(script_path and script_path.exists())
    blocked = record.get("status") != "ready_to_run"
    missing = []
    if not exists:
        missing.append("runner_script_missing")
    if not blocked:
        missing.append("stage116_runner_not_blocked")
    return {
        "provider": record.get("provider"),
        "window_id": record.get("window_id"),
        "stage116_status": record.get("status"),
        "runner_command": command,
        "runner_script_path": str(script_path.as_posix()) if script_path else "",
        "runner_script_exists": exists,
        "stage116_runner_blocked": blocked,
        "missing_evidence": missing,
        "ready": not missing,
    }


def run_stage117_audit(*, stage116_results_path: Path = DEFAULT_STAGE116_RESULTS) -> dict[str, Any]:
    stage116 = _load_json(stage116_results_path)
    missing_sources = [] if isinstance(stage116, dict) else [str(stage116_results_path.as_posix())]
    runner_records = [_runner_record(record) for record in stage116.get("runner_records", [])] if isinstance(stage116, dict) else []
    ready = bool(runner_records) and all(record["ready"] for record in runner_records) and not missing_sources
    return {
        "schema_version": STAGE117_SCHEMA_VERSION,
        "stage": "stage117_provider_runner_guard_audit",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": (
            "PROVIDER_RUNNER_GUARDS_PREPARED_EXECUTION_BLOCKED"
            if ready
            else "PROVIDER_RUNNER_GUARDS_INCOMPLETE"
        ),
        "source_artifacts": [str(stage116_results_path.as_posix())],
        "missing_source_artifacts": missing_sources,
        "stage116_decision": stage116.get("decision") if isinstance(stage116, dict) else None,
        "runner_count": len(runner_records),
        "guarded_runner_count": sum(1 for record in runner_records if record["ready"]),
        "runner_records": runner_records,
        "no_hardware_submission": True,
        "provider_credentials_required": True,
        "secret_values_recorded": False,
        "claim_boundary": {
            "supported": [
                "existence of guarded provider runner entrypoints referenced by Stage 116",
                "confirmation that current Stage 116 runner commands remain blocked before live execution",
                "a no-submission safety check before provider SDK execution work",
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
            "Clear Stage 111 and Stage 129 cutover authorization, then execute only Stage 133 authorized command "
            "records that still emit Stage 114 result records."
        ),
    }


def write_stage117_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
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
        "guarded_runner_count": result["guarded_runner_count"],
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
            fieldnames=("provider", "window_id", "stage116_status", "runner_script_exists", "stage116_runner_blocked", "ready", "missing_evidence"),
        )
        writer.writeheader()
        for record in result["runner_records"]:
            writer.writerow(
                {
                    "provider": record["provider"],
                    "window_id": record["window_id"],
                    "stage116_status": record["stage116_status"],
                    "runner_script_exists": record["runner_script_exists"],
                    "stage116_runner_blocked": record["stage116_runner_blocked"],
                    "ready": record["ready"],
                    "missing_evidence": "; ".join(record["missing_evidence"]),
                }
            )
    return paths


def print_stage117_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"guarded_runner_count: {result['guarded_runner_count']}/{result['runner_count']}")
    print(f"next_gate: {result['next_gate']}")
