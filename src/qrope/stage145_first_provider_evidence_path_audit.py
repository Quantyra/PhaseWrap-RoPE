from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


STAGE145_SCHEMA_VERSION = "qrope_stage145_first_provider_evidence_path_audit_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE113_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage113_job_result_evidence_assembler" / "results.json"
DEFAULT_STAGE114_MANIFEST = DEFAULT_ARTIFACT_ROOT / "stage114_provider_result_capture_contract" / "manifest.json"
DEFAULT_STAGE115_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage115_provider_result_collector" / "results.json"
DEFAULT_STAGE133_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage133_authorized_runner_command_packet" / "results.json"
DEFAULT_STAGE135_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage135_post_collection_claim_gate_sequence" / "results.json"
DEFAULT_STAGE137_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage137_auditability_metric_evaluator" / "results.json"
DEFAULT_STAGE144_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage144_post_configuration_rerun_chain_audit" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage145_first_provider_evidence_path_audit"
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


def _shards_for_provider(stage115: dict[str, Any] | None, provider: str) -> list[dict[str, Any]]:
    if not isinstance(stage115, dict):
        return []
    return [record for record in stage115.get("shard_records", []) if record.get("provider") == provider]


def _scoped_commands(provider: str) -> list[str]:
    return [
        f"python scripts/run_stage115_provider_result_collector.py --provider {provider} --write-stage113-input",
        f"python scripts/run_stage113_job_result_evidence_assembler.py --provider {provider} --write-evidence",
        f"python scripts/run_stage109_window_evidence_intake_validator.py --provider {provider}",
        f"python scripts/run_stage137_auditability_metric_evaluator.py --provider {provider}",
        "python scripts/run_stage110_replicated_advantage_claim_gate.py",
        "python scripts/run_stage138_objective_claim_gate.py",
    ]


def _stage144_ready(stage144: dict[str, Any] | None) -> bool:
    return bool(
        isinstance(stage144, dict)
        and stage144.get("decision") == "POST_CONFIGURATION_RERUN_CHAIN_READY_FOR_AUTHORIZED_RUNNER"
        and stage144.get("first_blocked_transition") is None
        and stage144.get("ready_transition_count") == stage144.get("transition_count")
        and int(stage144.get("transition_count") or 0) > 0
        and int(stage144.get("first_provider_authorized_runner_count") or 0) > 0
    )


def run_stage145_audit(
    *,
    stage113_results_path: Path = DEFAULT_STAGE113_RESULTS,
    stage114_manifest_path: Path = DEFAULT_STAGE114_MANIFEST,
    stage115_results_path: Path = DEFAULT_STAGE115_RESULTS,
    stage133_results_path: Path = DEFAULT_STAGE133_RESULTS,
    stage135_results_path: Path = DEFAULT_STAGE135_RESULTS,
    stage137_results_path: Path = DEFAULT_STAGE137_RESULTS,
    stage144_results_path: Path = DEFAULT_STAGE144_RESULTS,
) -> dict[str, Any]:
    sources = {
        "stage113": (stage113_results_path, _load_json(stage113_results_path)),
        "stage114": (stage114_manifest_path, _load_json(stage114_manifest_path)),
        "stage115": (stage115_results_path, _load_json(stage115_results_path)),
        "stage133": (stage133_results_path, _load_json(stage133_results_path)),
        "stage135": (stage135_results_path, _load_json(stage135_results_path)),
        "stage137": (stage137_results_path, _load_json(stage137_results_path)),
        "stage144": (stage144_results_path, _load_json(stage144_results_path)),
    }
    payloads = {stage: payload for stage, (_, payload) in sources.items()}
    missing_sources = [str(path.as_posix()) for path, payload in sources.values() if payload is None]
    provider = str(payloads["stage144"].get("first_unlock_provider", "")) if isinstance(payloads["stage144"], dict) else ""
    commands = _commands_for_provider(payloads["stage133"], provider)
    authorized_commands = [record for record in commands if record.get("command_authorized") is True]
    shards = _shards_for_provider(payloads["stage115"], provider)
    ready_shards = [record for record in shards if record.get("ready") is True]
    missing_jobs = sum(int(record.get("missing_job_count") or 0) for record in shards)
    expected_jobs = sum(int(record.get("expected_job_count") or 0) for record in shards)
    result_records = sum(int(record.get("result_record_count") or 0) for record in shards)
    stage144_ready = _stage144_ready(payloads["stage144"])
    stage115_provider_ready = bool(shards) and len(ready_shards) == len(shards)
    stage113_ready = bool(
        isinstance(payloads["stage113"], dict)
        and payloads["stage113"].get("decision") in {
            "JOB_RESULTS_READY_FOR_STAGE109_EVIDENCE_ASSEMBLY",
            "JOB_RESULTS_ASSEMBLED_INTO_STAGE109_EVIDENCE",
        }
    )
    stage137_ready = bool(
        isinstance(payloads["stage137"], dict)
        and payloads["stage137"].get("decision") == "AUDITABILITY_METRICS_READY_FOR_CLAIM_GATE"
    )

    readiness_records = [
        {
            "name": "post_configuration_authorized_runner_chain",
            "ready": stage144_ready,
            "decision": payloads["stage144"].get("decision") if isinstance(payloads["stage144"], dict) else None,
            "next_command": payloads["stage144"].get("next_command") if isinstance(payloads["stage144"], dict) and not stage144_ready else "",
            "blockers": [
                blocker
                for blocker, blocked in (
                    ("stage144_not_ready_for_authorized_runner", not isinstance(payloads["stage144"], dict) or payloads["stage144"].get("decision") != "POST_CONFIGURATION_RERUN_CHAIN_READY_FOR_AUTHORIZED_RUNNER"),
                    ("stage144_has_blocked_transition", isinstance(payloads["stage144"], dict) and payloads["stage144"].get("first_blocked_transition") is not None),
                    ("stage144_transition_counts_incomplete", isinstance(payloads["stage144"], dict) and payloads["stage144"].get("ready_transition_count") != payloads["stage144"].get("transition_count")),
                    ("stage144_no_authorized_runner_count", isinstance(payloads["stage144"], dict) and int(payloads["stage144"].get("first_provider_authorized_runner_count") or 0) <= 0),
                )
                if blocked
            ],
        },
        {
            "name": "first_provider_authorized_runner_commands",
            "ready": bool(authorized_commands),
            "decision": payloads["stage133"].get("decision") if isinstance(payloads["stage133"], dict) else None,
            "next_command": "python scripts/run_stage133_authorized_runner_command_packet.py" if not authorized_commands else "",
        },
        {
            "name": "first_provider_stage115_result_shards",
            "ready": stage115_provider_ready,
            "decision": payloads["stage115"].get("decision") if isinstance(payloads["stage115"], dict) else None,
            "next_command": _scoped_commands(provider)[0] if provider and not stage115_provider_ready else "",
        },
        {
            "name": "first_provider_stage113_evidence_assembly",
            "ready": stage113_ready,
            "decision": payloads["stage113"].get("decision") if isinstance(payloads["stage113"], dict) else None,
            "next_command": _scoped_commands(provider)[1] if provider and stage115_provider_ready and not stage113_ready else "",
        },
        {
            "name": "first_provider_auditability_evaluator",
            "ready": stage137_ready,
            "decision": payloads["stage137"].get("decision") if isinstance(payloads["stage137"], dict) else None,
            "next_command": _scoped_commands(provider)[3] if provider and stage113_ready and not stage137_ready else "",
        },
    ]
    first_blocked = next((record for record in readiness_records if not record["ready"]), None)
    ready = (
        bool(provider)
        and not missing_sources
        and stage144_ready
        and bool(authorized_commands)
        and stage115_provider_ready
        and stage113_ready
    )
    return {
        "schema_version": STAGE145_SCHEMA_VERSION,
        "stage": "stage145_first_provider_evidence_path_audit",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": (
            "FIRST_PROVIDER_EVIDENCE_PATH_READY_FOR_CLAIM_GATES"
            if ready
            else "FIRST_PROVIDER_EVIDENCE_PATH_PREPARED_RESULTS_BLOCKED"
        ),
        "source_artifacts": [str(path.as_posix()) for path, _ in sources.values()],
        "missing_source_artifacts": missing_sources,
        "first_unlock_provider": provider,
        "first_provider_runner_command_count": len(commands),
        "first_provider_authorized_runner_count": len(authorized_commands),
        "first_provider_shard_count": len(shards),
        "first_provider_ready_shard_count": len(ready_shards),
        "first_provider_expected_job_count": expected_jobs,
        "first_provider_result_record_count": result_records,
        "first_provider_missing_job_count": missing_jobs,
        "first_blocked_readiness_record": first_blocked,
        "next_command": first_blocked["next_command"] if first_blocked else "",
        "readiness_records": readiness_records,
        "first_provider_shard_records": shards,
        "provider_scoped_commands": _scoped_commands(provider) if provider else [],
        "stage135_decision": payloads["stage135"].get("decision") if isinstance(payloads["stage135"], dict) else None,
        "stage114_required_result_fields": payloads["stage114"].get("required_result_fields", []) if isinstance(payloads["stage114"], dict) else [],
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "claim_boundary": {
            "supported": [
                "first-provider evidence intake readiness after authorized IBM Runtime execution",
                "Stage 144 ready-transition and authorized-runner count enforcement before provider result collection",
                "provider-scoped Stage 115, Stage 113, Stage 109, and Stage 137 command sequence",
                "explicit blocker reporting before Stage 138 objective wording",
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
            "Clear Stage 144 and Stage 133 authorization first. After IBM Runtime result JSONL files exist, run the "
            "provider-scoped collection and evidence commands before Stage 110/138 claim gates."
        ),
    }


def write_stage145_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
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
        "first_provider_runner_command_count": result["first_provider_runner_command_count"],
        "first_provider_authorized_runner_count": result["first_provider_authorized_runner_count"],
        "first_provider_shard_count": result["first_provider_shard_count"],
        "first_provider_ready_shard_count": result["first_provider_ready_shard_count"],
        "first_provider_expected_job_count": result["first_provider_expected_job_count"],
        "first_provider_result_record_count": result["first_provider_result_record_count"],
        "first_provider_missing_job_count": result["first_provider_missing_job_count"],
        "first_blocked_readiness_record": result["first_blocked_readiness_record"],
        "next_command": result["next_command"],
        "stage135_decision": result["stage135_decision"],
        "stage114_required_result_fields": result["stage114_required_result_fields"],
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
        writer = csv.DictWriter(handle, fieldnames=("name", "ready", "decision", "blockers", "next_command"))
        writer.writeheader()
        for record in result["readiness_records"]:
            writer.writerow(
                {
                    "name": record["name"],
                    "ready": record["ready"],
                    "decision": record["decision"],
                    "blockers": "; ".join(str(blocker) for blocker in record.get("blockers", [])),
                    "next_command": record["next_command"],
                }
            )
    return paths


def print_stage145_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"first_unlock_provider: {result['first_unlock_provider']}")
    print(f"first_provider_ready_shard_count: {result['first_provider_ready_shard_count']}/{result['first_provider_shard_count']}")
    print(f"first_provider_missing_job_count: {result['first_provider_missing_job_count']}")
    blocked = result["first_blocked_readiness_record"]
    print(f"first_blocked_readiness_record: {blocked['name'] if blocked else ''}")
    print(f"next_command: {result['next_command']}")
