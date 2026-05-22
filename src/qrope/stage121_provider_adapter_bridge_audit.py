from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


STAGE121_SCHEMA_VERSION = "qrope_stage121_provider_adapter_bridge_audit_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE120_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage120_live_runner_orchestration_audit" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage121_provider_adapter_bridge_audit"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _probe_runner_help(script: str) -> dict[str, bool]:
    help_text = ""
    if script and Path(script).exists():
        help_text = subprocess.run(
            [sys.executable, script, "--help"],
            capture_output=True,
            text=True,
            check=False,
        ).stdout
    return {
        "accepts_stage118_results": "--stage118-results" in help_text,
        "accepts_stage129_results": "--stage129-results" in help_text,
        "has_allow_live_submit_flag": "--allow-live-submit" in help_text,
        "accepts_submitter_import_path": "--submitter" in help_text,
    }


def _runner_record(record: dict[str, Any]) -> dict[str, Any]:
    script = str(record.get("runner_script") or "")
    probe = _probe_runner_help(script)
    missing = []
    for key, marker in (
        ("accepts_stage118_results", "runner_missing_stage118_payload_input"),
        ("accepts_stage129_results", "runner_missing_stage129_cutover_input"),
        ("has_allow_live_submit_flag", "runner_missing_live_submit_flag"),
        ("accepts_submitter_import_path", "runner_missing_submitter_import_path"),
    ):
        if not probe[key]:
            missing.append(marker)
    return {
        "provider": record.get("provider"),
        "window_id": record.get("window_id"),
        "runner_script": script,
        **probe,
        "missing_evidence": missing,
        "ready": not missing,
    }


def run_stage121_audit(*, stage120_results_path: Path = DEFAULT_STAGE120_RESULTS) -> dict[str, Any]:
    stage120 = _load_json(stage120_results_path)
    missing_sources = [] if isinstance(stage120, dict) else [str(stage120_results_path.as_posix())]
    runner_records = [_runner_record(record) for record in stage120.get("runner_records", [])] if isinstance(stage120, dict) else []
    ready = bool(runner_records) and all(record["ready"] for record in runner_records) and not missing_sources
    return {
        "schema_version": STAGE121_SCHEMA_VERSION,
        "stage": "stage121_provider_adapter_bridge_audit",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": (
            "PROVIDER_ADAPTER_BRIDGE_READY_PROVIDER_ADAPTERS_REQUIRED"
            if ready
            else "PROVIDER_ADAPTER_BRIDGE_INCOMPLETE"
        ),
        "source_artifacts": [str(stage120_results_path.as_posix())],
        "missing_source_artifacts": missing_sources,
        "stage120_decision": stage120.get("decision") if isinstance(stage120, dict) else None,
        "runner_count": len(runner_records),
        "ready_runner_count": sum(1 for record in runner_records if record["ready"]),
        "runner_records": runner_records,
        "no_hardware_submission": True,
        "provider_credentials_required": True,
        "secret_values_recorded": False,
        "claim_boundary": {
            "supported": [
                "provider runner CLI can bind an explicit submitter callable by import path",
                "adapter binding remains behind Stage 111 readiness, Stage 118 payload loading, Stage 129 cutover authorization, and Stage 114 result validation",
                "live submission remains impossible without an explicit adapter selection",
            ],
            "excluded": [
                "hardware job submission",
                "provider credentials or secret values",
                "provider SDK adapter implementation",
                "real provider result records",
                "Stage 113 evidence assembly",
                "a noisy-hardware robustness result",
            ],
        },
        "next_gate": (
            "Use the Stage 121 adapter bridge only after Stage 106/111 readiness clears and Stage 129 authorizes "
            "cutover for the target provider."
        ),
    }


def write_stage121_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "stage120_decision": result["stage120_decision"],
        "runner_count": result["runner_count"],
        "ready_runner_count": result["ready_runner_count"],
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
                "accepts_stage118_results",
                "accepts_stage129_results",
                "has_allow_live_submit_flag",
                "accepts_submitter_import_path",
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
                    "accepts_stage118_results": record["accepts_stage118_results"],
                    "accepts_stage129_results": record["accepts_stage129_results"],
                    "has_allow_live_submit_flag": record["has_allow_live_submit_flag"],
                    "accepts_submitter_import_path": record["accepts_submitter_import_path"],
                    "ready": record["ready"],
                    "missing_evidence": "; ".join(record["missing_evidence"]),
                }
            )
    return paths


def print_stage121_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"ready_runner_count: {result['ready_runner_count']}/{result['runner_count']}")
    print(f"next_gate: {result['next_gate']}")
