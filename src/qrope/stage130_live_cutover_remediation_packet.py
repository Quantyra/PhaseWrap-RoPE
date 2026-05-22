from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


STAGE130_SCHEMA_VERSION = "qrope_stage130_live_cutover_remediation_packet_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE106_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage106_hardware_execution_preflight" / "results.json"
DEFAULT_STAGE111_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage111_provider_sdk_backend_discovery" / "results.json"
DEFAULT_STAGE128_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage128_sdk_client_factory_audit" / "results.json"
DEFAULT_STAGE129_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage129_live_cutover_authorization_audit" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage130_live_cutover_remediation_packet"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)


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


def _providers(*payloads: dict[str, Any] | None) -> list[str]:
    found = set()
    for payload in payloads:
        if not isinstance(payload, dict):
            continue
        found.update(str(provider) for provider in payload.get("providers", []) if provider)
        found.update(str(record.get("provider")) for record in payload.get("provider_records", []) if record.get("provider"))
    return sorted(found)


def _remediation_actions(
    *,
    provider: str,
    stage106: dict[str, Any] | None,
    stage111_record: dict[str, Any],
    stage128_record: dict[str, Any],
    stage129_record: dict[str, Any],
) -> list[str]:
    actions: list[str] = []
    required_provider_env = {}
    if isinstance(stage106, dict):
        required_provider_env = stage106.get("required_provider_env", {})
    provider_env = required_provider_env.get(provider, [])
    common_env = stage106.get("required_common_env", []) if isinstance(stage106, dict) else []
    if any(blocker.startswith("stage106:") for blocker in stage129_record.get("blockers", [])):
        actions.append("Set or verify non-committed provider configuration for Stage 106.")
    if provider_env:
        actions.append("Required provider env groups: " + "; ".join(provider_env) + ".")
    if common_env:
        actions.append("Required common env groups: " + "; ".join(common_env) + ".")
    if "provider_sdk_missing" in stage111_record.get("blockers", []):
        modules = stage111_record.get("sdk_modules", {})
        missing = sorted(name for name, present in modules.items() if present is False)
        if missing:
            actions.append("Install or expose missing provider SDK modules: " + ", ".join(missing) + ".")
    client_config = stage128_record.get("client_config", {})
    if client_config.get("client_factory_implemented") is not True:
        actions.append("Replace the fail-closed SDK client factory with a guarded real factory after Stage 106/111 are ready.")
    if stage129_record.get("cutover_authorized") is not True:
        actions.append("Rerun Stage 129 and execute only Stage 133 command records with command_authorized=true for this provider.")
    return actions


def _provider_packet(
    *,
    provider: str,
    stage106: dict[str, Any] | None,
    stage111: dict[str, Any] | None,
    stage128: dict[str, Any] | None,
    stage129: dict[str, Any] | None,
) -> dict[str, Any]:
    stage106_record = _provider_record(stage106, provider)
    stage111_record = _provider_record(stage111, provider)
    stage128_record = _provider_record(stage128, provider)
    stage129_record = _provider_record(stage129, provider)
    return {
        "provider": provider,
        "cutover_authorized": stage129_record.get("cutover_authorized") is True,
        "stage106_status": stage106_record.get("status"),
        "stage111_status": stage111_record.get("status"),
        "stage128_ready": stage128_record.get("ready"),
        "stage129_blockers": stage129_record.get("blockers", []),
        "stage106_blockers": stage106_record.get("blockers", []),
        "stage111_blockers": stage111_record.get("blockers", []),
        "stage128_client_blockers": stage128_record.get("client_config", {}).get("blockers", []),
        "required_provider_env": (
            stage106.get("required_provider_env", {}).get(provider, []) if isinstance(stage106, dict) else []
        ),
        "required_common_env": stage106.get("required_common_env", []) if isinstance(stage106, dict) else [],
        "sdk_modules": stage111_record.get("sdk_modules", stage128_record.get("client_config", {}).get("sdk_modules", {})),
        "remediation_actions": _remediation_actions(
            provider=provider,
            stage106=stage106,
            stage111_record=stage111_record,
            stage128_record=stage128_record,
            stage129_record=stage129_record,
        ),
    }


def run_stage130_packet(
    *,
    stage106_results_path: Path = DEFAULT_STAGE106_RESULTS,
    stage111_results_path: Path = DEFAULT_STAGE111_RESULTS,
    stage128_results_path: Path = DEFAULT_STAGE128_RESULTS,
    stage129_results_path: Path = DEFAULT_STAGE129_RESULTS,
) -> dict[str, Any]:
    stage106 = _load_json(stage106_results_path)
    stage111 = _load_json(stage111_results_path)
    stage128 = _load_json(stage128_results_path)
    stage129 = _load_json(stage129_results_path)
    sources = [
        (stage106_results_path, stage106),
        (stage111_results_path, stage111),
        (stage128_results_path, stage128),
        (stage129_results_path, stage129),
    ]
    missing_sources = [str(path.as_posix()) for path, payload in sources if payload is None]
    provider_records = [
        _provider_packet(provider=provider, stage106=stage106, stage111=stage111, stage128=stage128, stage129=stage129)
        for provider in _providers(stage106, stage111, stage128, stage129)
    ]
    authorized_count = sum(1 for record in provider_records if record["cutover_authorized"])
    return {
        "schema_version": STAGE130_SCHEMA_VERSION,
        "stage": "stage130_live_cutover_remediation_packet",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": (
            "LIVE_CUTOVER_REMEDIATION_PACKET_READY"
            if authorized_count == len(provider_records) and provider_records and not missing_sources
            else "LIVE_CUTOVER_REMEDIATION_PACKET_READY_EXECUTION_BLOCKED"
        ),
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "provider_count": len(provider_records),
        "authorized_provider_count": authorized_count,
        "provider_records": provider_records,
        "no_hardware_submission": True,
        "provider_credentials_required": True,
        "secret_values_recorded": False,
        "rerun_sequence": [
            "python scripts/run_stage106_hardware_execution_preflight.py",
            "python scripts/run_stage111_provider_sdk_backend_discovery.py",
            "python scripts/run_stage128_sdk_client_factory_audit.py",
            "python scripts/run_stage129_live_cutover_authorization_audit.py",
            "python scripts/run_stage130_live_cutover_remediation_packet.py",
            "python scripts/run_stage132_guarded_sdk_factory_implementation_audit.py",
            "python scripts/run_stage116_provider_runner_plan.py",
            "python scripts/run_stage120_live_runner_orchestration_audit.py",
            "python scripts/run_stage133_authorized_runner_command_packet.py",
        ],
        "live_execution_rule": (
            "Do not run provider runner commands until Stage 133 reports command_authorized=true for the target "
            "provider/window after Stage 129 reports cutover_authorized=true."
        ),
        "claim_boundary": {
            "supported": [
                "non-secret provider remediation actions derived from Stage 106/111/128/129 evidence",
                "ordered rerun sequence for live cutover readiness",
                "confirmation that noisy-hardware execution remains blocked until cutover authorization clears",
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
            "Complete the provider remediation actions, rerun the listed stages, and only then proceed to "
            "guarded live provider runner execution for authorized providers."
        ),
    }


def _packet_markdown(result: dict[str, Any]) -> str:
    lines = [
        "# QRoPE Stage 130 - Live Cutover Remediation Packet",
        "",
        "## Decision",
        result["decision"],
        "",
        "## Rerun Sequence",
    ]
    lines.extend(f"- `{command}`" for command in result["rerun_sequence"])
    lines.extend(["", "## Provider Actions"])
    for record in result["provider_records"]:
        lines.append(f"### {record['provider']}")
        lines.append(f"- Cutover authorized: `{record['cutover_authorized']}`")
        if record["stage129_blockers"]:
            lines.append("- Stage 129 blockers: " + "; ".join(record["stage129_blockers"]))
        for action in record["remediation_actions"]:
            lines.append(f"- {action}")
    lines.extend(
        [
            "",
            "## Live Execution Rule",
            result["live_execution_rule"],
            "",
            "## Claim Boundary",
            "- No hardware submission occurred.",
            "- No provider credentials or secret values were recorded.",
            "- No noisy-hardware robustness or PhaseWrap advantage claim is supported by this packet.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_stage130_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "provider_count": result["provider_count"],
        "authorized_provider_count": result["authorized_provider_count"],
        "no_hardware_submission": result["no_hardware_submission"],
        "provider_credentials_required": result["provider_credentials_required"],
        "secret_values_recorded": result["secret_values_recorded"],
        "result_path": str((output_dir / "results.json").as_posix()),
        "summary_csv_path": str((output_dir / "summary.csv").as_posix()),
        "remediation_packet_path": str((output_dir / "remediation_packet.md").as_posix()),
        "live_execution_rule": result["live_execution_rule"],
        "next_gate": result["next_gate"],
        "claim_boundary": result["claim_boundary"],
    }
    paths = {
        "manifest": str(output_dir / "manifest.json"),
        "result": str(output_dir / "results.json"),
        "summary_csv": str(output_dir / "summary.csv"),
        "remediation_packet": str(output_dir / "remediation_packet.md"),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "remediation_packet.md").write_text(_packet_markdown(result), encoding="utf-8")
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=(
                "provider",
                "cutover_authorized",
                "stage106_status",
                "stage111_status",
                "stage128_ready",
                "stage129_blockers",
                "remediation_actions",
            ),
        )
        writer.writeheader()
        for record in result["provider_records"]:
            writer.writerow(
                {
                    "provider": record["provider"],
                    "cutover_authorized": record["cutover_authorized"],
                    "stage106_status": record["stage106_status"],
                    "stage111_status": record["stage111_status"],
                    "stage128_ready": record["stage128_ready"],
                    "stage129_blockers": "; ".join(record["stage129_blockers"]),
                    "remediation_actions": " | ".join(record["remediation_actions"]),
                }
            )
    return paths


def print_stage130_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"authorized_provider_count: {result['authorized_provider_count']}/{result['provider_count']}")
    print(f"next_gate: {result['next_gate']}")
