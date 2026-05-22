from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


STAGE141_SCHEMA_VERSION = "qrope_stage141_provider_unlock_priority_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE139_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage139_provider_action_readiness_checklist" / "results.json"
DEFAULT_STAGE140_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage140_local_provider_configuration_readiness" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage141_provider_unlock_priority"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _by_provider(payload: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    if not isinstance(payload, dict):
        return {}
    return {str(record.get("provider")): record for record in payload.get("provider_records", []) if record.get("provider")}


def _priority_record(provider: str, stage139_record: dict[str, Any], stage140_record: dict[str, Any]) -> dict[str, Any]:
    missing_env = list(stage140_record.get("missing_env_groups", []))
    missing_sdk = list(stage140_record.get("missing_sdk_modules", []))
    prepared_jobs = int(stage139_record.get("prepared_job_count") or 0)
    runner_count = int(stage139_record.get("runner_command_count") or 0)
    authorized_runner_count = int(stage139_record.get("authorized_runner_command_count") or 0)
    env_missing_count = len(missing_env)
    sdk_missing_count = len(missing_sdk)
    already_ready_bonus = 1000 if stage140_record.get("ready_for_preflight_rerun") is True else 0
    # Lower score is better; already-ready providers sort first.
    priority_score = env_missing_count + (3 * sdk_missing_count) - already_ready_bonus
    minimal_unlock_actions: list[str] = []
    if missing_env:
        minimal_unlock_actions.append("Set local env groups without committing values: " + "; ".join(missing_env) + ".")
    if missing_sdk:
        minimal_unlock_actions.append("Install or expose SDK modules: " + ", ".join(missing_sdk) + ".")
    if not minimal_unlock_actions:
        minimal_unlock_actions.append("Rerun Stage 106/111/128/129/130/139; then execute only authorized Stage 133 commands.")
    return {
        "provider": provider,
        "priority_score": priority_score,
        "ready_for_preflight_rerun": stage140_record.get("ready_for_preflight_rerun") is True,
        "env_missing_count": env_missing_count,
        "sdk_missing_count": sdk_missing_count,
        "missing_env_groups": missing_env,
        "missing_sdk_modules": missing_sdk,
        "prepared_job_count": prepared_jobs,
        "runner_command_count": runner_count,
        "authorized_runner_command_count": authorized_runner_count,
        "stage139_first_blocker": stage139_record.get("first_blocker"),
        "minimal_unlock_actions": minimal_unlock_actions,
    }


def run_stage141_priority(
    *,
    stage139_results_path: Path = DEFAULT_STAGE139_RESULTS,
    stage140_results_path: Path = DEFAULT_STAGE140_RESULTS,
) -> dict[str, Any]:
    stage139 = _load_json(stage139_results_path)
    stage140 = _load_json(stage140_results_path)
    sources = [(stage139_results_path, stage139), (stage140_results_path, stage140)]
    missing_sources = [str(path.as_posix()) for path, payload in sources if payload is None]
    stage139_by_provider = _by_provider(stage139)
    stage140_by_provider = _by_provider(stage140)
    providers = sorted(set(stage139_by_provider) | set(stage140_by_provider))
    priority_records = [
        _priority_record(provider, stage139_by_provider.get(provider, {}), stage140_by_provider.get(provider, {}))
        for provider in providers
    ]
    priority_records.sort(key=lambda record: (record["priority_score"], record["sdk_missing_count"], record["env_missing_count"], record["provider"]))
    first_record = priority_records[0] if priority_records else {}
    first_provider = first_record.get("provider") if first_record else None
    first_ready = bool(first_record and first_record["ready_for_preflight_rerun"])
    return {
        "schema_version": STAGE141_SCHEMA_VERSION,
        "stage": "stage141_provider_unlock_priority",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": (
            "PROVIDER_UNLOCK_PRIORITY_READY_FOR_PREFLIGHT_RERUN"
            if first_ready
            else "PROVIDER_UNLOCK_PRIORITY_PREPARED_EXECUTION_BLOCKED"
        ),
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "stage139_decision": stage139.get("decision") if isinstance(stage139, dict) else None,
        "stage140_decision": stage140.get("decision") if isinstance(stage140, dict) else None,
        "provider_count": len(priority_records),
        "first_unlock_provider": first_provider,
        "first_unlock_ready_for_preflight_rerun": first_ready,
        "first_unlock_missing_env_groups": list(first_record.get("missing_env_groups", [])),
        "first_unlock_missing_sdk_modules": list(first_record.get("missing_sdk_modules", [])),
        "first_unlock_minimal_actions": list(first_record.get("minimal_unlock_actions", [])),
        "priority_records": priority_records,
        "no_hardware_submission": True,
        "provider_credentials_required": True,
        "secret_values_recorded": False,
        "claim_boundary": {
            "supported": [
                "provider unlock ordering based on non-secret env-key and SDK readiness evidence",
                "minimal first-provider unlock actions before Stage 106/111/129 reruns",
                "explicit separation from live provider submission and Stage 138 objective claims",
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
            "Complete the first provider's minimal unlock actions, rerun Stage 140, and only then rerun Stage 106/111/128/129/130/139 "
            "before any authorized Stage 133 runner command."
        ),
    }


def write_stage141_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "stage139_decision": result["stage139_decision"],
        "stage140_decision": result["stage140_decision"],
        "provider_count": result["provider_count"],
        "first_unlock_provider": result["first_unlock_provider"],
        "first_unlock_ready_for_preflight_rerun": result["first_unlock_ready_for_preflight_rerun"],
        "first_unlock_missing_env_groups": result["first_unlock_missing_env_groups"],
        "first_unlock_missing_sdk_modules": result["first_unlock_missing_sdk_modules"],
        "first_unlock_minimal_actions": result["first_unlock_minimal_actions"],
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
                "priority_score",
                "ready_for_preflight_rerun",
                "env_missing_count",
                "sdk_missing_count",
                "prepared_job_count",
                "runner_command_count",
                "authorized_runner_command_count",
            ),
        )
        writer.writeheader()
        for record in result["priority_records"]:
            writer.writerow({field: record.get(field) for field in writer.fieldnames})
    return paths


def print_stage141_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"first_unlock_provider: {result['first_unlock_provider']}")
    print(f"first_unlock_ready_for_preflight_rerun: {result['first_unlock_ready_for_preflight_rerun']}")
    print(f"next_gate: {result['next_gate']}")
