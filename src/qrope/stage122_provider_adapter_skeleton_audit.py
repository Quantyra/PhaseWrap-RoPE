from __future__ import annotations

import csv
import importlib
import json
from pathlib import Path
from typing import Any


STAGE122_SCHEMA_VERSION = "qrope_stage122_provider_adapter_skeleton_audit_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE121_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage121_provider_adapter_bridge_audit" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage122_provider_adapter_skeleton_audit"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)
ADAPTER_IMPORTS = {
    "amazon_braket": "qrope.provider_adapters.amazon_braket:submit",
    "ibm_runtime": "qrope.provider_adapters.ibm_runtime:submit",
}


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _adapter_record(provider: str, import_path: str) -> dict[str, Any]:
    module_name, _, attr_name = import_path.partition(":")
    missing = []
    status: dict[str, Any] = {}
    module_imported = False
    submitter_callable = False
    status_callable = False
    try:
        module = importlib.import_module(module_name)
        module_imported = True
        submitter_callable = callable(getattr(module, attr_name, None))
        status_callable = callable(getattr(module, "adapter_status", None))
        if status_callable:
            status = module.adapter_status()
    except Exception as exc:  # noqa: BLE001 - audit reports import failures as blockers.
        missing.append(f"adapter_import_failed:{exc}")
    if not module_imported:
        missing.append("adapter_module_missing")
    if not submitter_callable:
        missing.append("submitter_not_callable")
    if not status_callable:
        missing.append("adapter_status_not_callable")
    if status and status.get("provider") != provider:
        missing.append("adapter_provider_mismatch")
    if status and status.get("secret_values_recorded") is True:
        missing.append("adapter_secret_boundary_missing")
    return {
        "provider": provider,
        "submitter_import_path": import_path,
        "adapter_module_imported": module_imported,
        "submitter_callable": submitter_callable,
        "adapter_status_callable": status_callable,
        "adapter_status": status,
        "missing_evidence": sorted(set(missing)),
        "ready": not missing and module_imported and submitter_callable and status_callable,
    }


def run_stage122_audit(*, stage121_results_path: Path = DEFAULT_STAGE121_RESULTS) -> dict[str, Any]:
    stage121 = _load_json(stage121_results_path)
    missing_sources = [] if isinstance(stage121, dict) else [str(stage121_results_path.as_posix())]
    adapter_records = [_adapter_record(provider, import_path) for provider, import_path in sorted(ADAPTER_IMPORTS.items())]
    ready = all(record["ready"] for record in adapter_records) and not missing_sources
    return {
        "schema_version": STAGE122_SCHEMA_VERSION,
        "stage": "stage122_provider_adapter_skeleton_audit",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": (
            "PROVIDER_ADAPTER_SKELETONS_READY_EXECUTION_BLOCKED"
            if ready
            else "PROVIDER_ADAPTER_SKELETONS_INCOMPLETE"
        ),
        "source_artifacts": [str(stage121_results_path.as_posix())],
        "missing_source_artifacts": missing_sources,
        "stage121_decision": stage121.get("decision") if isinstance(stage121, dict) else None,
        "adapter_count": len(adapter_records),
        "ready_adapter_count": sum(1 for record in adapter_records if record["ready"]),
        "adapter_records": adapter_records,
        "no_hardware_submission": True,
        "provider_credentials_required": True,
        "secret_values_recorded": False,
        "claim_boundary": {
            "supported": [
                "canonical IBM Runtime and Amazon Braket adapter import paths exist",
                "adapter modules expose callable submitters and non-secret readiness metadata",
                "adapter submitters fail closed under current provider readiness blockers",
            ],
            "excluded": [
                "hardware job submission",
                "provider credentials or secret values",
                "authorized live provider SDK submission",
                "real provider result records",
                "Stage 113 evidence assembly",
                "a noisy-hardware robustness result",
            ],
        },
        "next_gate": (
            "Run provider SDK implementations only after Stage 106/111 readiness clears and Stage 129 authorizes cutover."
        ),
    }


def write_stage122_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "stage121_decision": result["stage121_decision"],
        "adapter_count": result["adapter_count"],
        "ready_adapter_count": result["ready_adapter_count"],
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
            fieldnames=("provider", "submitter_import_path", "adapter_module_imported", "submitter_callable", "adapter_status_callable", "ready", "missing_evidence"),
        )
        writer.writeheader()
        for record in result["adapter_records"]:
            writer.writerow(
                {
                    "provider": record["provider"],
                    "submitter_import_path": record["submitter_import_path"],
                    "adapter_module_imported": record["adapter_module_imported"],
                    "submitter_callable": record["submitter_callable"],
                    "adapter_status_callable": record["adapter_status_callable"],
                    "ready": record["ready"],
                    "missing_evidence": "; ".join(record["missing_evidence"]),
                }
            )
    return paths


def print_stage122_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"ready_adapter_count: {result['ready_adapter_count']}/{result['adapter_count']}")
    print(f"next_gate: {result['next_gate']}")
