from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


STAGE143_SCHEMA_VERSION = "qrope_stage143_first_provider_handoff_safety_audit_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE142_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage142_first_provider_unlock_handoff" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage143_first_provider_handoff_safety_audit"
FORBIDDEN_COMMAND_FRAGMENTS = ("--allow-live-submit", "--submitter", "provider_runners")
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _template_records(template: str) -> list[dict[str, Any]]:
    records = []
    for line in template.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        records.append({"key": key.strip(), "value_present": bool(value.strip()), "ready": not bool(value.strip())})
    return records


def _candidate_keys(group: str) -> list[str]:
    return [part.strip() for part in group.split(" or ") if part.strip()]


def _expected_template_keys(missing_env_groups: list[str]) -> list[str]:
    keys: list[str] = []
    for group in missing_env_groups:
        keys.extend(_candidate_keys(group))
    return sorted(set(keys))


def _command_records(commands: list[str]) -> list[dict[str, Any]]:
    records = []
    for command in commands:
        forbidden = [fragment for fragment in FORBIDDEN_COMMAND_FRAGMENTS if fragment in command]
        records.append({"command": command, "forbidden_fragments": forbidden, "ready": not forbidden})
    return records


def run_stage143_audit(*, stage142_results_path: Path = DEFAULT_STAGE142_RESULTS) -> dict[str, Any]:
    stage142 = _load_json(stage142_results_path)
    missing_sources = [] if isinstance(stage142, dict) else [str(stage142_results_path.as_posix())]
    template = str(stage142.get("env_template", "")) if isinstance(stage142, dict) else ""
    commands = [str(command) for command in stage142.get("rerun_commands", [])] if isinstance(stage142, dict) else []
    missing_env_groups = [str(group) for group in stage142.get("missing_env_groups", [])] if isinstance(stage142, dict) else []
    stage139_context_blockers = [
        str(blocker) for blocker in stage142.get("stage139_context_blockers", [])
    ] if isinstance(stage142, dict) else []
    template_records = _template_records(template)
    expected_template_keys = _expected_template_keys(missing_env_groups)
    observed_template_keys = sorted(record["key"] for record in template_records)
    unexpected_template_keys = sorted(set(observed_template_keys) - set(expected_template_keys))
    missing_template_keys = sorted(set(expected_template_keys) - set(observed_template_keys))
    command_records = _command_records(commands)
    template_key_scope_ready = not unexpected_template_keys and not missing_template_keys
    template_ready = template_key_scope_ready and all(record["ready"] for record in template_records)
    commands_ready = bool(command_records) and all(record["ready"] for record in command_records)
    boundary_ready = bool(
        isinstance(stage142, dict)
        and stage142.get("no_hardware_submission") is True
        and stage142.get("secret_values_recorded") is False
    )
    stage139_context_ready = not stage139_context_blockers
    ready = template_ready and commands_ready and boundary_ready and stage139_context_ready and not missing_sources
    return {
        "schema_version": STAGE143_SCHEMA_VERSION,
        "stage": "stage143_first_provider_handoff_safety_audit",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": (
            "FIRST_PROVIDER_HANDOFF_SAFETY_VERIFIED_NO_SUBMISSION"
            if ready
            else "FIRST_PROVIDER_HANDOFF_SAFETY_BLOCKED"
        ),
        "source_artifacts": [str(stage142_results_path.as_posix())],
        "missing_source_artifacts": missing_sources,
        "stage142_decision": stage142.get("decision") if isinstance(stage142, dict) else None,
        "first_unlock_provider": stage142.get("first_unlock_provider") if isinstance(stage142, dict) else None,
        "template_assignment_count": len(template_records),
        "nonempty_template_assignment_count": sum(1 for record in template_records if record["value_present"]),
        "expected_template_keys": expected_template_keys,
        "observed_template_keys": observed_template_keys,
        "unexpected_template_keys": unexpected_template_keys,
        "missing_template_keys": missing_template_keys,
        "rerun_command_count": len(command_records),
        "forbidden_command_count": sum(1 for record in command_records if record["forbidden_fragments"]),
        "stage139_context_blockers": stage139_context_blockers,
        "template_records": template_records,
        "command_records": command_records,
        "template_placeholders_only": template_ready,
        "template_key_scope_ready": template_key_scope_ready,
        "rerun_commands_non_live": commands_ready,
        "stage139_context_ready": stage139_context_ready,
        "boundary_ready": boundary_ready,
        "no_hardware_submission": True,
        "provider_credentials_required": True,
        "secret_values_recorded": False,
        "claim_boundary": {
            "supported": [
                "machine-checkable safety audit for the Stage 142 first-provider handoff",
                "verification that env-template assignments remain empty placeholders",
                "verification that env-template keys match the Stage 142 missing environment groups",
                "verification that Stage 142 carries no Stage 139 action-checklist context blockers",
                "verification that rerun commands do not include live-submit fragments",
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
            "Keep the committed handoff as placeholders only. Fill local env outside git, rerun Stage 142/140, and only "
            "run live provider commands after Stage 133 authorizes them."
        ),
    }


def write_stage143_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "stage142_decision": result["stage142_decision"],
        "first_unlock_provider": result["first_unlock_provider"],
        "template_assignment_count": result["template_assignment_count"],
        "nonempty_template_assignment_count": result["nonempty_template_assignment_count"],
        "expected_template_keys": result["expected_template_keys"],
        "observed_template_keys": result["observed_template_keys"],
        "unexpected_template_keys": result["unexpected_template_keys"],
        "missing_template_keys": result["missing_template_keys"],
        "rerun_command_count": result["rerun_command_count"],
        "forbidden_command_count": result["forbidden_command_count"],
        "stage139_context_blockers": result["stage139_context_blockers"],
        "template_placeholders_only": result["template_placeholders_only"],
        "template_key_scope_ready": result["template_key_scope_ready"],
        "rerun_commands_non_live": result["rerun_commands_non_live"],
        "stage139_context_ready": result["stage139_context_ready"],
        "boundary_ready": result["boundary_ready"],
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
        writer = csv.DictWriter(handle, fieldnames=("record_type", "key_or_command", "ready", "problem"))
        writer.writeheader()
        for record in result["template_records"]:
            writer.writerow(
                {
                    "record_type": "template_assignment",
                    "key_or_command": record["key"],
                    "ready": record["ready"],
                    "problem": "nonempty_assignment" if record["value_present"] else "",
                }
            )
        for record in result["command_records"]:
            writer.writerow(
                {
                    "record_type": "rerun_command",
                    "key_or_command": record["command"],
                    "ready": record["ready"],
                    "problem": "; ".join(record["forbidden_fragments"]),
                }
            )
    return paths


def print_stage143_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"first_unlock_provider: {result['first_unlock_provider']}")
    print(f"nonempty_template_assignment_count: {result['nonempty_template_assignment_count']}")
    print(f"forbidden_command_count: {result['forbidden_command_count']}")
    print(f"next_gate: {result['next_gate']}")
