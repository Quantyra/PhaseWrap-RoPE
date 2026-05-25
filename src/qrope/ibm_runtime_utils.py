from __future__ import annotations

import os
from typing import Any


def ibm_runtime_service_kwargs() -> dict[str, Any]:
    token = os.environ.get("IBM_QUANTUM_TOKEN") or os.environ.get("QISKIT_IBM_TOKEN")
    instance = os.environ.get("IBM_QUANTUM_INSTANCE_CRN")
    if not token or not instance:
        raise RuntimeError("IBM token or instance missing")
    channel = os.environ.get("IBM_QUANTUM_CHANNEL", "").strip() or "ibm_cloud"
    return {"channel": channel, "token": token, "instance": instance}
