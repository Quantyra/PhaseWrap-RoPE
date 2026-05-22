from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


STAGE132_SCHEMA_VERSION = "qrope_stage132_guarded_sdk_factory_implementation_audit_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE128_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage128_sdk_client_factory_audit" / "results.json"
DEFAULT_STAGE129_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage129_live_cutover_authorization_audit" / "results.json"
DEFAULT_STAGE131_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage131_sdk_factory_contract_audit" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage132_guarded_sdk_factory_implementation_audit"
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
        found.update(str(record.get("provider")) for record in payload.get("provider_records", []) if record.get("provider"))
    return sorted(found)


def _implementation_record(
    *,
    provider: str,
    stage128: dict[str, Any] | None,
    stage129: dict[str, Any] | None,
    stage131: dict[str, Any] | None,
) -> dict[str, Any]:
    stage128_record = _provider_record(stage128, provider)
    stage129_record = _provider_record(stage129, provider)
    stage131_record = _provider_record(stage131, provider)
    config = stage128_record.get("client_config", {})
    contract = stage131_record.get("contract", {})
    missing = []
    if config.get("client_factory_implemented") is not True:
        missing.append("client_factory_not_implemented")
    if config.get("no_hardware_submission") is not False:
        missing.append("client_factory_not_live_capable")
    if config.get("secret_values_recorded") is not False:
        missing.append("secret_boundary_missing")
    if stage128_record.get("blocked_without_allow") is not True:
        missing.append("factory_not_blocked_without_allow")
    if stage128_record.get("blocked_without_cutover") is not True:
        missing.append("factory_unexpectedly_unblocked_before_cutover")
    if stage129_record.get("cutover_authorized") is not True and not stage129_record.get("blockers", []):
        missing.append("stage129_cutover_state_missing_authorization_or_blockers")
    if "stage128:client_factory_not_implemented" in stage129_record.get("blockers", []):
        missing.append("stage129_still_reports_factory_not_implemented")
    if "stage128:no_hardware_submission_guard_active" in stage129_record.get("blockers", []):
        missing.append("stage129_still_reports_no_submit_guard_active")
    if stage131_record.get("ready") is not True:
        missing.append("stage131_contract_not_ready")
    return {
        "provider": provider,
        "client_factory_implemented": config.get("client_factory_implemented"),
        "client_factory_live_capable": config.get("no_hardware_submission") is False,
        "blocked_without_allow": stage128_record.get("blocked_without_allow"),
        "blocked_without_cutover": stage128_record.get("blocked_without_cutover"),
        "cutover_authorized": stage129_record.get("cutover_authorized"),
        "stage129_blockers": stage129_record.get("blockers", []),
        "contract_version": contract.get("contract_version"),
        "missing_evidence": sorted(set(missing)),
        "ready": not missing,
    }


def run_stage132_audit(
    *,
    stage128_results_path: Path = DEFAULT_STAGE128_RESULTS,
    stage129_results_path: Path = DEFAULT_STAGE129_RESULTS,
    stage131_results_path: Path = DEFAULT_STAGE131_RESULTS,
) -> dict[str, Any]:
    stage128 = _load_json(stage128_results_path)
    stage129 = _load_json(stage129_results_path)
    stage131 = _load_json(stage131_results_path)
    sources = [(stage128_results_path, stage128), (stage129_results_path, stage129), (stage131_results_path, stage131)]
    missing_sources = [str(path.as_posix()) for path, payload in sources if payload is None]
    records = [
        _implementation_record(provider=provider, stage128=stage128, stage129=stage129, stage131=stage131)
        for provider in _providers(stage128, stage129, stage131)
    ]
    ready = bool(records) and all(record["ready"] for record in records) and not missing_sources
    return {
        "schema_version": STAGE132_SCHEMA_VERSION,
        "stage": "stage132_guarded_sdk_factory_implementation_audit",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": "GUARDED_SDK_FACTORIES_IMPLEMENTED_CUTOVER_BLOCKED" if ready else "GUARDED_SDK_FACTORIES_INCOMPLETE",
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "stage128_decision": stage128.get("decision") if isinstance(stage128, dict) else None,
        "stage129_decision": stage129.get("decision") if isinstance(stage129, dict) else None,
        "stage131_decision": stage131.get("decision") if isinstance(stage131, dict) else None,
        "provider_count": len(records),
        "ready_provider_count": sum(1 for record in records if record["ready"]),
        "provider_records": records,
        "no_hardware_submission": True,
        "provider_credentials_required": True,
        "secret_values_recorded": False,
        "claim_boundary": {
            "supported": [
                "guarded SDK factory implementation blockers are removed for IBM Runtime and Amazon Braket",
                "live client creation still fails closed without explicit allow/cutover controls",
                "Stage 129 cutover blockers now point to readiness rather than missing factory code when a provider is not authorized",
                "provider-scoped cutover authorization does not require every provider to be authorized before Stage 133 can evaluate target-provider commands",
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
            "Clear Stage 106/111 provider readiness, rerun Stage 128/129/130/131/132, and execute Stage 116/117/120 "
            "runner commands only for providers with Stage 129 cutover_authorized=true."
        ),
    }


def write_stage132_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "stage128_decision": result["stage128_decision"],
        "stage129_decision": result["stage129_decision"],
        "stage131_decision": result["stage131_decision"],
        "provider_count": result["provider_count"],
        "ready_provider_count": result["ready_provider_count"],
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
                "client_factory_implemented",
                "client_factory_live_capable",
                "blocked_without_cutover",
                "cutover_authorized",
                "ready",
                "missing_evidence",
            ),
        )
        writer.writeheader()
        for record in result["provider_records"]:
            writer.writerow(
                {
                    "provider": record["provider"],
                    "client_factory_implemented": record["client_factory_implemented"],
                    "client_factory_live_capable": record["client_factory_live_capable"],
                    "blocked_without_cutover": record["blocked_without_cutover"],
                    "cutover_authorized": record["cutover_authorized"],
                    "ready": record["ready"],
                    "missing_evidence": "; ".join(record["missing_evidence"]),
                }
            )
    return paths


def print_stage132_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"ready_provider_count: {result['ready_provider_count']}/{result['provider_count']}")
    print(f"next_gate: {result['next_gate']}")
