from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


STAGE129_SCHEMA_VERSION = "qrope_stage129_live_cutover_authorization_audit_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE106_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage106_hardware_execution_preflight" / "results.json"
DEFAULT_STAGE111_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage111_provider_sdk_backend_discovery" / "results.json"
DEFAULT_STAGE128_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage128_sdk_client_factory_audit" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage129_live_cutover_authorization_audit"
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


def _providers(stage106: dict[str, Any] | None, stage128: dict[str, Any] | None) -> list[str]:
    found = set()
    if isinstance(stage106, dict):
        found.update(str(provider) for provider in stage106.get("providers", []))
    if isinstance(stage128, dict):
        found.update(str(record.get("provider")) for record in stage128.get("provider_records", []) if record.get("provider"))
    return sorted(found)


def _cutover_record(stage106: dict[str, Any] | None, stage111: dict[str, Any] | None, stage128: dict[str, Any] | None, provider: str) -> dict[str, Any]:
    stage106_record = _provider_record(stage106, provider)
    stage111_record = _provider_record(stage111, provider)
    stage128_record = _provider_record(stage128, provider)
    blockers = []
    if stage106_record.get("status") != "ready":
        blockers.extend(f"stage106:{item}" for item in stage106_record.get("blockers", ["provider_not_ready"]))
    if stage111_record.get("status") != "ready":
        blockers.extend(f"stage111:{item}" for item in stage111_record.get("blockers", ["provider_not_ready"]))
    client_config = stage128_record.get("client_config", {})
    if client_config.get("client_factory_implemented") is not True:
        blockers.append("stage128:client_factory_not_implemented")
    if client_config.get("no_hardware_submission") is not False:
        blockers.append("stage128:no_hardware_submission_guard_active")
    if stage128_record.get("blocked_with_allow") is not False:
        blockers.append("stage128:client_factory_still_blocked_with_allow")
    authorized = not blockers
    return {
        "provider": provider,
        "stage106_status": stage106_record.get("status"),
        "stage111_status": stage111_record.get("status"),
        "stage128_ready": stage128_record.get("ready"),
        "client_factory_implemented": client_config.get("client_factory_implemented"),
        "client_factory_blocked_with_allow": stage128_record.get("blocked_with_allow"),
        "cutover_authorized": authorized,
        "blockers": sorted(set(blockers)),
    }


def run_stage129_audit(
    *,
    stage106_results_path: Path = DEFAULT_STAGE106_RESULTS,
    stage111_results_path: Path = DEFAULT_STAGE111_RESULTS,
    stage128_results_path: Path = DEFAULT_STAGE128_RESULTS,
) -> dict[str, Any]:
    stage106 = _load_json(stage106_results_path)
    stage111 = _load_json(stage111_results_path)
    stage128 = _load_json(stage128_results_path)
    sources = [(stage106_results_path, stage106), (stage111_results_path, stage111), (stage128_results_path, stage128)]
    missing_sources = [str(path.as_posix()) for path, payload in sources if payload is None]
    records = [_cutover_record(stage106, stage111, stage128, provider) for provider in _providers(stage106, stage128)]
    authorized_count = sum(1 for record in records if record["cutover_authorized"])
    any_authorized = authorized_count > 0
    return {
        "schema_version": STAGE129_SCHEMA_VERSION,
        "stage": "stage129_live_cutover_authorization_audit",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": (
            "LIVE_CUTOVER_AUTHORIZED"
            if any_authorized and not missing_sources
            else "LIVE_CUTOVER_BLOCKED_READINESS_REQUIRED"
        ),
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "stage106_decision": stage106.get("decision") if isinstance(stage106, dict) else None,
        "stage111_decision": stage111.get("decision") if isinstance(stage111, dict) else None,
        "stage128_decision": stage128.get("decision") if isinstance(stage128, dict) else None,
        "provider_count": len(records),
        "authorized_provider_count": authorized_count,
        "provider_records": records,
        "no_hardware_submission": True,
        "provider_credentials_required": True,
        "secret_values_recorded": False,
        "claim_boundary": {
            "supported": [
                "explicit live-client cutover authorization decision from Stage 106, Stage 111, and Stage 128 evidence",
                "provider-level blockers that must clear before guarded live provider execution",
                "confirmation that current live cutover remains blocked before hardware submission",
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
            "Clear the listed provider blockers, rerun Stage 106, Stage 111, Stage 128, and this cutover audit, "
            "then run guarded live provider execution only for providers with cutover_authorized=true."
        ),
    }


def write_stage129_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
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
        "stage128_decision": result["stage128_decision"],
        "provider_count": result["provider_count"],
        "authorized_provider_count": result["authorized_provider_count"],
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
                "stage106_status",
                "stage111_status",
                "stage128_ready",
                "client_factory_implemented",
                "client_factory_blocked_with_allow",
                "cutover_authorized",
                "blockers",
            ),
        )
        writer.writeheader()
        for record in result["provider_records"]:
            writer.writerow(
                {
                    "provider": record["provider"],
                    "stage106_status": record["stage106_status"],
                    "stage111_status": record["stage111_status"],
                    "stage128_ready": record["stage128_ready"],
                    "client_factory_implemented": record["client_factory_implemented"],
                    "client_factory_blocked_with_allow": record["client_factory_blocked_with_allow"],
                    "cutover_authorized": record["cutover_authorized"],
                    "blockers": "; ".join(record["blockers"]),
                }
            )
    return paths


def print_stage129_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"authorized_provider_count: {result['authorized_provider_count']}/{result['provider_count']}")
    print(f"next_gate: {result['next_gate']}")
