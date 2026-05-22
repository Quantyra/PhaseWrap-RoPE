from __future__ import annotations

import csv
import importlib
import json
from pathlib import Path
from typing import Any


STAGE131_SCHEMA_VERSION = "qrope_stage131_sdk_factory_contract_audit_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE130_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage130_live_cutover_remediation_packet" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage131_sdk_factory_contract_audit"
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


def _contract_record(stage130: dict[str, Any] | None, provider: str) -> dict[str, Any]:
    module = importlib.import_module(PROVIDER_MODULES[provider])
    missing = []
    contract: dict[str, Any] = {}
    builder = getattr(module, "build_live_client_factory_contract", None)
    if not callable(builder):
        missing.append("live_client_factory_contract_not_callable")
    else:
        contract = builder()
    stage130_record = _provider_record(stage130, provider)
    if contract.get("provider") != provider:
        missing.append("contract_provider_mismatch")
    if not contract.get("contract_version"):
        missing.append("contract_version_missing")
    if not str(contract.get("official_doc_url", "")).startswith("https://"):
        missing.append("official_doc_url_missing")
    if not contract.get("required_imports"):
        missing.append("required_imports_missing")
    if not contract.get("factory_steps"):
        missing.append("factory_steps_missing")
    if not contract.get("result_contract"):
        missing.append("result_contract_missing")
    if contract.get("no_hardware_submission") is not True:
        missing.append("no_hardware_submission_marker_missing")
    if contract.get("secret_values_recorded") is not False:
        missing.append("secret_boundary_missing")
    activation_gates = set(contract.get("activation_gates", []))
    required_gates = {
        "stage106_provider_status_ready",
        "stage111_provider_status_ready",
        "stage129_cutover_authorized_true",
    }
    if not required_gates.issubset(activation_gates):
        missing.append("activation_gates_incomplete")
    if stage130_record.get("cutover_authorized") is not False:
        missing.append("stage130_current_blocker_state_changed")
    return {
        "provider": provider,
        "stage130_cutover_authorized": stage130_record.get("cutover_authorized"),
        "contract": contract,
        "missing_evidence": sorted(set(missing)),
        "ready": not missing,
    }


def run_stage131_audit(*, stage130_results_path: Path = DEFAULT_STAGE130_RESULTS) -> dict[str, Any]:
    stage130 = _load_json(stage130_results_path)
    sources = [(stage130_results_path, stage130)]
    missing_sources = [str(path.as_posix()) for path, payload in sources if payload is None]
    records = [_contract_record(stage130, provider) for provider in sorted(PROVIDER_MODULES)]
    ready = all(record["ready"] for record in records) and not missing_sources
    return {
        "schema_version": STAGE131_SCHEMA_VERSION,
        "stage": "stage131_sdk_factory_contract_audit",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": "SDK_FACTORY_CONTRACTS_READY_EXECUTION_BLOCKED" if ready else "SDK_FACTORY_CONTRACTS_INCOMPLETE",
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "stage130_decision": stage130.get("decision") if isinstance(stage130, dict) else None,
        "provider_count": len(records),
        "ready_provider_count": sum(1 for record in records if record["ready"]),
        "provider_records": records,
        "no_hardware_submission": True,
        "provider_credentials_required": True,
        "secret_values_recorded": False,
        "claim_boundary": {
            "supported": [
                "provider-specific SDK factory contracts for eventual guarded live-client implementation",
                "official documentation URLs and activation gates for IBM Runtime and Amazon Braket factories",
                "confirmation that current contracts do not create SDK clients or submit hardware jobs",
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
            "Activate the guarded SDK client wrappers against these contracts only after Stage 106/111 readiness "
            "and Stage 129 cutover authorization clear for the target provider."
        ),
    }


def write_stage131_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "stage130_decision": result["stage130_decision"],
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
                "stage130_cutover_authorized",
                "contract_version",
                "official_doc_url",
                "ready",
                "missing_evidence",
            ),
        )
        writer.writeheader()
        for record in result["provider_records"]:
            contract = record["contract"]
            writer.writerow(
                {
                    "provider": record["provider"],
                    "stage130_cutover_authorized": record["stage130_cutover_authorized"],
                    "contract_version": contract.get("contract_version"),
                    "official_doc_url": contract.get("official_doc_url"),
                    "ready": record["ready"],
                    "missing_evidence": "; ".join(record["missing_evidence"]),
                }
            )
    return paths


def print_stage131_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"ready_provider_count: {result['ready_provider_count']}/{result['provider_count']}")
    print(f"next_gate: {result['next_gate']}")
