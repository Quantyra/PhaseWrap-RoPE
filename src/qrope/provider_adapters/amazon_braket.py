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


PROVIDER = "amazon_braket"
SUBMITTER_IMPORT_PATH = "qrope.provider_adapters.amazon_braket:submit"
REQUIRED_ENV = (
    "AWS_ACCESS_KEY_ID or AWS_PROFILE",
    "QROPE_BRAKET_DEVICE_ARN or QROPE_BRAKET_DEVICE_ARNS",
    "QROPE_BRAKET_OUTPUT_S3_BUCKET",
    "QROPE_BRAKET_AWS_REGION or AWS_REGION",
)


def adapter_status() -> dict[str, Any]:
    return ProviderAdapterStatus(
        provider=PROVIDER,
        submitter_import_path=SUBMITTER_IMPORT_PATH,
        sdk_modules={
            "boto3": module_available("boto3"),
            "braket": module_available("braket"),
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
        "client_kind": "amazon_braket_openqasm3_task_client",
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
        "contract_version": "amazon_braket_openqasm3_factory_contract_v1",
        "official_doc_url": "https://docs.aws.amazon.com/braket/latest/developerguide/braket-openqasm-create-submit-task.html",
        "required_imports": [
            "braket.aws.AwsDevice",
            "braket.ir.openqasm.Program",
        ],
        "required_env": list(REQUIRED_ENV),
        "factory_steps": [
            "Read AWS credential/profile, device ARN, S3 bucket, and region references without recording values.",
            "Create AwsDevice only after Stage 106, Stage 111, and Stage 129 authorize this provider.",
            "Wrap plan OpenQASM 3 source in braket.ir.openqasm.Program.",
            "Run the program with the configured S3 output location and plan shot count.",
            "Preserve the Stage 127 run_openqasm3(plan) adapter boundary around the SDK call.",
        ],
        "result_contract": [
            "Return provider task ARN or ID as job_or_task_id.",
            "Return backend metadata with device ARN, region, and provider identifiers only.",
            "Return raw measurement counts in a shape accepted by normalize_result_counts().",
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
        raise ProviderAdapterBlocked("Amazon Braket live client creation requires allow_live_client=True")
    raise ProviderAdapterBlocked(
        "Amazon Braket live client factory is intentionally blocked; "
        f"blockers={', '.join(config['blockers'])}"
    )


def build_submission_plan(*, jobs: list[dict[str, Any]], payloads: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if len(jobs) != len(payloads):
        raise ProviderAdapterBlocked("job/payload count mismatch before Amazon Braket plan build")
    plans = []
    for job, payload in zip(jobs, payloads, strict=True):
        if job.get("job_id") != payload.get("job_id"):
            raise ProviderAdapterBlocked("job/payload id mismatch before Amazon Braket plan build")
        plans.append(
            {
                "provider": PROVIDER,
                "job_id": job.get("job_id"),
                "window_id": job.get("window_id"),
                "provider_submission_kind": "amazon_braket_openqasm3_task",
                "credential_env": "AWS_ACCESS_KEY_ID or AWS_PROFILE",
                "device_arn_env": "QROPE_BRAKET_DEVICE_ARN or QROPE_BRAKET_DEVICE_ARNS",
                "output_s3_bucket_env": "QROPE_BRAKET_OUTPUT_S3_BUCKET",
                "region_env": "QROPE_BRAKET_AWS_REGION or AWS_REGION",
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
        if "measurementCounts" in raw_result:
            return canonicalize_counts(raw_result["measurementCounts"])
        if "counts" in raw_result:
            return canonicalize_counts(raw_result["counts"])
    raise ProviderAdapterBlocked("unsupported Amazon Braket result shape")


def execute_submission_plans(
    *,
    plans: list[dict[str, Any]],
    client: Any,
    submitted_at_utc: str,
    completed_at_utc: str,
) -> list[dict[str, Any]]:
    records = []
    if not hasattr(client, "run_openqasm3"):
        raise ProviderAdapterBlocked("Amazon Braket client missing run_openqasm3")
    for plan in plans:
        response = client.run_openqasm3(plan)
        if not isinstance(response, dict):
            raise ProviderAdapterBlocked("Amazon Braket client response is not a dict")
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
        raise ProviderAdapterBlocked(f"Amazon Braket adapter received provider={provider!r}")
    if len(jobs) != len(payloads):
        raise ProviderAdapterBlocked("job/payload count mismatch before Amazon Braket submission")
    build_submission_plan(jobs=jobs, payloads=payloads)
    status = adapter_status()
    raise ProviderAdapterBlocked(
        "Amazon Braket live submission adapter is intentionally blocked; "
        f"blockers={', '.join(status['blockers'])}"
    )
