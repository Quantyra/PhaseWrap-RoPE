from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


STAGE133_SCHEMA_VERSION = "qrope_stage133_authorized_runner_command_packet_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE116_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage116_provider_runner_plan" / "results.json"
DEFAULT_STAGE129_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage129_live_cutover_authorization_audit" / "results.json"
DEFAULT_STAGE132_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage132_guarded_sdk_factory_implementation_audit" / "results.json"
DEFAULT_STAGE163_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage163_first_provider_prerun_lock" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage133_authorized_runner_command_packet"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)
SUBMITTERS = {
    "amazon_braket": "qrope.provider_adapters.amazon_braket:submit",
    "ibm_runtime": "qrope.provider_adapters.ibm_runtime:submit",
}
STAGE116_READY = "PROVIDER_RUNNER_PLAN_READY_FOR_EXECUTION"
STAGE129_AUTHORIZED = "LIVE_CUTOVER_AUTHORIZED"
STAGE132_READY = "GUARDED_SDK_FACTORIES_IMPLEMENTED_CUTOVER_BLOCKED"


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _provider_record(payload: dict[str, Any] | None, provider: str) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {}
    for record in payload.get("provider_records", []):
        if record.get("provider") == provider:
            return record
    return {}


def _command_record(
    runner: dict[str, Any],
    stage116: dict[str, Any] | None,
    stage129: dict[str, Any] | None,
    stage132: dict[str, Any] | None,
) -> dict[str, Any]:
    provider = str(runner.get("provider"))
    stage129_record = _provider_record(stage129, provider)
    stage132_record = _provider_record(stage132, provider)
    runner_command = str(runner.get("runner_command", ""))
    blockers = []
    if not isinstance(stage116, dict):
        blockers.append("stage116:runner_plan_missing")
    if not isinstance(stage129, dict) or stage129.get("decision") != STAGE129_AUTHORIZED:
        blockers.append("stage129:live_cutover_not_authorized")
    if not isinstance(stage132, dict) or stage132.get("decision") != STAGE132_READY:
        blockers.append("stage132:guarded_factory_audit_not_ready")
    blockers.extend(f"stage116:{item}" for item in runner.get("blockers", []))
    blockers.extend(f"stage129:{item}" for item in stage129_record.get("blockers", []))
    if runner.get("status") != "ready_to_run":
        blockers.append("stage116:runner_not_ready")
    if runner.get("provider_ready") is not True:
        blockers.append("stage116:provider_not_ready")
    if stage129_record.get("cutover_authorized") is not True:
        blockers.append("stage129:cutover_not_authorized")
    if stage132_record.get("ready") is not True:
        blockers.append("stage132:guarded_factory_not_ready")
    if "--stage111-results" not in runner_command:
        blockers.append("runner_command_missing_stage111_results")
    if "--stage118-results" not in runner_command:
        blockers.append("runner_command_missing_stage118_results")
    if "--stage129-results" not in runner_command:
        blockers.append("runner_command_missing_stage129_results")
    submitter = SUBMITTERS.get(provider, "")
    if not submitter:
        blockers.append("submitter_import_path_missing")
    authorized = not blockers
    stage163_results_path = DEFAULT_STAGE163_RESULTS.as_posix() if provider == "ibm_runtime" else ""
    stage163_argument = f" --stage163-results {stage163_results_path}" if stage163_results_path else ""
    live_submit_command = (
        f"{runner_command}{stage163_argument} --allow-live-submit --submitter {submitter}"
        if authorized and submitter
        else ""
    )
    return {
        "provider": provider,
        "window_id": runner.get("window_id"),
        "job_count": runner.get("job_count"),
        "runner_status": runner.get("status"),
        "cutover_authorized": stage129_record.get("cutover_authorized"),
        "guarded_factory_ready": stage132_record.get("ready"),
        "runner_command": runner_command,
        "live_submit_command": live_submit_command,
        "submitter_import_path": submitter,
        "stage163_results_path": stage163_results_path,
        "command_authorized": authorized,
        "live_submit_command_available": authorized,
        "blockers": sorted(set(blockers)),
    }


def run_stage133_packet(
    *,
    stage116_results_path: Path = DEFAULT_STAGE116_RESULTS,
    stage129_results_path: Path = DEFAULT_STAGE129_RESULTS,
    stage132_results_path: Path = DEFAULT_STAGE132_RESULTS,
) -> dict[str, Any]:
    stage116 = _load_json(stage116_results_path)
    stage129 = _load_json(stage129_results_path)
    stage132 = _load_json(stage132_results_path)
    sources = [(stage116_results_path, stage116), (stage129_results_path, stage129), (stage132_results_path, stage132)]
    missing_sources = [str(path.as_posix()) for path, payload in sources if payload is None]
    command_records = [
        _command_record(runner, stage116, stage129, stage132)
        for runner in (stage116.get("runner_records", []) if isinstance(stage116, dict) else [])
    ]
    authorized_count = sum(1 for record in command_records if record["command_authorized"])
    return {
        "schema_version": STAGE133_SCHEMA_VERSION,
        "stage": "stage133_authorized_runner_command_packet",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": (
            "AUTHORIZED_RUNNER_COMMANDS_READY"
            if command_records and authorized_count == len(command_records) and not missing_sources
            else "AUTHORIZED_RUNNER_COMMANDS_PREPARED_EXECUTION_BLOCKED"
        ),
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "stage116_decision": stage116.get("decision") if isinstance(stage116, dict) else None,
        "stage129_decision": stage129.get("decision") if isinstance(stage129, dict) else None,
        "stage132_decision": stage132.get("decision") if isinstance(stage132, dict) else None,
        "runner_count": len(command_records),
        "authorized_runner_count": authorized_count,
        "job_count": sum(int(record.get("job_count") or 0) for record in command_records),
        "command_records": command_records,
        "no_hardware_submission": True,
        "provider_credentials_required": True,
        "secret_values_recorded": False,
        "claim_boundary": {
            "supported": [
                "declared live-submit command templates include Stage 111, Stage 118, and Stage 129 evidence inputs",
                "live-submit command strings require source-level Stage 116 per-runner readiness and Stage 129 cutover authorization",
                "provider submitter import paths are attached to each provider/window runner command",
                "IBM Runtime live-submit command strings carry the Stage 163 pre-run lock path for boundary verification",
                "live-submit command strings are emitted only for records with command_authorized=true",
                "current commands remain blocked until per-runner Stage 116 readiness, Stage 129 cutover, and Stage 132 factory readiness all align",
            ],
            "excluded": [
                "hardware job submission",
                "provider credentials or secret values",
                "live provider SDK client creation",
                "real provider result records",
                "a noisy-hardware robustness result",
            ],
        },
        "next_gate": (
            "After Stage 106/111 readiness clears and Stage 129 authorizes the target provider, execute only command "
            "records with command_authorized=true, then validate Stage 114 result files through Stage 115."
        ),
    }


def write_stage133_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
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
        "stage129_decision": result["stage129_decision"],
        "stage132_decision": result["stage132_decision"],
        "runner_count": result["runner_count"],
        "authorized_runner_count": result["authorized_runner_count"],
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
                "job_count",
                "command_authorized",
                "submitter_import_path",
                "stage163_results_path",
                "live_submit_command_available",
                "blockers",
                "live_submit_command",
            ),
        )
        writer.writeheader()
        for record in result["command_records"]:
            writer.writerow(
                {
                    "provider": record["provider"],
                    "window_id": record["window_id"],
                    "job_count": record["job_count"],
                    "command_authorized": record["command_authorized"],
                    "submitter_import_path": record["submitter_import_path"],
                    "stage163_results_path": record["stage163_results_path"],
                    "live_submit_command_available": record["live_submit_command_available"],
                    "blockers": "; ".join(record["blockers"]),
                    "live_submit_command": record["live_submit_command"],
                }
            )
    return paths


def print_stage133_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"authorized_runner_count: {result['authorized_runner_count']}/{result['runner_count']}")
    print(f"job_count: {result['job_count']}")
    print(f"next_gate: {result['next_gate']}")
