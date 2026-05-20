from __future__ import annotations

import argparse
import copy
import json
import os
import subprocess
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


def _coerce_float(value: Any) -> float | None:
    try:
        cast = float(value)
    except (TypeError, ValueError):
        return None
    return cast if cast >= 0.0 else None


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


def _split_env_list(value: str) -> list[str]:
    return [item.strip() for item in value.replace(";", ",").split(",") if item.strip()]


def _aws_region_from_arn(arn: str) -> str:
    parts = arn.split(":")
    return parts[3] if len(parts) > 3 else ""


def _aws_cmd(profile: str, region: str, service: str, operation: str) -> list[str]:
    cmd = ["aws", service, operation]
    if region:
        cmd.extend(["--region", region])
    if profile:
        cmd.extend(["--profile", profile])
    return cmd


def discover_braket_backends() -> list[dict[str, Any]]:
    backends: list[dict[str, Any]] = []
    device_arns = _split_env_list(os.environ.get("QROPE_BRAKET_DEVICE_ARNS", ""))
    single_device_arn = os.environ.get("QROPE_BRAKET_DEVICE_ARN", "").strip()
    if single_device_arn:
        device_arns.append(single_device_arn)
    if not device_arns:
        return backends

    profile = os.environ.get("QROPE_BRAKET_AWS_PROFILE", os.environ.get("AWS_PROFILE", "")).strip()
    s3_bucket = os.environ.get("QROPE_BRAKET_OUTPUT_S3_BUCKET", "").strip()
    seen = set()
    for arn in device_arns:
        if arn in seen:
            continue
        seen.add(arn)
        region = os.environ.get("QROPE_BRAKET_AWS_REGION", "").strip() or _aws_region_from_arn(arn)
        cmd = _aws_cmd(profile, region, "braket", "get-device")
        cmd.extend(["--device-arn", arn])
        try:
            completed = subprocess.run(cmd, capture_output=True, text=True, check=False)
            if completed.returncode != 0:
                backends.append(
                    {
                        "provider": "amazon_braket",
                        "backend": arn,
                        "aws_profile": profile,
                        "aws_region": region,
                        "output_s3_bucket": s3_bucket,
                        "status": f"unreadable: {completed.stderr.strip() or completed.stdout.strip()}",
                    }
                )
                continue
            device = json.loads(completed.stdout or "{}")
            status = str(device.get("deviceStatus", "unknown"))
            if status.upper() != "ONLINE":
                continue
            caps = json.loads(device.get("deviceCapabilities") or "{}")
            service_caps = caps.get("service", {}) if isinstance(caps, dict) else {}
            shots_range = service_caps.get("shotsRange") if isinstance(service_caps, dict) else None
            max_shots = _coerce_int(shots_range[-1]) if isinstance(shots_range, list) and shots_range else None
            device_cost = service_caps.get("deviceCost", {}) if isinstance(service_caps, dict) else {}
            cost_per_shot = _coerce_float(device_cost.get("price")) if isinstance(device_cost, dict) else None
            backends.append(
                {
                    "provider": "amazon_braket",
                    "backend": arn,
                    "aws_profile": profile,
                    "aws_region": region,
                    "output_s3_bucket": s3_bucket,
                    "max_shots": max_shots,
                    "cost_per_shot_usd": cost_per_shot,
                    "cost_unit": device_cost.get("unit") if isinstance(device_cost, dict) else None,
                    "status": "online",
                    "device_name": device.get("deviceName", ""),
                    "provider_name": device.get("providerName", ""),
                }
            )
        except Exception as exc:
            backends.append(
                {
                    "provider": "amazon_braket",
                    "backend": arn,
                    "aws_profile": profile,
                    "aws_region": region,
                    "output_s3_bucket": s3_bucket,
                    "status": f"unreadable: {exc}",
                }
            )
    return backends


def list_available_targets() -> list[dict[str, Any]]:
    load_local_dotenv(REPO_ROOT / ".env")
    all_backends: list[dict[str, Any]] = []
    all_backends.extend(discover_ibm_backends())
    all_backends.extend(discover_ionq_backends())
    all_backends.extend(discover_braket_backends())
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


def _execution_task_arns(execution: dict[str, Any]) -> list[str]:
    task_arns: list[str] = []
    for job in execution.get("jobs", []):
        for record in job.get("provider_job_records", []):
            task_arn = record.get("job_id")
            if task_arn:
                task_arns.append(str(task_arn))
        if not job.get("provider_job_records") and job.get("job_id"):
            task_arns.extend(item for item in str(job["job_id"]).split(",") if item)
    return task_arns


def _execution_result_s3_uris(execution: dict[str, Any]) -> list[str]:
    uris: list[str] = []
    for job in execution.get("jobs", []):
        for row in job.get("raw_counts_by_row", []):
            uri = row.get("result_s3_uri")
            if uri:
                uris.append(str(uri))
    return uris


def _artifact_summary(
    result: dict[str, Any],
    backend: dict[str, Any],
    *,
    shot_target: int,
    shot_count: int,
    row_limit: int,
    result_dir: Path,
) -> dict[str, Any]:
    execution = result.get("execution", {})
    preflight = result.get("preflight", {})
    jobs = execution.get("jobs", [])
    return {
        "artifact_dir": str(result_dir),
        "status": result.get("status"),
        "outcome": result.get("outcome"),
        "gate_pass": result.get("gate_pass"),
        "provider": backend["provider"],
        "backend": backend["backend"],
        "target_shots": shot_target,
        "effective_shots": shot_count,
        "cost_per_shot_usd": backend.get("cost_per_shot_usd"),
        "row_limit": row_limit,
        "packet_id": result.get("packet", {}).get("packet_id"),
        "preflight_status": preflight.get("status"),
        "preflight_blockers": preflight.get("blockers", []),
        "account_setup_check": preflight.get("account_setup_check"),
        "execution_status": execution.get("status"),
        "error_category": execution.get("error_category"),
        "blockers": execution.get("blockers", []),
        "job_ids": [job.get("job_id") for job in jobs],
        "task_arns": _execution_task_arns(execution),
        "result_s3_uris": _execution_result_s3_uris(execution),
        "error": execution.get("error"),
    }


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
    if backend["provider"] == "amazon_braket":
        env["QROPE_BRAKET_DEVICE_ARN"] = backend["backend"]
        env["QROPE_BRAKET_AWS_PROFILE"] = str(backend.get("aws_profile", ""))
        env["QROPE_BRAKET_AWS_REGION"] = str(backend.get("aws_region", ""))
        env["QROPE_BRAKET_OUTPUT_S3_BUCKET"] = str(backend.get("output_s3_bucket", ""))
        env["QROPE_BRAKET_OUTPUT_S3_PREFIX"] = (
            "phasewrap-rope/stage4-hardware-sweep/"
            f"{_safe_name(backend['backend'])}/"
            f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
        )
        env["QROPE_BRAKET_BUDGET_USD_CAP"] = str(budget_cap)
        cost_per_shot = backend.get("cost_per_shot_usd")
        if cost_per_shot is None:
            cost_per_shot = float(os.environ.get("QROPE_BRAKET_COST_PER_SHOT_USD", "0.001"))
        env["QROPE_BRAKET_ESTIMATED_COST_USD"] = f"{float(shot_count) * float(cost_per_shot):.12g}"
        env["QROPE_BRAKET_COST_PER_SHOT_USD"] = str(cost_per_shot)
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
    (target_dir / "frozen_packet.json").write_text(json.dumps(result.get("packet", {}), indent=2, sort_keys=True), encoding="utf-8")
    (target_dir / "preflight.json").write_text(json.dumps(result.get("preflight", {}), indent=2, sort_keys=True), encoding="utf-8")
    (target_dir / "execution.json").write_text(json.dumps(result.get("execution", {}), indent=2, sort_keys=True), encoding="utf-8")
    (target_dir / "evaluation.json").write_text(json.dumps(result.get("evaluation", {}), indent=2, sort_keys=True), encoding="utf-8")
    summary = _artifact_summary(
        result,
        backend,
        shot_target=shot_target,
        shot_count=shot_count,
        row_limit=row_limit,
        result_dir=target_dir,
    )
    (target_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    return result, target_dir


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Stage 4 on all discovered hardware targets.")
    parser.add_argument(
        "--providers",
        default="",
        help="Comma-separated provider filter, for example amazon_braket or ibm_runtime,amazon_braket.",
    )
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
    parser.add_argument("--braket-device-arn", action="append", default=[], help="Amazon Braket device ARN to add.")
    parser.add_argument("--braket-profile", default="", help="AWS profile for Amazon Braket targets.")
    parser.add_argument("--braket-region", default="", help="AWS region for Amazon Braket targets.")
    parser.add_argument("--braket-s3-bucket", default="", help="S3 bucket for Amazon Braket task results.")
    parser.add_argument("--braket-timeout-sec", type=float, help="Maximum seconds to wait for each Braket task.")
    parser.add_argument("--braket-poll-interval-sec", type=float, help="Seconds between Braket task status polls.")
    parser.add_argument(
        "--require-pass",
        action="store_true",
        help="Return a non-zero exit code unless every attempted target passes the hardware gate.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    load_local_dotenv(REPO_ROOT / ".env")
    if args.braket_device_arn:
        existing_arns = _split_env_list(os.environ.get("QROPE_BRAKET_DEVICE_ARNS", ""))
        os.environ["QROPE_BRAKET_DEVICE_ARNS"] = ",".join(existing_arns + args.braket_device_arn)
    if args.braket_profile:
        os.environ["QROPE_BRAKET_AWS_PROFILE"] = args.braket_profile
    if args.braket_region:
        os.environ["QROPE_BRAKET_AWS_REGION"] = args.braket_region
    if args.braket_s3_bucket:
        os.environ["QROPE_BRAKET_OUTPUT_S3_BUCKET"] = args.braket_s3_bucket
    if args.braket_timeout_sec is not None:
        os.environ["QROPE_BRAKET_JOB_TIMEOUT_SEC"] = str(args.braket_timeout_sec)
    if args.braket_poll_interval_sec is not None:
        os.environ["QROPE_BRAKET_POLL_INTERVAL_SEC"] = str(args.braket_poll_interval_sec)

    targets = list_available_targets()
    provider_filter = set(_split_env_list(args.providers))
    if provider_filter:
        targets = [target for target in targets if target.get("provider") in provider_filter]
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
    if args.require_pass and not all(item["status"] == "PASS" for item in outcomes):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
