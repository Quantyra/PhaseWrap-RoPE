from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


STAGE120_SCHEMA_VERSION = "qrope_stage120_live_runner_orchestration_audit_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE116_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage116_provider_runner_plan" / "results.json"
DEFAULT_STAGE118_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage118_provider_payload_dry_run_audit" / "results.json"
DEFAULT_STAGE119_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage119_provider_result_rehearsal_audit" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage120_live_runner_orchestration_audit"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _probe_runner(command: str) -> dict[str, Any]:
    parts = command.split()
    script = parts[1] if len(parts) > 1 else ""
    help_text = ""
    if script and Path(script).exists():
        help_text = subprocess.run(
            [sys.executable, script, "--help"],
            capture_output=True,
            text=True,
            check=False,
        ).stdout
    return {
        "runner_command": command,
        "runner_script": script,
        "accepts_stage118_results": "--stage118-results" in help_text,
        "accepts_stage129_results": "--stage129-results" in help_text,
        "has_allow_live_submit_flag": "--allow-live-submit" in help_text,
    }


def _runner_record(record: dict[str, Any]) -> dict[str, Any]:
    probe = _probe_runner(str(record.get("runner_command", "")))
    missing = []
    if not probe["accepts_stage118_results"]:
        missing.append("runner_missing_stage118_payload_input")
    if not probe["accepts_stage129_results"]:
        missing.append("runner_missing_stage129_cutover_input")
    if not probe["has_allow_live_submit_flag"]:
        missing.append("runner_missing_live_submit_flag")
    return {
        "provider": record.get("provider"),
        "window_id": record.get("window_id"),
        "stage116_status": record.get("status"),
        "job_count": record.get("job_count"),
        "runner_command": record.get("runner_command"),
        "runner_script": probe["runner_script"],
        "accepts_stage118_results": probe["accepts_stage118_results"],
        "accepts_stage129_results": probe["accepts_stage129_results"],
        "has_allow_live_submit_flag": probe["has_allow_live_submit_flag"],
        "missing_evidence": missing,
        "ready": not missing,
    }


def run_stage120_audit(
    *,
    stage116_results_path: Path = DEFAULT_STAGE116_RESULTS,
    stage118_results_path: Path = DEFAULT_STAGE118_RESULTS,
    stage119_results_path: Path = DEFAULT_STAGE119_RESULTS,
) -> dict[str, Any]:
    stage116 = _load_json(stage116_results_path)
    stage118 = _load_json(stage118_results_path)
    stage119 = _load_json(stage119_results_path)
    sources = [(stage116_results_path, stage116), (stage118_results_path, stage118), (stage119_results_path, stage119)]
    missing_sources = [str(path.as_posix()) for path, payload in sources if payload is None]
    runner_records = [_runner_record(record) for record in stage116.get("runner_records", [])] if isinstance(stage116, dict) else []
    ready = bool(runner_records) and all(record["ready"] for record in runner_records) and not missing_sources
    return {
        "schema_version": STAGE120_SCHEMA_VERSION,
        "stage": "stage120_live_runner_orchestration_audit",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": (
            "LIVE_RUNNER_ORCHESTRATION_READY_ADAPTER_REQUIRED"
            if ready
            else "LIVE_RUNNER_ORCHESTRATION_INCOMPLETE"
        ),
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "stage116_decision": stage116.get("decision") if isinstance(stage116, dict) else None,
        "stage118_decision": stage118.get("decision") if isinstance(stage118, dict) else None,
        "stage119_decision": stage119.get("decision") if isinstance(stage119, dict) else None,
        "runner_count": len(runner_records),
        "ready_runner_count": sum(1 for record in runner_records if record["ready"]),
        "job_count": sum(int(record.get("job_count") or 0) for record in runner_records),
        "runner_records": runner_records,
        "no_hardware_submission": True,
        "provider_credentials_required": True,
        "secret_values_recorded": False,
        "claim_boundary": {
            "supported": [
                "runner orchestration can load Stage 118 payload inputs before live submission",
                "runner orchestration requires Stage 129 cutover authorization before invoking provider submitters",
                "runner guard has a result-contract validation path before writing Stage 114 provider results",
                "CLI still refuses live submission without an explicit provider adapter",
            ],
            "excluded": [
                "hardware job submission",
                "provider credentials or secret values",
                "real provider result records",
                "Stage 113 evidence assembly",
                "a noisy-hardware robustness result",
            ],
        },
        "next_gate": (
            "Clear Stage 106/111 readiness and Stage 129 cutover authorization, then run guarded live submissions "
            "with --allow-live-submit and --stage129-results."
        ),
    }


def write_stage120_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
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
        "stage118_decision": result["stage118_decision"],
        "stage119_decision": result["stage119_decision"],
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
            fieldnames=(
                "provider",
                "window_id",
                "stage116_status",
                "job_count",
                "accepts_stage118_results",
                "accepts_stage129_results",
                "has_allow_live_submit_flag",
                "ready",
                "missing_evidence",
            ),
        )
        writer.writeheader()
        for record in result["runner_records"]:
            writer.writerow(
                {
                    "provider": record["provider"],
                    "window_id": record["window_id"],
                    "stage116_status": record["stage116_status"],
                    "job_count": record["job_count"],
                    "accepts_stage118_results": record["accepts_stage118_results"],
                    "accepts_stage129_results": record["accepts_stage129_results"],
                    "has_allow_live_submit_flag": record["has_allow_live_submit_flag"],
                    "ready": record["ready"],
                    "missing_evidence": "; ".join(record["missing_evidence"]),
                }
            )
    return paths


def print_stage120_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"ready_runner_count: {result['ready_runner_count']}/{result['runner_count']}")
    print(f"job_count: {result['job_count']}")
    print(f"next_gate: {result['next_gate']}")
