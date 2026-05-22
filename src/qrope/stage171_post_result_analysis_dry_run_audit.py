from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


STAGE171_SCHEMA_VERSION = "qrope_stage171_post_result_analysis_dry_run_audit_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE160_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage160_first_provider_post_run_analysis_packet" / "results.json"
DEFAULT_STAGE170_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage170_ibm_hardware_pause_resolution_packet" / "results.json"
DEFAULT_SCRIPT_ROOT = Path("scripts")
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage171_post_result_analysis_dry_run_audit"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)
STAGE160_AWAITING_RESULTS = "FIRST_PROVIDER_POST_RUN_ANALYSIS_PACKET_READY_AWAITING_PROVIDER_RESULTS"
STAGE160_SEQUENCE_READY = "FIRST_PROVIDER_POST_RUN_ANALYSIS_SEQUENCE_READY"
STAGE170_PAUSE_READY = "IBM_HARDWARE_PAUSE_READY_FOR_CREDIT_PROVIDER_RESOLUTION"
STAGE170_FINAL_GO_READY = "IBM_HARDWARE_PAUSE_READY_FOR_FINAL_HUMAN_GO_NO_GO"
EXPECTED_STAGE_SEQUENCE = [
    "stage164",
    "stage115",
    "stage113",
    "stage101",
    "stage103",
    "stage136",
    "stage137",
    "stage148",
    "stage109",
    "stage110",
    "stage138",
    "stage135",
]
FORBIDDEN_COMMAND_FRAGMENTS = ["--allow-live-submit", "IBM_QUANTUM_TOKEN", "crn:v1"]


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _script_path_from_command(command: str, script_root: Path) -> Path | None:
    parts = command.strip().split()
    if len(parts) < 2 or parts[0] != "python":
        return None
    script = Path(parts[1])
    if script.parts and script.parts[0] == script_root.name:
        return script
    return None


def _command_record(record: dict[str, Any], script_root: Path) -> dict[str, Any]:
    command = str(record.get("command") or "")
    script_path = _script_path_from_command(command, script_root)
    forbidden_fragments = [fragment for fragment in FORBIDDEN_COMMAND_FRAGMENTS if fragment in command]
    blockers = []
    if script_path is None:
        blockers.append("command_not_python_script_invocation")
    elif not script_path.exists():
        blockers.append("script_missing")
    if record.get("hardware_submission_command") is not False:
        blockers.append("hardware_submission_command_flagged")
    if forbidden_fragments:
        blockers.append("forbidden_command_fragment_present")
    return {
        "order": record.get("order"),
        "stage_id": record.get("stage_id"),
        "command": command,
        "script_path": str(script_path.as_posix()) if script_path is not None else None,
        "script_exists": bool(script_path and script_path.exists()),
        "hardware_submission_command": record.get("hardware_submission_command"),
        "forbidden_fragments": forbidden_fragments,
        "ready": not blockers,
        "blockers": sorted(set(blockers)),
    }


def run_stage171_dry_run_audit(
    *,
    stage160_results_path: Path = DEFAULT_STAGE160_RESULTS,
    stage170_results_path: Path = DEFAULT_STAGE170_RESULTS,
    script_root: Path = DEFAULT_SCRIPT_ROOT,
) -> dict[str, Any]:
    stage160 = _load_json(stage160_results_path)
    stage170 = _load_json(stage170_results_path)
    sources = [(stage160_results_path, stage160), (stage170_results_path, stage170)]
    missing_sources = [str(path.as_posix()) for path, payload in sources if not isinstance(payload, dict)]
    command_records = [
        _command_record(record, script_root)
        for record in (stage160.get("command_records", []) if isinstance(stage160, dict) else [])
        if isinstance(record, dict)
    ]
    observed_stage_sequence = [str(record.get("stage_id")) for record in command_records]
    blockers: list[str] = []
    if missing_sources:
        blockers.append("source_artifacts_missing")
    stage160_decision = stage160.get("decision") if isinstance(stage160, dict) else None
    if stage160_decision not in {STAGE160_AWAITING_RESULTS, STAGE160_SEQUENCE_READY}:
        blockers.append("stage160_post_run_packet_not_ready")
    stage170_decision = stage170.get("decision") if isinstance(stage170, dict) else None
    if stage170_decision not in {STAGE170_PAUSE_READY, STAGE170_FINAL_GO_READY}:
        blockers.append("stage170_pause_packet_not_ready")
    if len(command_records) != len(EXPECTED_STAGE_SEQUENCE):
        blockers.append("post_result_command_count_mismatch")
    if observed_stage_sequence != EXPECTED_STAGE_SEQUENCE:
        blockers.append("post_result_stage_sequence_mismatch")
    if any(not record["ready"] for record in command_records):
        blockers.append("post_result_command_records_not_ready")
    if isinstance(stage160, dict) and stage160.get("runnable_hardware_commands_recorded") is not False:
        blockers.append("stage160_runnable_hardware_commands_recorded")
    if isinstance(stage170, dict) and stage170.get("runnable_commands_recorded") is not False:
        blockers.append("stage170_runnable_commands_recorded")
    provider_results_missing = bool(stage160.get("missing_job_count")) if isinstance(stage160, dict) else True
    decision = (
        "POST_RESULT_ANALYSIS_DRY_RUN_AUDIT_INCOMPLETE"
        if missing_sources
        else "POST_RESULT_ANALYSIS_DRY_RUN_READY_AWAITING_PROVIDER_RESULTS"
        if not blockers and provider_results_missing
        else "POST_RESULT_ANALYSIS_DRY_RUN_READY_FOR_RESULT_INTERPRETATION"
        if not blockers
        else "POST_RESULT_ANALYSIS_DRY_RUN_AUDIT_BLOCKED"
    )
    return {
        "schema_version": STAGE171_SCHEMA_VERSION,
        "stage": "stage171_post_result_analysis_dry_run_audit",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": decision,
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "stage160_decision": stage160_decision,
        "stage170_decision": stage170_decision,
        "first_unlock_provider": stage170.get("first_unlock_provider") if isinstance(stage170, dict) else None,
        "expected_stage_sequence": EXPECTED_STAGE_SEQUENCE,
        "observed_stage_sequence": observed_stage_sequence,
        "command_count": len(command_records),
        "command_records": command_records,
        "script_ready_count": sum(1 for record in command_records if record["script_exists"]),
        "provider_results_missing": provider_results_missing,
        "missing_job_count": stage160.get("missing_job_count") if isinstance(stage160, dict) else None,
        "blockers": sorted(set(blockers)),
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "runnable_commands_recorded": False,
        "claim_boundary": {
            "supported": [
                "no-submit validation that the Stage160 post-result command sequence references present local scripts",
                "no-submit validation that the post-result sequence remains ordered from lock verification through objective claim gate",
                "explicit separation between result-analysis readiness and missing provider result records",
            ],
            "excluded": [
                "hardware job submission",
                "execution of the post-result command sequence",
                "provider credentials or secret values",
                "IBM credit balance or dollar cost verification",
                "a noisy-hardware robustness or auditability conclusion",
            ],
        },
        "next_gate": (
            "After provider result records exist and Stage164 verifies the lock, run the Stage160 sequence in the validated "
            "order before interpreting robustness or auditability."
        ),
    }


def write_stage171_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "stage160_decision": result["stage160_decision"],
        "stage170_decision": result["stage170_decision"],
        "first_unlock_provider": result["first_unlock_provider"],
        "command_count": result["command_count"],
        "script_ready_count": result["script_ready_count"],
        "provider_results_missing": result["provider_results_missing"],
        "missing_job_count": result["missing_job_count"],
        "blockers": result["blockers"],
        "no_hardware_submission": result["no_hardware_submission"],
        "provider_credentials_required": result["provider_credentials_required"],
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
            fieldnames=("order", "stage_id", "script_path", "script_exists", "hardware_submission_command", "ready", "blockers"),
        )
        writer.writeheader()
        for record in result["command_records"]:
            writer.writerow({**{field: record.get(field) for field in writer.fieldnames}, "blockers": "; ".join(record["blockers"])})
    return paths


def print_stage171_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"command_count: {result['command_count']}")
    print(f"script_ready_count: {result['script_ready_count']}")
    print(f"provider_results_missing: {result['provider_results_missing']}")
    print(f"blockers: {', '.join(result['blockers'])}")
    print(f"next_gate: {result['next_gate']}")
