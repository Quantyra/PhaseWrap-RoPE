from __future__ import annotations

from typing import Any

from qrope.provider_adapters.common import (
    ProviderAdapterBlocked,
    ProviderAdapterStatus,
    build_stage114_result_record,
    canonicalize_counts,
    env_present,
    module_available,
)


PROVIDER = "ibm_runtime"
SUBMITTER_IMPORT_PATH = "qrope.provider_adapters.ibm_runtime:submit"
REQUIRED_ENV = ("IBM_QUANTUM_TOKEN or QISKIT_IBM_TOKEN", "IBM_QUANTUM_INSTANCE_CRN", "QROPE_IBM_BACKEND or QROPE_HARDWARE_BACKEND")


def adapter_status() -> dict[str, Any]:
    return ProviderAdapterStatus(
        provider=PROVIDER,
        submitter_import_path=SUBMITTER_IMPORT_PATH,
        sdk_modules={
            "qiskit": module_available("qiskit"),
            "qiskit_ibm_runtime": module_available("qiskit_ibm_runtime"),
        },
        required_env=REQUIRED_ENV,
        required_env_present=env_present(REQUIRED_ENV),
        live_submission_implemented=False,
        no_hardware_submission=True,
    ).as_dict()


def build_client_config() -> dict[str, Any]:
    status = adapter_status()
    return {
        "provider": PROVIDER,
        "client_kind": "ibm_runtime_sampler_client",
        "submitter_import_path": SUBMITTER_IMPORT_PATH,
        "required_env": list(REQUIRED_ENV),
        "sdk_modules": status["sdk_modules"],
        "required_env_present": status["required_env_present"],
        "client_factory_implemented": False,
        "no_hardware_submission": True,
        "secret_values_recorded": False,
        "blockers": status["blockers"] + ["sdk_client_factory_not_enabled"],
    }


def build_live_client_factory_contract() -> dict[str, Any]:
    return {
        "provider": PROVIDER,
        "contract_version": "ibm_runtime_sampler_v2_factory_contract_v1",
        "official_doc_url": "https://quantum.cloud.ibm.com/docs/en/api/qiskit-ibm-runtime/runtime-service",
        "required_imports": [
            "qiskit_ibm_runtime.QiskitRuntimeService",
            "qiskit_ibm_runtime.SamplerV2",
            "qiskit.transpiler.preset_passmanagers.generate_preset_pass_manager",
        ],
        "required_env": list(REQUIRED_ENV),
        "factory_steps": [
            "Read IBM token, instance CRN, and backend name from environment references without recording values.",
            "Create QiskitRuntimeService only after Stage 106, Stage 111, and Stage 129 authorize this provider.",
            "Resolve the configured backend through QiskitRuntimeService.backend().",
            "Transpile the OpenQASM-derived circuit for the backend target before sampler execution.",
            "Create a SamplerV2-compatible runtime client and preserve the Stage 127 run_openqasm3(plan) adapter boundary.",
        ],
        "result_contract": [
            "Return provider job ID as job_or_task_id.",
            "Return backend metadata with backend name and provider identifiers only.",
            "Return raw counts in a shape accepted by normalize_result_counts().",
            "Return submitted_at_utc and completed_at_utc timestamps for Stage 114 record construction.",
        ],
        "activation_gates": [
            "stage106_provider_status_ready",
            "stage111_provider_status_ready",
            "stage129_cutover_authorized_true",
        ],
        "no_hardware_submission": True,
        "secret_values_recorded": False,
    }


def create_live_client(*, allow_live_client: bool = False) -> Any:
    config = build_client_config()
    if not allow_live_client:
        raise ProviderAdapterBlocked("IBM Runtime live client creation requires allow_live_client=True")
    raise ProviderAdapterBlocked(
        "IBM Runtime live client factory is intentionally blocked; "
        f"blockers={', '.join(config['blockers'])}"
    )


def build_submission_plan(*, jobs: list[dict[str, Any]], payloads: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if len(jobs) != len(payloads):
        raise ProviderAdapterBlocked("job/payload count mismatch before IBM Runtime plan build")
    plans = []
    for job, payload in zip(jobs, payloads, strict=True):
        if job.get("job_id") != payload.get("job_id"):
            raise ProviderAdapterBlocked("job/payload id mismatch before IBM Runtime plan build")
        plans.append(
            {
                "provider": PROVIDER,
                "job_id": job.get("job_id"),
                "window_id": job.get("window_id"),
                "provider_submission_kind": "ibm_runtime_openqasm3_sampler",
                "backend_env": "QROPE_IBM_BACKEND or QROPE_HARDWARE_BACKEND",
                "instance_env": "IBM_QUANTUM_INSTANCE_CRN",
                "credential_env": "IBM_QUANTUM_TOKEN or QISKIT_IBM_TOKEN",
                "shots": payload.get("shots", job.get("shots")),
                "openqasm3_sha256": payload.get("openqasm3_sha256"),
                "openqasm3": payload.get("openqasm3"),
                "target_counts_key": payload.get("target_counts_key"),
                "expected_result_fields": [
                    "job_id",
                    "job_or_task_id",
                    "backend_metadata",
                    "submitted_at_utc",
                    "completed_at_utc",
                    "counts",
                ],
                "no_hardware_submission": True,
            }
        )
    return plans


def normalize_result_counts(raw_result: Any) -> dict[str, int]:
    if isinstance(raw_result, dict):
        if "counts" in raw_result:
            return canonicalize_counts(raw_result["counts"])
        if "quasi_dists" in raw_result:
            quasi_dists = raw_result["quasi_dists"]
            if not quasi_dists:
                raise ProviderAdapterBlocked("IBM Runtime quasi_dists empty")
            shots = int(raw_result.get("shots", 0))
            if shots <= 0:
                raise ProviderAdapterBlocked("IBM Runtime quasi_dists require positive shots")
            first = quasi_dists[0]
            return canonicalize_counts({key: round(float(value) * shots) for key, value in first.items()})
    raise ProviderAdapterBlocked("unsupported IBM Runtime result shape")


def execute_submission_plans(
    *,
    plans: list[dict[str, Any]],
    client: Any,
    submitted_at_utc: str,
    completed_at_utc: str,
) -> list[dict[str, Any]]:
    records = []
    if not hasattr(client, "run_openqasm3"):
        raise ProviderAdapterBlocked("IBM Runtime client missing run_openqasm3")
    for plan in plans:
        response = client.run_openqasm3(plan)
        if not isinstance(response, dict):
            raise ProviderAdapterBlocked("IBM Runtime client response is not a dict")
        counts = normalize_result_counts(response.get("raw_result", response))
        records.append(
            build_stage114_result_record(
                plan=plan,
                job_or_task_id=str(response.get("job_or_task_id", "")),
                backend_metadata=response.get("backend_metadata", {}),
                submitted_at_utc=str(response.get("submitted_at_utc", submitted_at_utc)),
                completed_at_utc=str(response.get("completed_at_utc", completed_at_utc)),
                counts=counts,
            )
        )
    return records


def submit(*, provider: str, jobs: list[dict[str, Any]], payloads: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if provider != PROVIDER:
        raise ProviderAdapterBlocked(f"IBM Runtime adapter received provider={provider!r}")
    if len(jobs) != len(payloads):
        raise ProviderAdapterBlocked("job/payload count mismatch before IBM Runtime submission")
    build_submission_plan(jobs=jobs, payloads=payloads)
    status = adapter_status()
    raise ProviderAdapterBlocked(
        "IBM Runtime live submission adapter is intentionally blocked; "
        f"blockers={', '.join(status['blockers'])}"
    )
