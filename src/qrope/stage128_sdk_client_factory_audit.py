from __future__ import annotations

import csv
import importlib
import json
from pathlib import Path
from typing import Any

from qrope.provider_adapters.common import ProviderAdapterBlocked


STAGE128_SCHEMA_VERSION = "qrope_stage128_sdk_client_factory_audit_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE106_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage106_hardware_execution_preflight" / "results.json"
DEFAULT_STAGE111_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage111_provider_sdk_backend_discovery" / "results.json"
DEFAULT_STAGE127_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage127_injected_client_submitter_audit" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage128_sdk_client_factory_audit"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)
PROVIDER_MODULES = {
    "amazon_braket": "qrope.provider_adapters.amazon_braket",
    "ibm_runtime": "qrope.provider_adapters.ibm_runtime",
}


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


def _factory_record(stage106: dict[str, Any] | None, stage111: dict[str, Any] | None, provider: str) -> dict[str, Any]:
    module = importlib.import_module(PROVIDER_MODULES[provider])
    missing = []
    config: dict[str, Any] = {}
    blocked_without_allow = False
    blocked_with_allow = False
    if not callable(getattr(module, "build_client_config", None)):
        missing.append("build_client_config_not_callable")
    else:
        config = module.build_client_config()
    if not callable(getattr(module, "create_live_client", None)):
        missing.append("create_live_client_not_callable")
    else:
        try:
            module.create_live_client()
        except ProviderAdapterBlocked:
            blocked_without_allow = True
        try:
            module.create_live_client(allow_live_client=True)
        except ProviderAdapterBlocked:
            blocked_with_allow = True
    if config.get("provider") != provider:
        missing.append("client_config_provider_mismatch")
    if config.get("secret_values_recorded") is not False:
        missing.append("client_config_secret_boundary_missing")
    if config.get("no_hardware_submission") is not True:
        missing.append("client_config_no_submit_marker_missing")
    if not blocked_without_allow:
        missing.append("client_factory_not_blocked_without_allow")
    if not blocked_with_allow:
        missing.append("client_factory_not_blocked_with_current_readiness")
    stage106_record = _provider_record(stage106, provider)
    stage111_record = _provider_record(stage111, provider)
    if stage106_record.get("status") != "blocked" or stage111_record.get("status") != "blocked":
        missing.append("current_provider_blocker_state_changed")
    return {
        "provider": provider,
        "stage106_status": stage106_record.get("status"),
        "stage111_status": stage111_record.get("status"),
        "client_config": config,
        "blocked_without_allow": blocked_without_allow,
        "blocked_with_allow": blocked_with_allow,
        "missing_evidence": sorted(set(missing)),
        "ready": not missing,
    }


def run_stage128_audit(
    *,
    stage106_results_path: Path = DEFAULT_STAGE106_RESULTS,
    stage111_results_path: Path = DEFAULT_STAGE111_RESULTS,
    stage127_results_path: Path = DEFAULT_STAGE127_RESULTS,
) -> dict[str, Any]:
    stage106 = _load_json(stage106_results_path)
    stage111 = _load_json(stage111_results_path)
    stage127 = _load_json(stage127_results_path)
    sources = [(stage106_results_path, stage106), (stage111_results_path, stage111), (stage127_results_path, stage127)]
    missing_sources = [str(path.as_posix()) for path, payload in sources if payload is None]
    records = [_factory_record(stage106, stage111, provider) for provider in sorted(PROVIDER_MODULES)]
    ready = all(record["ready"] for record in records) and not missing_sources
    return {
        "schema_version": STAGE128_SCHEMA_VERSION,
        "stage": "stage128_sdk_client_factory_audit",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": (
            "SDK_CLIENT_FACTORIES_GUARDED_EXECUTION_BLOCKED"
            if ready
            else "SDK_CLIENT_FACTORIES_INCOMPLETE"
        ),
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "stage106_decision": stage106.get("decision") if isinstance(stage106, dict) else None,
        "stage111_decision": stage111.get("decision") if isinstance(stage111, dict) else None,
        "stage127_decision": stage127.get("decision") if isinstance(stage127, dict) else None,
        "provider_count": len(records),
        "ready_provider_count": sum(1 for record in records if record["ready"]),
        "provider_records": records,
        "no_hardware_submission": True,
        "provider_credentials_required": True,
        "secret_values_recorded": False,
        "claim_boundary": {
            "supported": [
                "provider adapters expose guarded SDK client factory boundaries",
                "client configs report non-secret readiness metadata and SDK/env blockers",
                "live client creation fails closed while Stage 106/111 provider readiness is blocked",
            ],
            "excluded": [
                "hardware job submission",
                "provider credentials or secret values",
                "live provider SDK client creation",
                "real provider result records",
                "Stage 113 evidence assembly",
                "a noisy-hardware robustness result",
            ],
        },
        "next_gate": (
            "After Stage 106/111 readiness clears, replace the blocked client factories with real SDK client creation "
            "while preserving the Stage 127 injected-client execution contract."
        ),
    }


def write_stage128_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "stage106_decision": result["stage106_decision"],
        "stage111_decision": result["stage111_decision"],
        "stage127_decision": result["stage127_decision"],
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
            fieldnames=("provider", "stage106_status", "stage111_status", "blocked_without_allow", "blocked_with_allow", "ready", "missing_evidence"),
        )
        writer.writeheader()
        for record in result["provider_records"]:
            writer.writerow(
                {
                    "provider": record["provider"],
                    "stage106_status": record["stage106_status"],
                    "stage111_status": record["stage111_status"],
                    "blocked_without_allow": record["blocked_without_allow"],
                    "blocked_with_allow": record["blocked_with_allow"],
                    "ready": record["ready"],
                    "missing_evidence": "; ".join(record["missing_evidence"]),
                }
            )
    return paths


def print_stage128_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"ready_provider_count: {result['ready_provider_count']}/{result['provider_count']}")
    print(f"next_gate: {result['next_gate']}")
