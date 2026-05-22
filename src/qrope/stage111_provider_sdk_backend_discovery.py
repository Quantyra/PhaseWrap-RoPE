from __future__ import annotations

import csv
import importlib.util
import json
import os
from pathlib import Path
from typing import Any, Mapping


STAGE111_SCHEMA_VERSION = "qrope_stage111_provider_sdk_backend_discovery_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE106_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage106_hardware_execution_preflight" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage111_provider_sdk_backend_discovery"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)
SDK_MODULES_BY_PROVIDER: dict[str, tuple[str, ...]] = {
    "ibm_runtime": ("qiskit", "qiskit_ibm_runtime"),
    "amazon_braket": ("braket", "boto3"),
}


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _module_present(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def _env_value(env: Mapping[str, str], *keys: str) -> str | None:
    for key in keys:
        value = str(env.get(key, "")).strip()
        if value:
            return value
    return None


def _safe_error(exc: Exception) -> dict[str, str]:
    return {"type": type(exc).__name__, "message": str(exc)[:240]}


def _ibm_live_discovery(env: Mapping[str, str]) -> dict[str, Any]:
    token = _env_value(env, "IBM_QUANTUM_TOKEN", "QISKIT_IBM_TOKEN")
    backend_name = _env_value(env, "QROPE_IBM_BACKEND", "QROPE_HARDWARE_BACKEND")
    instance = _env_value(env, "IBM_QUANTUM_INSTANCE_CRN")
    if not token or not backend_name:
        return {"attempted": False, "status": "blocked", "blockers": ["ibm_token_or_backend_missing"]}
    try:
        from qiskit_ibm_runtime import QiskitRuntimeService

        kwargs: dict[str, Any] = {"channel": "ibm_quantum_platform", "token": token}
        if instance:
            kwargs["instance"] = instance
        service = QiskitRuntimeService(**kwargs)
        backend = service.backend(backend_name)
        status = backend.status()
        return {
            "attempted": True,
            "status": "available",
            "backend_name": getattr(backend, "name", backend_name),
            "operational": bool(getattr(status, "operational", False)),
            "pending_jobs": getattr(status, "pending_jobs", None),
            "instance_supplied": bool(instance),
            "secret_values_recorded": False,
        }
    except Exception as exc:  # pragma: no cover - exercised only with live provider access
        return {
            "attempted": True,
            "status": "unavailable",
            "backend_name": backend_name,
            "instance_supplied": bool(instance),
            "error": _safe_error(exc),
            "secret_values_recorded": False,
        }


def _provider_record(
    provider_record: dict[str, Any],
    env: Mapping[str, str],
    *,
    allow_live_discovery: bool,
) -> dict[str, Any]:
    provider = str(provider_record.get("provider"))
    module_status = {module: _module_present(module) for module in SDK_MODULES_BY_PROVIDER.get(provider, ())}
    sdk_ready = bool(module_status) and all(module_status.values())
    blockers = []
    if not sdk_ready:
        blockers.append("provider_sdk_missing")
    if provider_record.get("status") != "ready":
        blockers.append("stage106_provider_preflight_not_ready")
    discovery: dict[str, Any] = {"attempted": False, "status": "disabled"}
    if allow_live_discovery and sdk_ready:
        if provider == "ibm_runtime":
            discovery = _ibm_live_discovery(env)
        elif provider == "amazon_braket":
            discovery = {
                "attempted": False,
                "status": "not_implemented",
                "reason": "Stage111 currently checks Braket SDK presence but does not submit or discover devices.",
            }
    if discovery.get("status") in {"blocked", "unavailable"}:
        blockers.append("backend_discovery_failed")
    return {
        "provider": provider,
        "stage106_status": provider_record.get("status"),
        "stage106_blockers": provider_record.get("blockers", []),
        "sdk_modules": module_status,
        "sdk_ready": sdk_ready,
        "live_discovery_allowed": allow_live_discovery,
        "backend_discovery": discovery,
        "status": "ready" if not blockers else "blocked",
        "blockers": blockers,
    }


def run_stage111_discovery(
    *,
    stage106_results_path: Path = DEFAULT_STAGE106_RESULTS,
    env: Mapping[str, str] | None = None,
    allow_live_discovery: bool = False,
) -> dict[str, Any]:
    environ = os.environ if env is None else env
    stage106 = _load_json(stage106_results_path)
    missing_sources = [] if stage106 else [str(stage106_results_path.as_posix())]
    provider_records = [
        _provider_record(record, environ, allow_live_discovery=allow_live_discovery)
        for record in stage106.get("provider_records", [])
    ] if stage106 else []
    all_ready = bool(provider_records) and all(record["status"] == "ready" for record in provider_records)
    return {
        "schema_version": STAGE111_SCHEMA_VERSION,
        "stage": "stage111_provider_sdk_backend_discovery",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": (
            "PROVIDER_SDK_BACKEND_DISCOVERY_READY_NO_SUBMISSION"
            if all_ready
            else "PROVIDER_SDK_BACKEND_DISCOVERY_BLOCKED"
        ),
        "source_artifacts": [str(stage106_results_path.as_posix())],
        "missing_source_artifacts": missing_sources,
        "stage106_decision": stage106.get("decision") if stage106 else None,
        "stage106_ready_for_hardware_submission": bool(stage106 and stage106.get("ready_for_hardware_submission") is True),
        "allow_live_discovery": allow_live_discovery,
        "provider_count": len(provider_records),
        "ready_provider_count": sum(1 for record in provider_records if record["status"] == "ready"),
        "provider_records": provider_records,
        "no_hardware_submission": True,
        "provider_credentials_required": allow_live_discovery,
        "secret_values_recorded": False,
        "claim_boundary": {
            "supported": [
                "a no-submission provider SDK readiness and optional backend discovery check",
                "explicit separation between installed SDK capability, Stage 106 policy readiness, and live provider availability",
                "non-secret reporting of provider/backend discovery status before hardware execution",
            ],
            "excluded": [
                "hardware job submission",
                "completed calibration counts",
                "completed matched packet counts",
                "a noisy-hardware robustness result",
            ],
        },
        "next_gate": (
            "Install missing provider SDK extras, clear Stage 106 configuration blockers, and optionally rerun this gate "
            "with --allow-live-discovery before executing Stage 107 windows."
        ),
    }


def write_stage111_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
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
        "stage106_ready_for_hardware_submission": result["stage106_ready_for_hardware_submission"],
        "allow_live_discovery": result["allow_live_discovery"],
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
            fieldnames=("provider", "stage106_status", "sdk_ready", "live_discovery_allowed", "backend_discovery_status", "status", "blockers"),
        )
        writer.writeheader()
        for record in result["provider_records"]:
            writer.writerow(
                {
                    "provider": record["provider"],
                    "stage106_status": record["stage106_status"],
                    "sdk_ready": record["sdk_ready"],
                    "live_discovery_allowed": record["live_discovery_allowed"],
                    "backend_discovery_status": record["backend_discovery"].get("status"),
                    "status": record["status"],
                    "blockers": "; ".join(record["blockers"]),
                }
            )
    return paths


def print_stage111_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"stage106_ready_for_hardware_submission: {result['stage106_ready_for_hardware_submission']}")
    print(f"allow_live_discovery: {result['allow_live_discovery']}")
    print(f"ready_provider_count: {result['ready_provider_count']}/{result['provider_count']}")
    print(f"next_gate: {result['next_gate']}")
