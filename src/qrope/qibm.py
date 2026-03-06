from __future__ import annotations

import os
import time
from functools import lru_cache
from pathlib import Path

from .env_utils import load_local_dotenv
from .qsim import effective_variant_phases, feature_angles


def derive_ibm_angles(text: str, variant: str, seed: int) -> tuple[float, float]:
    features = feature_angles(text=text, n_qubits=2, seed=seed)
    phases = effective_variant_phases(variant, features)
    return features[0], phases[0] + 0.5 * phases[1]


@lru_cache(maxsize=1)
def get_ibm_service():
    load_local_dotenv(Path(".env"))
    token = os.environ.get("IBM_QUANTUM_TOKEN", "").strip()
    if not token:
        raise RuntimeError("IBM_QUANTUM_TOKEN is missing for ibm_runtime_remote backend")

    from qiskit_ibm_runtime import QiskitRuntimeService

    return QiskitRuntimeService(channel="ibm_cloud", token=token)


@lru_cache(maxsize=4)
def get_ibm_backend(backend_name: str | None = None):
    service = get_ibm_service()
    if backend_name:
        return service.backend(backend_name)
    preferred = os.environ.get("IBM_QUANTUM_BACKEND", "").strip()
    if preferred:
        return service.backend(preferred)
    for candidate in ("ibm_torino", "ibm_marrakesh", "ibm_fez"):
        try:
            return service.backend(candidate)
        except Exception:
            continue
    backends = service.backends()
    if not backends:
        raise RuntimeError("No IBM Runtime backends available")
    return backends[0]


def run_ibm_sampler_batch(
    texts: list[str],
    variant: str,
    seed: int,
    backend_name: str | None = None,
    shots: int = 128,
    retries: int = 2,
) -> list[float]:
    from qiskit import QuantumCircuit
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
    from qiskit_ibm_runtime import SamplerV2

    backend = get_ibm_backend(backend_name)
    circuits = []
    for text in texts:
        ry_angle, rz_angle = derive_ibm_angles(text=text, variant=variant, seed=seed)
        qc = QuantumCircuit(1)
        qc.ry(ry_angle, 0)
        qc.rz(rz_angle, 0)
        qc.measure_all()
        circuits.append(qc)

    pass_manager = generate_preset_pass_manager(backend=backend, optimization_level=1)
    pubs = [pass_manager.run(circuit) for circuit in circuits]

    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            sampler = SamplerV2(mode=backend)
            job = sampler.run(pubs, shots=shots)
            result = job.result()
            scores: list[float] = []
            for pub_result in result:
                counts = pub_result.data.meas.get_counts()
                p1 = counts.get("1", 0) / shots
                scores.append(max(0.0, min(1.0, float(p1))))
            return scores
        except Exception as exc:
            last_error = exc
            if attempt >= retries:
                break
            time.sleep(2.0 * (attempt + 1))
    raise RuntimeError("IBM Runtime batch execution failed") from last_error
