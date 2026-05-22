from __future__ import annotations

from typing import Any

from qrope.provider_adapters.common import ProviderAdapterBlocked, ProviderAdapterStatus, env_present, module_available


PROVIDER = "ibm_runtime"
SUBMITTER_IMPORT_PATH = "qrope.provider_adapters.ibm_runtime:submit"
REQUIRED_ENV = ("IBM_QUANTUM_TOKEN", "IBM_QUANTUM_INSTANCE_CRN", "QROPE_IBM_BACKEND")


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
                "backend_env": "QROPE_IBM_BACKEND",
                "instance_env": "IBM_QUANTUM_INSTANCE_CRN",
                "credential_env": "IBM_QUANTUM_TOKEN",
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
