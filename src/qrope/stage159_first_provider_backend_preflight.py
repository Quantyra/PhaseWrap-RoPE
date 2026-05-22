from __future__ import annotations

import csv
import importlib.util
import json
import os
from pathlib import Path
from typing import Any, Callable, Mapping


STAGE159_SCHEMA_VERSION = "qrope_stage159_first_provider_backend_preflight_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE158_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage158_first_provider_pre_execution_sanity" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage159_first_provider_backend_preflight"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)
STAGE158_READY = "FIRST_PROVIDER_PRE_EXECUTION_SANITY_READY_AWAITING_APPROVAL"
FIRST_PROVIDER = "ibm_runtime"


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _module_present(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def _env_value(env: Mapping[str, str], *keys: str) -> str:
    for key in keys:
        value = str(env.get(key, "")).strip()
        if value:
            return value
    return ""


def _call_or_value(value: Any) -> Any:
    return value() if callable(value) else value


def _small_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _public_backend_metadata(backend: Any, backend_name: str) -> dict[str, Any]:
    status = None
    if hasattr(backend, "status"):
        try:
            status = backend.status()
        except Exception:  # noqa: BLE001 - status is optional metadata only.
            status = None
    configuration = None
    if hasattr(backend, "configuration"):
        try:
            configuration = backend.configuration()
        except Exception:  # noqa: BLE001 - configuration is optional metadata only.
            configuration = None
    basis_gates = getattr(configuration, "basis_gates", None) or getattr(backend, "operation_names", None) or []
    coupling_map = getattr(configuration, "coupling_map", None) or getattr(backend, "coupling_map", None) or []
    return {
        "backend": str(_call_or_value(getattr(backend, "name", backend_name)) or backend_name),
        "version": str(_call_or_value(getattr(backend, "version", "")) or ""),
        "num_qubits": _small_int(
            getattr(backend, "num_qubits", None) or getattr(configuration, "num_qubits", None) or getattr(configuration, "n_qubits", None)
        ),
        "simulator": bool(getattr(configuration, "simulator", False) or getattr(backend, "simulator", False)),
        "operational": getattr(status, "operational", None) if status is not None else None,
        "pending_jobs": _small_int(getattr(status, "pending_jobs", None)) if status is not None else None,
        "basis_gate_count": len(list(basis_gates)) if basis_gates else 0,
        "coupling_edge_count": len(list(coupling_map)) if coupling_map else 0,
    }


def _lookup_ibm_backend(env: Mapping[str, str]) -> dict[str, Any]:
    from qiskit_ibm_runtime import QiskitRuntimeService

    token = _env_value(env, "IBM_QUANTUM_TOKEN", "QISKIT_IBM_TOKEN")
    instance = _env_value(env, "IBM_QUANTUM_INSTANCE_CRN")
    backend_name = _env_value(env, "QROPE_IBM_BACKEND", "IBM_QUANTUM_BACKEND", "QROPE_HARDWARE_BACKEND")
    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=token, instance=instance)
    backend = service.backend(backend_name)
    return _public_backend_metadata(backend, backend_name)


def run_stage159_backend_preflight(
    *,
    stage158_results_path: Path = DEFAULT_STAGE158_RESULTS,
    env: Mapping[str, str] | None = None,
    allow_backend_lookup: bool = False,
    backend_lookup: Callable[[Mapping[str, str]], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    environ = os.environ if env is None else env
    stage158 = _load_json(stage158_results_path)
    missing_sources = [] if isinstance(stage158, dict) else [str(stage158_results_path.as_posix())]
    provider = stage158.get("first_unlock_provider") if isinstance(stage158, dict) else None
    token_present = bool(_env_value(environ, "IBM_QUANTUM_TOKEN", "QISKIT_IBM_TOKEN"))
    instance_present = bool(_env_value(environ, "IBM_QUANTUM_INSTANCE_CRN"))
    backend_env_present = bool(_env_value(environ, "QROPE_IBM_BACKEND", "IBM_QUANTUM_BACKEND", "QROPE_HARDWARE_BACKEND"))
    sdk_ready = _module_present("qiskit") and _module_present("qiskit_ibm_runtime")
    lookup_attempted = False
    lookup_ready = False
    backend_metadata: dict[str, Any] = {}
    backend_lookup_error: dict[str, str] | None = None
    blockers = []
    if missing_sources:
        blockers.append("missing_stage158_results")
    if not isinstance(stage158, dict) or stage158.get("decision") != STAGE158_READY:
        blockers.append("stage158_not_ready")
    if provider != FIRST_PROVIDER:
        blockers.append("first_provider_not_ibm_runtime")
    if not token_present:
        blockers.append("ibm_token_missing")
    if not instance_present:
        blockers.append("ibm_instance_crn_missing")
    if not backend_env_present:
        blockers.append("ibm_backend_env_missing")
    if not sdk_ready:
        blockers.append("qiskit_sdk_missing")
    if not allow_backend_lookup:
        blockers.append("backend_lookup_not_requested")
    if not blockers:
        lookup_attempted = True
        try:
            lookup = backend_lookup or _lookup_ibm_backend
            backend_metadata = lookup(environ)
            lookup_ready = bool(backend_metadata.get("backend"))
        except Exception as exc:  # noqa: BLE001 - provider/API failures must fail closed without leaking values.
            backend_lookup_error = {"type": type(exc).__name__}
            blockers.append("backend_lookup_failed")
    if lookup_attempted and not lookup_ready and "backend_lookup_failed" not in blockers:
        blockers.append("backend_lookup_returned_no_backend")
    if missing_sources:
        decision = "FIRST_PROVIDER_BACKEND_PREFLIGHT_INCOMPLETE"
    elif not blockers:
        decision = "FIRST_PROVIDER_BACKEND_PREFLIGHT_READY_AWAITING_APPROVAL"
    else:
        decision = "FIRST_PROVIDER_BACKEND_PREFLIGHT_BLOCKED"
    return {
        "schema_version": STAGE159_SCHEMA_VERSION,
        "stage": "stage159_first_provider_backend_preflight",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": decision,
        "source_artifacts": [str(stage158_results_path.as_posix())],
        "missing_source_artifacts": missing_sources,
        "stage158_decision": stage158.get("decision") if isinstance(stage158, dict) else None,
        "first_unlock_provider": provider,
        "approval_phrase_required": stage158.get("approval_phrase_required") if isinstance(stage158, dict) else None,
        "ibm_token_present": token_present,
        "ibm_instance_crn_present": instance_present,
        "ibm_backend_env_present": backend_env_present,
        "qiskit_sdk_ready": sdk_ready,
        "backend_lookup_allowed": allow_backend_lookup,
        "backend_lookup_attempted": lookup_attempted,
        "backend_lookup_ready": lookup_ready,
        "backend_metadata": backend_metadata,
        "backend_lookup_error": backend_lookup_error,
        "blockers": sorted(set(blockers)),
        "no_hardware_submission": True,
        "explicit_user_approval_required": True,
        "provider_credentials_required": True,
        "secret_values_recorded": False,
        "runnable_commands_recorded": False,
        "claim_boundary": {
            "supported": [
                "read-only IBM Runtime backend resolution after Stage 158 pre-execution sanity",
                "non-secret backend availability, queue, and topology-size metadata when the lookup succeeds",
                "final provider-side readiness evidence before the explicit live-run approval pause",
            ],
            "excluded": [
                "hardware job submission",
                "Sampler or Estimator runtime execution",
                "IBM token or instance CRN values",
                "runnable live-submit command strings",
                "credit balance verification",
                "a noisy-hardware robustness or auditability conclusion",
            ],
        },
        "next_gate": (
            "Pause for the exact approval phrase before any Stage 133 live-submit command. After live execution, "
            "rerun Stage 115, Stage 113, Stage 101, Stage 103, and the claim gates against collected IBM results."
        ),
    }


def write_stage159_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        key: result[key]
        for key in (
            "schema_version",
            "stage",
            "status",
            "objective",
            "decision",
            "source_artifacts",
            "missing_source_artifacts",
            "stage158_decision",
            "first_unlock_provider",
            "approval_phrase_required",
            "ibm_token_present",
            "ibm_instance_crn_present",
            "ibm_backend_env_present",
            "qiskit_sdk_ready",
            "backend_lookup_allowed",
            "backend_lookup_attempted",
            "backend_lookup_ready",
            "blockers",
            "no_hardware_submission",
            "explicit_user_approval_required",
            "secret_values_recorded",
            "runnable_commands_recorded",
            "claim_boundary",
            "next_gate",
        )
    }
    manifest["result_path"] = str((output_dir / "results.json").as_posix())
    manifest["summary_csv_path"] = str((output_dir / "summary.csv").as_posix())
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
                "decision",
                "first_unlock_provider",
                "backend_lookup_attempted",
                "backend_lookup_ready",
                "backend",
                "num_qubits",
                "operational",
                "pending_jobs",
                "blockers",
            ),
        )
        writer.writeheader()
        metadata = result["backend_metadata"]
        writer.writerow(
            {
                "decision": result["decision"],
                "first_unlock_provider": result["first_unlock_provider"],
                "backend_lookup_attempted": result["backend_lookup_attempted"],
                "backend_lookup_ready": result["backend_lookup_ready"],
                "backend": metadata.get("backend", ""),
                "num_qubits": metadata.get("num_qubits", ""),
                "operational": metadata.get("operational", ""),
                "pending_jobs": metadata.get("pending_jobs", ""),
                "blockers": "; ".join(result["blockers"]),
            }
        )
    return paths


def print_stage159_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"backend_lookup_attempted: {result['backend_lookup_attempted']}")
    print(f"backend_lookup_ready: {result['backend_lookup_ready']}")
    print(f"blockers: {', '.join(result['blockers'])}")
    print(f"next_gate: {result['next_gate']}")
