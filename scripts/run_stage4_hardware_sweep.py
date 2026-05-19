from __future__ import annotations

import argparse
import copy
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from qrope.automated_stage_gates import HARDWARE_PACKET_ROW_LIMIT, generate_transformer_phase_wrap_attention_bundle, run_hardware_packet
from qrope.automated_stage_gates import PRODUCT_STATE_CIRCUIT_FAMILY
from qrope.env_utils import load_local_dotenv


REPO_ROOT = Path(__file__).resolve().parents[1]
LOG_ROOT = REPO_ROOT / "logs" / "automated_stage_gates" / "stage4_hardware_sweep"


def _safe_name(value: str) -> str:
    return "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in value)


def _coerce_int(value: Any) -> int | None:
    try:
        cast = int(value)
    except (TypeError, ValueError):
        return None
    return cast if cast > 0 else None


def discover_ibm_backends() -> list[dict[str, Any]]:
    backends: list[dict[str, Any]] = []
    token = os.environ.get("IBM_QUANTUM_TOKEN") or os.environ.get("QISKIT_IBM_TOKEN")
    if not token:
        return backends
    try:
        from qiskit_ibm_runtime import QiskitRuntimeService

        kwargs = {"channel": "ibm_cloud", "token": token.strip()}
        instance = os.environ.get("IBM_QUANTUM_INSTANCE_CRN", "").strip()
        if instance:
            kwargs["instance"] = instance
        service = QiskitRuntimeService(**kwargs)
        for backend in service.backends():
            try:
                name = str(getattr(backend, "name", ""))
                config = backend.configuration()
                status = backend.status() if hasattr(backend, "status") else None
                max_shots = _coerce_int(getattr(config, "max_shots", None))
                is_online = bool(getattr(status, "operational", True))
                if not is_online:
                    continue
                backend_type = str(type(config).__name__).lower()
                if "sim" in name.lower() and "simulator" in backend_type:
                    continue
                backends.append(
                    {
                        "provider": "ibm_runtime",
                        "backend": name,
                        "max_shots": max_shots,
                        "status": "online",
                    }
                )
            except Exception as exc:
                backends.append(
                    {
                        "provider": "ibm_runtime",
                        "backend": str(getattr(backend, "name", "ibm_unknown")),
                        "status": f"unreadable: {exc}",
                    }
                )
    except Exception as exc:
        print(f"IBM backend discovery failed: {exc}")
    return backends


def discover_ionq_backends() -> list[dict[str, Any]]:
    backends: list[dict[str, Any]] = []
    token = os.environ.get("IONQ_API_KEY") or os.environ.get("IONQ_API_TOKEN")
    if not token:
        return backends
    try:
        from qiskit_ionq import IonQProvider

        provider = IonQProvider(token=token.strip())
        for backend in provider.backends():
            name = str(getattr(backend, "name", ""))
            if "simulator" in name.lower():
                continue
            opt = getattr(backend, "options", None)
            max_shots = _coerce_int(getattr(opt, "shots", None))
            status = "online"
            try:
                status_value = backend.status()
                if isinstance(status_value, str) and status_value.lower() in {"false", "0", "unavailable"}:
                    continue
            except Exception:
                pass
            backends.append(
                {
                    "provider": "ionq",
                    "backend": name,
                    "max_shots": max_shots,
                    "status": status,
                }
            )
    except Exception as exc:
        print(f"IonQ backend discovery failed: {exc}")
    return backends


def list_available_targets() -> list[dict[str, Any]]:
    load_local_dotenv(REPO_ROOT / ".env")
    all_backends: list[dict[str, Any]] = []
    all_backends.extend(discover_ibm_backends())
    all_backends.extend(discover_ionq_backends())
    dedup = []
    seen = set()
    for item in all_backends:
        key = (item["provider"], item["backend"])
        if key in seen:
            continue
        seen.add(key)
        if item.get("status") in {"online", "unreadable: online", "unreadable: open"}:
            pass
        dedup.append(item)
    return dedup


def _target_shots(default_target: int, max_shots: int | None) -> int:
    if not max_shots:
        return min(default_target, 1024)
    return min(default_target, max_shots)


def run_single_backend(
    base_env: dict[str, str],
    backend: dict[str, Any],
    row_limit: int,
    family: str,
    shot_target: int,
    budget_cap: float,
) -> tuple[dict[str, Any], Path]:
    shot_count = _target_shots(shot_target, backend.get("max_shots")) if isinstance(backend.get("max_shots"), int) else shot_target
    env = copy.deepcopy(base_env)
    env["QROPE_REAL_HARDWARE_PROVIDER"] = backend["provider"]
    env["QROPE_HARDWARE_BACKEND"] = backend["backend"]
    env["QROPE_HARDWARE_SHOT_COUNT"] = str(shot_count)
    env["QROPE_HARDWARE_ROW_LIMIT"] = str(row_limit)
    env["QROPE_HARDWARE_CIRCUIT_FAMILY"] = family
    env["QROPE_HARDWARE_BUDGET_USD_CAP"] = str(budget_cap)
    run_payload: dict[str, Any] = {
        "target_shots": shot_target,
        "effective_shots": shot_count,
    }
    bundle = generate_transformer_phase_wrap_attention_bundle(42)
    result = run_hardware_packet(bundle.test[:row_limit], env=env)
    run_payload["result"] = result
    run_payload["backend"] = backend
    run_payload["params"] = {
        "provider": backend["provider"],
        "backend": backend["backend"],
        "row_limit": row_limit,
        "circuit_family": family,
        "budget_usd_cap": budget_cap,
    }

    tag = f'{_safe_name(backend["provider"])}__{_safe_name(backend["backend"])}'
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    target_dir = LOG_ROOT / tag / f"{family}_{timestamp}"
    target_dir.mkdir(parents=True, exist_ok=True)
    (target_dir / "run_payload.json").write_text(json.dumps(run_payload, indent=2, sort_keys=True), encoding="utf-8")
    (target_dir / "summary.json").write_text(
        json.dumps(
            {
                "status": result["status"],
                "outcome": result["outcome"],
                "provider": backend["provider"],
                "backend": backend["backend"],
                "target_shots": shot_target,
                "effective_shots": shot_count,
                "row_limit": row_limit,
                "packet_id": result.get("packet", {}).get("packet_id"),
                "job_ids": [job.get("job_id") for job in result.get("execution", {}).get("jobs", [])],
            },
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    return result, target_dir


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Stage 4 on all discovered hardware targets.")
    parser.add_argument(
        "--target-shots",
        type=int,
        default=4096,
        help="Target shot count before backend cap fallback.",
    )
    parser.add_argument(
        "--row-limit",
        type=int,
        default=HARDWARE_PACKET_ROW_LIMIT,
        help="Rows in the frozen packet.",
    )
    parser.add_argument(
        "--circuit-family",
        default=PRODUCT_STATE_CIRCUIT_FAMILY,
        help="Circuit family to run (default is product-state witness).",
    )
    parser.add_argument(
        "--budget-usd-cap",
        type=float,
        default=1000.0,
        help="Hardware budget cap in USD (for preflight gating).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    load_local_dotenv(REPO_ROOT / ".env")
    targets = list_available_targets()
    if not targets:
        print("No available hardware targets discovered.")
        return 1

    print(f"Discovered {len(targets)} hardware targets:")
    for item in targets:
        print(f"- {item['provider']} {item['backend']} max_shots={item.get('max_shots', 'unknown')}")

    base_env = {str(k): str(v) for k, v in os.environ.items()}
    bundle_rows = row_limit = args.row_limit
    outcomes = []

    for target in targets:
        print(
            f"Running {target['provider']} backend {target['backend']} "
            f"with target shots {args.target_shots}"
        )
        result, result_dir = run_single_backend(
            base_env=base_env,
            backend=target,
            row_limit=bundle_rows,
            family=args.circuit_family,
            shot_target=args.target_shots,
            budget_cap=args.budget_usd_cap,
        )
        witness = result.get("evaluation", {}).get("witness", {})
        control = result.get("evaluation", {}).get("control", {})
        print(
            f"-> status={result['status']} outcome={result['outcome']} "
            f"shots={_target_shots(args.target_shots, target.get('max_shots')) if target.get('max_shots') else args.target_shots} "
            f"dir={result_dir}"
        )
        print(f"   witness mae/rank = {witness.get('mae')} / {witness.get('rank_correlation')}")
        print(f"   control mae/rank = {control.get('mae')} / {control.get('rank_correlation')}")
        outcomes.append(
            {
                "provider": target["provider"],
                "backend": target["backend"],
                "status": result["status"],
                "outcome": result["outcome"],
                "shots": _target_shots(args.target_shots, target.get("max_shots"))
                if target.get("max_shots")
                else args.target_shots,
                "result_dir": str(result_dir),
            }
        )

    print("\nSweep summary:")
    for item in outcomes:
        print(f"- {item['provider']}/{item['backend']}: {item['status']} / {item['outcome']} (shots={item['shots']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
