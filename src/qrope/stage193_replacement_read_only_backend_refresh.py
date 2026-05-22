from __future__ import annotations

import csv
import importlib.util
import json
import os
from pathlib import Path
from typing import Any, Callable, Mapping

from qrope.stage159_first_provider_backend_preflight import _public_backend_metadata
from qrope.stage191_replacement_approval_dossier import DEFAULT_OUTPUT_DIR as STAGE191_OUTPUT_DIR
from qrope.stage192_replacement_provider_credit_preflight import DEFAULT_OUTPUT_DIR as STAGE192_OUTPUT_DIR
from qrope.stage99_matched_fixed_width_encoding_packet_freezer import OBJECTIVE


STAGE193_SCHEMA_VERSION = "qrope_stage193_replacement_read_only_backend_refresh_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE191_RESULTS = STAGE191_OUTPUT_DIR / "results.json"
DEFAULT_STAGE192_RESULTS = STAGE192_OUTPUT_DIR / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage193_replacement_read_only_backend_refresh"
STAGE191_READY = "REPLACEMENT_APPROVAL_DOSSIER_READY_FOR_HUMAN_REVIEW_NOT_LIVE"


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


def _lookup_ibm_backend(env: Mapping[str, str]) -> dict[str, Any]:
    from qiskit_ibm_runtime import QiskitRuntimeService

    token = _env_value(env, "IBM_QUANTUM_TOKEN", "QISKIT_IBM_TOKEN")
    instance = _env_value(env, "IBM_QUANTUM_INSTANCE_CRN")
    backend_name = _env_value(env, "QROPE_IBM_BACKEND", "IBM_QUANTUM_BACKEND", "QROPE_HARDWARE_BACKEND")
    service = QiskitRuntimeService(channel="ibm_quantum_platform", token=token, instance=instance)
    backend = service.backend(backend_name)
    return _public_backend_metadata(backend, backend_name)


def _refresh_item(item_id: str, status: str, description: str, evidence: Any) -> dict[str, Any]:
    return {"item_id": item_id, "status": status, "description": description, "evidence": evidence}


def run_stage193_replacement_read_only_backend_refresh(
    *,
    stage191_results_path: Path = DEFAULT_STAGE191_RESULTS,
    stage192_results_path: Path = DEFAULT_STAGE192_RESULTS,
    env: Mapping[str, str] | None = None,
    allow_read_only_refresh: bool = False,
    backend_lookup: Callable[[Mapping[str, str]], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    environ = os.environ if env is None else env
    stage191 = _load_json(stage191_results_path)
    stage192 = _load_json(stage192_results_path)
    sources = [(stage191_results_path, stage191), (stage192_results_path, stage192)]
    missing_sources = [str(path.as_posix()) for path, payload in sources if not isinstance(payload, dict)]
    token_present = bool(_env_value(environ, "IBM_QUANTUM_TOKEN", "QISKIT_IBM_TOKEN"))
    instance_present = bool(_env_value(environ, "IBM_QUANTUM_INSTANCE_CRN"))
    backend_env_present = bool(_env_value(environ, "QROPE_IBM_BACKEND", "IBM_QUANTUM_BACKEND", "QROPE_HARDWARE_BACKEND"))
    configured = token_present and instance_present and backend_env_present
    sdk_ready = _module_present("qiskit") and _module_present("qiskit_ibm_runtime")
    stage191_ready = bool(isinstance(stage191, dict) and stage191.get("decision") == STAGE191_READY)
    credit_verified = bool(isinstance(stage192, dict) and stage192.get("credit_balance_verified"))
    blockers: list[str] = []
    if missing_sources:
        blockers.append("source_artifacts_missing")
    if not stage191_ready:
        blockers.append("stage191_approval_dossier_not_ready")
    if not configured:
        blockers.append("current_ibm_configuration_missing_or_incomplete")
    if not sdk_ready:
        blockers.append("qiskit_sdk_missing")
    if not allow_read_only_refresh:
        blockers.append("read_only_backend_refresh_not_requested")

    lookup_attempted = False
    lookup_ready = False
    backend_metadata: dict[str, Any] = {}
    backend_lookup_error: dict[str, str] | None = None
    if not missing_sources and stage191_ready and configured and sdk_ready and allow_read_only_refresh:
        lookup_attempted = True
        try:
            lookup = backend_lookup or _lookup_ibm_backend
            backend_metadata = lookup(environ)
            lookup_ready = bool(backend_metadata.get("backend"))
        except Exception as exc:  # noqa: BLE001 - fail closed without leaking provider details.
            backend_lookup_error = {"type": type(exc).__name__}
            blockers.append("backend_lookup_failed")
    if lookup_attempted and not lookup_ready and "backend_lookup_failed" not in blockers:
        blockers.append("backend_lookup_returned_no_backend")

    refresh_items = [
        _refresh_item(
            "replacement_approval_dossier",
            "ready_for_refresh" if stage191_ready else "blocked",
            "Stage191 replacement approval dossier must be ready before a replacement-scoped backend refresh.",
            {"stage191_decision": stage191.get("decision") if isinstance(stage191, dict) else None},
        ),
        _refresh_item(
            "current_local_ibm_configuration",
            "present_non_secret" if configured else "missing_or_incomplete",
            "IBM token, instance, and backend name must be present in the current shell; values are never recorded.",
            {
                "ibm_token_present": token_present,
                "ibm_instance_crn_present": instance_present,
                "ibm_backend_env_present": backend_env_present,
            },
        ),
        _refresh_item(
            "read_only_refresh",
            "verified" if lookup_ready else "not_attempted" if not lookup_attempted else "blocked",
            "Read-only backend metadata refresh; no Sampler, Estimator, or hardware job submission is allowed.",
            {
                "allow_read_only_refresh": allow_read_only_refresh,
                "lookup_attempted": lookup_attempted,
                "backend_lookup_ready": lookup_ready,
                "backend": backend_metadata.get("backend"),
                "operational": backend_metadata.get("operational"),
                "pending_jobs": backend_metadata.get("pending_jobs"),
            },
        ),
        _refresh_item(
            "credit_billing_runtime_allowance",
            "verified" if credit_verified else "human_verification_required",
            "A successful read-only backend refresh still does not verify IBM credit, billing, or Runtime allowance.",
            {"credit_balance_verified": credit_verified},
        ),
    ]
    if missing_sources:
        decision = "REPLACEMENT_READ_ONLY_BACKEND_REFRESH_INCOMPLETE"
    elif lookup_ready:
        decision = "REPLACEMENT_READ_ONLY_BACKEND_REFRESH_READY_CREDIT_AND_APPROVAL_STILL_REQUIRED"
    else:
        decision = "REPLACEMENT_READ_ONLY_BACKEND_REFRESH_BLOCKED"
    return {
        "schema_version": STAGE193_SCHEMA_VERSION,
        "stage": "stage193_replacement_read_only_backend_refresh",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": decision,
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "blockers": sorted(set(blockers)),
        "estimated_total_job_count": stage191.get("estimated_total_job_count") if isinstance(stage191, dict) else None,
        "estimated_total_shots": stage191.get("estimated_total_shots") if isinstance(stage191, dict) else None,
        "ibm_token_present": token_present,
        "ibm_instance_crn_present": instance_present,
        "ibm_backend_env_present": backend_env_present,
        "qiskit_sdk_ready": sdk_ready,
        "allow_read_only_refresh": allow_read_only_refresh,
        "backend_lookup_attempted": lookup_attempted,
        "backend_lookup_ready": lookup_ready,
        "backend_lookup_error": backend_lookup_error,
        "backend_metadata": backend_metadata,
        "credit_balance_verified": credit_verified,
        "refresh_items": refresh_items,
        "no_hardware_submission": True,
        "provider_credentials_required": True,
        "secret_values_recorded": False,
        "runnable_commands_recorded": False,
        "explicit_user_approval_required": True,
        "claim_boundary": {
            "supported": [
                "replacement-scoped read-only IBM backend metadata refresh when explicitly allowed",
                "non-secret provider configuration presence and public backend status metadata",
                "separation of provider reachability from credit/billing and exact approval",
            ],
            "excluded": [
                "hardware job submission",
                "Sampler or Estimator runtime execution",
                "provider credentials, token values, CRN values, or account secrets",
                "IBM credit balance, billing plan, or dollar-cost verification",
                "runnable live-submit command strings",
                "a noisy-hardware robustness or auditability conclusion",
            ],
        },
        "next_gate": (
            "If read-only backend refresh succeeds, resolve IBM credit/billing/Runtime allowance with the user, then require "
            "the exact replacement approval phrase before any live execution runner is prepared."
        ),
    }


def write_stage193_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_keys = (
        "schema_version",
        "stage",
        "status",
        "objective",
        "decision",
        "source_artifacts",
        "missing_source_artifacts",
        "blockers",
        "estimated_total_job_count",
        "estimated_total_shots",
        "ibm_token_present",
        "ibm_instance_crn_present",
        "ibm_backend_env_present",
        "qiskit_sdk_ready",
        "allow_read_only_refresh",
        "backend_lookup_attempted",
        "backend_lookup_ready",
        "credit_balance_verified",
        "no_hardware_submission",
        "provider_credentials_required",
        "secret_values_recorded",
        "runnable_commands_recorded",
        "explicit_user_approval_required",
        "claim_boundary",
        "next_gate",
    )
    manifest = {key: result[key] for key in manifest_keys}
    manifest["result_path"] = str((output_dir / "results.json").as_posix())
    manifest["summary_csv_path"] = str((output_dir / "summary.csv").as_posix())
    paths = {"manifest": str(output_dir / "manifest.json"), "result": str(output_dir / "results.json"), "summary_csv": str(output_dir / "summary.csv")}
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=("item_id", "status", "description"))
        writer.writeheader()
        for item in result["refresh_items"]:
            writer.writerow({field: item.get(field) for field in writer.fieldnames})
    return paths


def print_stage193_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"backend_lookup_attempted: {result['backend_lookup_attempted']}")
    print(f"backend_lookup_ready: {result['backend_lookup_ready']}")
    print(f"credit_balance_verified: {result['credit_balance_verified']}")
    print(f"blockers: {', '.join(result['blockers'])}")
    print(f"next_gate: {result['next_gate']}")
