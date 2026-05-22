from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


STAGE144_SCHEMA_VERSION = "qrope_stage144_post_configuration_rerun_chain_audit_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE106_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage106_hardware_execution_preflight" / "results.json"
DEFAULT_STAGE111_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage111_provider_sdk_backend_discovery" / "results.json"
DEFAULT_STAGE128_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage128_sdk_client_factory_audit" / "results.json"
DEFAULT_STAGE129_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage129_live_cutover_authorization_audit" / "results.json"
DEFAULT_STAGE130_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage130_live_cutover_remediation_packet" / "results.json"
DEFAULT_STAGE133_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage133_authorized_runner_command_packet" / "results.json"
DEFAULT_STAGE138_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage138_objective_claim_gate" / "results.json"
DEFAULT_STAGE139_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage139_provider_action_readiness_checklist" / "results.json"
DEFAULT_STAGE140_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage140_local_provider_configuration_readiness" / "results.json"
DEFAULT_STAGE141_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage141_provider_unlock_priority" / "results.json"
DEFAULT_STAGE142_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage142_first_provider_unlock_handoff" / "results.json"
DEFAULT_STAGE143_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage143_first_provider_handoff_safety_audit" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage144_post_configuration_rerun_chain_audit"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)
RERUN_COMMANDS = [
    "python scripts/run_stage140_local_provider_configuration_readiness.py --load-dotenv",
    "python scripts/run_stage106_hardware_execution_preflight.py --load-dotenv",
    "python scripts/run_stage111_provider_sdk_backend_discovery.py",
    "python scripts/run_stage128_sdk_client_factory_audit.py --load-dotenv",
    "python scripts/run_stage129_live_cutover_authorization_audit.py",
    "python scripts/run_stage130_live_cutover_remediation_packet.py",
    "python scripts/run_stage139_provider_action_readiness_checklist.py",
    "python scripts/run_stage141_provider_unlock_priority.py",
    "python scripts/run_stage142_first_provider_unlock_handoff.py",
    "python scripts/run_stage143_first_provider_handoff_safety_audit.py",
    "python scripts/run_stage133_authorized_runner_command_packet.py",
]


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _provider_record(payload: dict[str, Any] | None, provider: str) -> dict[str, Any] | None:
    if not isinstance(payload, dict):
        return None
    for record in payload.get("provider_records", []):
        if record.get("provider") == provider:
            return record
    return None


def _commands_for_provider(payload: dict[str, Any] | None, provider: str) -> list[dict[str, Any]]:
    if not isinstance(payload, dict):
        return []
    return [record for record in payload.get("command_records", []) if record.get("provider") == provider]


def _first_unlock_provider(stage141: dict[str, Any] | None, stage142: dict[str, Any] | None, stage143: dict[str, Any] | None) -> str | None:
    for payload in (stage143, stage142, stage141):
        if isinstance(payload, dict) and payload.get("first_unlock_provider"):
            return str(payload["first_unlock_provider"])
    return None


def _transition(
    *,
    stage: str,
    label: str,
    ready: bool,
    observed: Any,
    required: Any,
    next_command: str,
    blockers: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "stage": stage,
        "label": label,
        "ready": ready,
        "observed": observed,
        "required": required,
        "blockers": blockers or [],
        "next_command": "" if ready else next_command,
    }


def _bool(value: Any) -> bool:
    return value is True


def _stage140_first_provider_ready(record: dict[str, Any] | None) -> bool:
    if not record:
        return False
    tolerated_context_blockers = {"stage139_provider_already_cutover_authorized"}
    context_blockers = set(str(blocker) for blocker in record.get("stage139_context_blockers", []))
    return bool(
        (
            record.get("ready_for_preflight_rerun") is True
            or (
                record.get("env_ready_for_stage106") is True
                and record.get("sdk_ready_for_stage111") is True
                and context_blockers.issubset(tolerated_context_blockers)
            )
        )
        and not record.get("missing_env_groups", [])
        and not record.get("missing_sdk_modules", [])
    )


def _stage140_first_provider_blockers(record: dict[str, Any] | None) -> list[str]:
    if not record:
        return ["provider_record_missing"]
    tolerated_context_blockers = {"stage139_provider_already_cutover_authorized"}
    context_blockers = [
        str(blocker)
        for blocker in record.get("stage139_context_blockers", [])
        if str(blocker) not in tolerated_context_blockers
    ]
    return (
        list(record.get("missing_env_groups", []))
        + list(record.get("missing_sdk_modules", []))
        + context_blockers
    )


def _stage143_scoped_safety_ready(stage143: dict[str, Any] | None) -> bool:
    return bool(
        isinstance(stage143, dict)
        and stage143.get("decision") == "FIRST_PROVIDER_HANDOFF_SAFETY_VERIFIED_NO_SUBMISSION"
        and stage143.get("template_placeholders_only") is True
        and stage143.get("template_key_scope_ready") is True
        and stage143.get("rerun_commands_non_live") is True
        and stage143.get("stage139_context_ready") is True
        and stage143.get("boundary_ready") is True
        and int(stage143.get("template_assignment_count") or 0) > 0
        and not stage143.get("unexpected_template_keys", [])
        and not stage143.get("missing_template_keys", [])
    )


def run_stage144_audit(
    *,
    stage106_results_path: Path = DEFAULT_STAGE106_RESULTS,
    stage111_results_path: Path = DEFAULT_STAGE111_RESULTS,
    stage128_results_path: Path = DEFAULT_STAGE128_RESULTS,
    stage129_results_path: Path = DEFAULT_STAGE129_RESULTS,
    stage130_results_path: Path = DEFAULT_STAGE130_RESULTS,
    stage133_results_path: Path = DEFAULT_STAGE133_RESULTS,
    stage138_results_path: Path = DEFAULT_STAGE138_RESULTS,
    stage139_results_path: Path = DEFAULT_STAGE139_RESULTS,
    stage140_results_path: Path = DEFAULT_STAGE140_RESULTS,
    stage141_results_path: Path = DEFAULT_STAGE141_RESULTS,
    stage142_results_path: Path = DEFAULT_STAGE142_RESULTS,
    stage143_results_path: Path = DEFAULT_STAGE143_RESULTS,
) -> dict[str, Any]:
    sources = {
        "stage106": (stage106_results_path, _load_json(stage106_results_path)),
        "stage111": (stage111_results_path, _load_json(stage111_results_path)),
        "stage128": (stage128_results_path, _load_json(stage128_results_path)),
        "stage129": (stage129_results_path, _load_json(stage129_results_path)),
        "stage130": (stage130_results_path, _load_json(stage130_results_path)),
        "stage133": (stage133_results_path, _load_json(stage133_results_path)),
        "stage138": (stage138_results_path, _load_json(stage138_results_path)),
        "stage139": (stage139_results_path, _load_json(stage139_results_path)),
        "stage140": (stage140_results_path, _load_json(stage140_results_path)),
        "stage141": (stage141_results_path, _load_json(stage141_results_path)),
        "stage142": (stage142_results_path, _load_json(stage142_results_path)),
        "stage143": (stage143_results_path, _load_json(stage143_results_path)),
    }
    payloads = {stage: payload for stage, (_, payload) in sources.items()}
    missing_sources = [str(path.as_posix()) for path, payload in sources.values() if payload is None]
    provider = _first_unlock_provider(payloads["stage141"], payloads["stage142"], payloads["stage143"])

    stage140_provider = _provider_record(payloads["stage140"], provider or "")
    stage106_provider = _provider_record(payloads["stage106"], provider or "")
    stage111_provider = _provider_record(payloads["stage111"], provider or "")
    stage128_provider = _provider_record(payloads["stage128"], provider or "")
    stage129_provider = _provider_record(payloads["stage129"], provider or "")
    stage130_provider = _provider_record(payloads["stage130"], provider or "")
    stage139_provider = _provider_record(payloads["stage139"], provider or "")
    stage133_commands = _commands_for_provider(payloads["stage133"], provider or "")
    authorized_stage133 = [record for record in stage133_commands if record.get("command_authorized") is True]
    prepared_job_count = sum(int(record.get("job_count") or 0) for record in stage133_commands)

    transition_records = [
        _transition(
            stage="stage143_first_provider_handoff_safety_audit",
            label="first-provider handoff safety verified",
            ready=_stage143_scoped_safety_ready(payloads["stage143"]),
            observed=payloads["stage143"].get("decision") if isinstance(payloads["stage143"], dict) else None,
            required="FIRST_PROVIDER_HANDOFF_SAFETY_VERIFIED_NO_SUBMISSION with scoped empty template and non-live rerun commands",
            blockers=[
                blocker
                for blocker, blocked in (
                    ("stage143_decision_not_verified", not isinstance(payloads["stage143"], dict) or payloads["stage143"].get("decision") != "FIRST_PROVIDER_HANDOFF_SAFETY_VERIFIED_NO_SUBMISSION"),
                    ("template_assignments_not_placeholders", isinstance(payloads["stage143"], dict) and payloads["stage143"].get("template_placeholders_only") is not True),
                    ("template_key_scope_not_ready", isinstance(payloads["stage143"], dict) and payloads["stage143"].get("template_key_scope_ready") is not True),
                    ("rerun_commands_not_non_live", isinstance(payloads["stage143"], dict) and payloads["stage143"].get("rerun_commands_non_live") is not True),
                    ("stage139_context_not_ready", isinstance(payloads["stage143"], dict) and payloads["stage143"].get("stage139_context_ready") is not True),
                    ("boundary_not_ready", isinstance(payloads["stage143"], dict) and payloads["stage143"].get("boundary_ready") is not True),
                )
                if blocked
            ],
            next_command="python scripts/run_stage143_first_provider_handoff_safety_audit.py",
        ),
        _transition(
            stage="stage140_local_provider_configuration_readiness",
            label="first provider configured for preflight or already cutover",
            ready=_stage140_first_provider_ready(stage140_provider),
            observed=stage140_provider.get("ready_for_preflight_rerun") if stage140_provider else None,
            required="ready_for_preflight_rerun=true or env/sdk ready with cutover already authorized",
            blockers=_stage140_first_provider_blockers(stage140_provider),
            next_command=RERUN_COMMANDS[0],
        ),
        _transition(
            stage="stage106_hardware_execution_preflight",
            label="first provider hardware preflight ready",
            ready=stage106_provider is not None
            and stage106_provider.get("status") == "ready"
            and not stage106_provider.get("blockers"),
            observed=stage106_provider.get("status") if stage106_provider else None,
            required="ready",
            blockers=list(stage106_provider.get("blockers", [])) if stage106_provider else ["provider_record_missing"],
            next_command=RERUN_COMMANDS[1],
        ),
        _transition(
            stage="stage111_provider_sdk_backend_discovery",
            label="first provider SDK/backend discovery ready",
            ready=stage111_provider is not None
            and stage111_provider.get("status") == "ready"
            and not stage111_provider.get("blockers"),
            observed=stage111_provider.get("status") if stage111_provider else None,
            required="ready",
            blockers=list(stage111_provider.get("blockers", [])) if stage111_provider else ["provider_record_missing"],
            next_command=RERUN_COMMANDS[2],
        ),
        _transition(
            stage="stage128_sdk_client_factory_audit",
            label="first provider guarded SDK factory ready",
            ready=_bool(stage128_provider.get("ready")) if stage128_provider else False,
            observed=stage128_provider.get("ready") if stage128_provider else None,
            required=True,
            blockers=list(stage128_provider.get("missing_evidence", [])) if stage128_provider else ["provider_record_missing"],
            next_command=RERUN_COMMANDS[3],
        ),
        _transition(
            stage="stage129_live_cutover_authorization_audit",
            label="first provider live cutover authorized",
            ready=_bool(stage129_provider.get("cutover_authorized")) if stage129_provider else False,
            observed=stage129_provider.get("cutover_authorized") if stage129_provider else None,
            required=True,
            blockers=list(stage129_provider.get("blockers", [])) if stage129_provider else ["provider_record_missing"],
            next_command=RERUN_COMMANDS[4],
        ),
        _transition(
            stage="stage130_live_cutover_remediation_packet",
            label="first provider remediation packet authorizes cutover",
            ready=_bool(stage130_provider.get("cutover_authorized")) if stage130_provider else False,
            observed=stage130_provider.get("cutover_authorized") if stage130_provider else None,
            required=True,
            blockers=list(stage130_provider.get("stage129_blockers", [])) if stage130_provider else ["provider_record_missing"],
            next_command=RERUN_COMMANDS[5],
        ),
        _transition(
            stage="stage139_provider_action_readiness_checklist",
            label="first provider ready for live runner execution",
            ready=_bool(stage139_provider.get("ready_for_live_runner_execution")) if stage139_provider else False,
            observed=stage139_provider.get("ready_for_live_runner_execution") if stage139_provider else None,
            required=True,
            blockers=[stage139_provider.get("first_blocker")] if stage139_provider and stage139_provider.get("first_blocker") else []
            if stage139_provider
            else ["provider_record_missing"],
            next_command=RERUN_COMMANDS[6],
        ),
        _transition(
            stage="stage133_authorized_runner_command_packet",
            label="first provider has authorized runner commands",
            ready=bool(authorized_stage133),
            observed=len(authorized_stage133),
            required="at least 1 authorized command",
            blockers=["no_authorized_runner_commands"] if not authorized_stage133 else [],
            next_command=RERUN_COMMANDS[10],
        ),
        _transition(
            stage="stage138_objective_claim_gate",
            label="objective claim gate remains downstream after hardware results",
            ready=True,
            observed=payloads["stage138"].get("decision") if isinstance(payloads["stage138"], dict) else None,
            required="informational; not required for authorized-runner readiness",
            next_command="",
        ),
    ]
    prerequisite_transitions = transition_records[:-1]
    ready_transition_count = sum(1 for record in prerequisite_transitions if record["ready"])
    first_blocked = next((record for record in prerequisite_transitions if not record["ready"]), None)
    ready_for_authorized_runner = (
        bool(provider)
        and not missing_sources
        and ready_transition_count == len(prerequisite_transitions)
        and bool(authorized_stage133)
    )

    return {
        "schema_version": STAGE144_SCHEMA_VERSION,
        "stage": "stage144_post_configuration_rerun_chain_audit",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": (
            "POST_CONFIGURATION_RERUN_CHAIN_READY_FOR_AUTHORIZED_RUNNER"
            if ready_for_authorized_runner
            else "POST_CONFIGURATION_RERUN_CHAIN_PREPARED_EXECUTION_BLOCKED"
        ),
        "source_artifacts": [str(path.as_posix()) for path, _ in sources.values()],
        "missing_source_artifacts": missing_sources,
        "first_unlock_provider": provider,
        "transition_count": len(prerequisite_transitions),
        "ready_transition_count": ready_transition_count,
        "first_blocked_transition": first_blocked,
        "next_command": first_blocked["next_command"] if first_blocked else "",
        "first_provider_authorized_runner_count": len(authorized_stage133),
        "first_provider_runner_command_count": len(stage133_commands),
        "first_provider_prepared_job_count": prepared_job_count,
        "transition_records": transition_records,
        "rerun_commands": RERUN_COMMANDS,
        "no_hardware_submission": True,
        "provider_credentials_required": True,
        "secret_values_recorded": False,
        "claim_boundary": {
            "supported": [
                "provider-level post-configuration transition audit from Stage 140 through Stage 133",
                "Stage 143 scoped-template and non-live handoff safety enforcement before provider preflight reruns",
                "the first incomplete transition and exact non-live rerun command after local provider configuration changes",
                "preservation of the Stage 138 no-claim boundary until downstream hardware result gates clear",
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
            "Fill first-provider local env outside git, rerun the reported command chain, and execute only Stage 133 "
            "commands that later report command_authorized=true."
        ),
    }


def write_stage144_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
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
        "transition_count": result["transition_count"],
        "ready_transition_count": result["ready_transition_count"],
        "first_blocked_transition": result["first_blocked_transition"],
        "next_command": result["next_command"],
        "first_provider_authorized_runner_count": result["first_provider_authorized_runner_count"],
        "first_provider_runner_command_count": result["first_provider_runner_command_count"],
        "first_provider_prepared_job_count": result["first_provider_prepared_job_count"],
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
            fieldnames=("stage", "label", "ready", "observed", "required", "blockers", "next_command"),
        )
        writer.writeheader()
        for record in result["transition_records"]:
            writer.writerow(
                {
                    "stage": record["stage"],
                    "label": record["label"],
                    "ready": record["ready"],
                    "observed": record["observed"],
                    "required": record["required"],
                    "blockers": "; ".join(str(blocker) for blocker in record["blockers"]),
                    "next_command": record["next_command"],
                }
            )
    return paths


def print_stage144_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"first_unlock_provider: {result['first_unlock_provider']}")
    print(f"ready_transition_count: {result['ready_transition_count']}/{result['transition_count']}")
    blocked = result["first_blocked_transition"]
    print(f"first_blocked_transition: {blocked['stage'] if blocked else ''}")
    print(f"next_command: {result['next_command']}")
