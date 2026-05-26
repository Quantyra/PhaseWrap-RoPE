from __future__ import annotations

import os
from pathlib import Path
from typing import Collection


ALLOWED_DOTENV_KEYS = frozenset(
    {
        "AWS_ACCESS_KEY_ID",
        "AWS_DEFAULT_REGION",
        "AWS_PROFILE",
        "AWS_REGION",
        "AWS_SECRET_ACCESS_KEY",
        "AWS_SESSION_TOKEN",
        "IBM_QUANTUM_BACKEND",
        "IBM_QUANTUM_CHANNEL",
        "IBM_QUANTUM_INSTANCE_CRN",
        "IBM_QUANTUM_TOKEN",
        "IONQ_API_KEY",
        "IONQ_API_TOKEN",
        "QISKIT_IBM_TOKEN",
        "QROPE_BRAKET_AWS_PROFILE",
        "QROPE_BRAKET_AWS_REGION",
        "QROPE_BRAKET_COST_PER_SHOT_USD",
        "QROPE_BRAKET_DEVICE_ARN",
        "QROPE_BRAKET_DEVICE_ARNS",
        "QROPE_BRAKET_JOB_TIMEOUT_SEC",
        "QROPE_BRAKET_OUTPUT_S3_BUCKET",
        "QROPE_BRAKET_OUTPUT_S3_PREFIX",
        "QROPE_BRAKET_POLL_INTERVAL_SEC",
        "QROPE_QUANDELA_ALLOW_SIMULATOR_STAGE4",
        "QROPE_QUANDELA_BACKEND",
        "QROPE_QUANDELA_JOB_TIMEOUT_SEC",
        "QROPE_QUANDELA_POLL_INTERVAL_SEC",
        "QUANDELA_CLOUD_TOKEN",
        "QUANDELA_CLOUD_URL",
        "QUANDELA_PLATFORM",
        "QUANDELA_TOKEN",
        "SCALEWAY_PROJECT_ID",
        "SCALEWAY_QAAS_PLATFORM",
        "SCALEWAY_SECRET_KEY",
        "XANADU_CLOUD_KEY",
    }
)


def _parse_dotenv_value(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def load_local_dotenv(path: Path, *, allowed_keys: Collection[str] = ALLOWED_DOTENV_KEYS) -> None:
    """Load allowlisted provider credentials from a local dotenv file."""
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        key, value = line.split("=", 1)
        key = key.strip()
        value = _parse_dotenv_value(value)
        if key not in allowed_keys:
            continue
        if key and key not in os.environ:
            os.environ[key] = value
