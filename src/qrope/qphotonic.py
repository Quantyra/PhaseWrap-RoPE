from __future__ import annotations

import os
import time
from functools import lru_cache
from pathlib import Path

import requests

from .env_utils import load_local_dotenv
from .qsim import effective_variant_phases, feature_angles

THETA_MIN = 0.2
THETA_MAX = 1.4
PHOTONIC_RETRY_DELAYS_SEC = (2.0, 5.0, 10.0)


def derive_photonic_angles(text: str, variant: str, seed: int) -> tuple[float, float, float]:
    features = feature_angles(text=text, n_qubits=2, seed=seed)
    phases = effective_variant_phases(variant, features)
    theta_left = THETA_MIN + 1.2 * (features[0] / 3.141592653589793)
    theta_right = THETA_MIN + 1.2 * (features[1] / 3.141592653589793)
    relative_phase = phases[1] - phases[0]
    return theta_left, theta_right, relative_phase


def photonic_distribution_to_score(distribution: object) -> float:
    from perceval import BasicState

    p20 = float(distribution.get(BasicState("|2,0>"), 0.0))
    p11 = float(distribution.get(BasicState("|1,1>"), 0.0))
    p02 = float(distribution.get(BasicState("|0,2>"), 0.0))
    score = p20 + 0.5 * p11 + 0.25 * p02
    return max(0.0, min(1.0, score))


@lru_cache(maxsize=4)
def get_quandela_remote_processor(platform_name: str):
    load_local_dotenv(Path(".env"))
    token = os.environ.get("QUANDELA_CLOUD_TOKEN", "").strip()
    if not token:
        raise RuntimeError("QUANDELA_CLOUD_TOKEN is missing for sim_quandela_remote backend")

    from perceval.providers import QuandelaSession

    session = QuandelaSession(platform_name=platform_name, token=token)
    return session.build_remote_processor()


def clear_quandela_remote_processor_cache() -> None:
    get_quandela_remote_processor.cache_clear()


def compute_effective_theta(theta_left: float, theta_right: float, relative_phase: float) -> float:
    return max(THETA_MIN, min(THETA_MAX, (theta_left + theta_right) / 2.0 + relative_phase / 4.0))


def inspect_quandela_submission_error(job, rpc_handler) -> str:
    try:
        payload = job._create_payload_data()
        endpoint = rpc_handler.build_endpoint("/api/job")
        response = requests.post(
            endpoint,
            headers=rpc_handler.headers,
            json=payload,
            timeout=rpc_handler.request_timeout,
            proxies=rpc_handler.proxies,
        )
        text = response.text.strip()
        if text:
            return text[:300]
    except Exception:
        return ""
    return ""


def quandela_remote_score(
    text: str,
    variant: str,
    seed: int,
    platform_name: str = "sim:slos",
    max_shots_per_call: int = 100,
    retries: int = 3,
) -> float:
    from perceval import BasicState, Circuit, Processor
    from perceval.algorithm import Sampler
    from perceval.components import BS

    theta_left, theta_right, relative_phase = derive_photonic_angles(text=text, variant=variant, seed=seed)
    effective_theta = compute_effective_theta(theta_left=theta_left, theta_right=theta_right, relative_phase=relative_phase)

    last_error: Exception | None = None
    for attempt in range(retries + 1):
        try:
            circuit = Circuit(2)
            circuit.add((0, 1), BS(theta=effective_theta))

            local = Processor("SLOS", circuit)
            rpc = get_quandela_remote_processor(platform_name=platform_name)
            remote = rpc.from_local_processor(local, rpc_handler=rpc.get_rpc_handler())
            remote.with_input(BasicState("|1,1>"))
            remote.min_detected_photons_filter(2)
            sampler = Sampler(remote, max_shots_per_call=max_shots_per_call)
            job = sampler.probs
            result = job.execute_sync()
            return photonic_distribution_to_score(result["results"])
        except Exception as exc:
            last_error = exc
            provider_detail = inspect_quandela_submission_error(job, remote.get_rpc_handler()) if "job" in locals() else ""
            clear_quandela_remote_processor_cache()
            if attempt >= retries:
                break
            time.sleep(PHOTONIC_RETRY_DELAYS_SEC[min(attempt, len(PHOTONIC_RETRY_DELAYS_SEC) - 1)])
    detail_suffix = f" provider_detail={provider_detail}" if provider_detail else ""
    raise RuntimeError(
        f"Quandela remote submission failed after retries for effective_theta={effective_theta:.6f}.{detail_suffix}"
    ) from last_error
