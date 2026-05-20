from __future__ import annotations

import argparse
import copy
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from qrope.automated_stage_gates import (
    PRODUCT_STATE_CIRCUIT_FAMILY,
    generate_transformer_phase_wrap_attention_bundle,
    run_hardware_packet,
    write_json,
)
from qrope.env_utils import load_local_dotenv


REPO_ROOT = Path(__file__).resolve().parents[1]
LOG_ROOT = REPO_ROOT / "logs" / "automated_stage_gates"
DEFAULT_DEVICE_ARN = "arn:aws:braket:us-west-1::device/qpu/rigetti/Cepheus-1-108Q"
DEFAULT_OUTPUT_S3_PREFIX_ROOT = "phasewrap-rope/braket-hardware-smoke"


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


def _artifact_summary(result: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    execution = result.get("execution", {})
    preflight = result.get("preflight", {})
    jobs = execution.get("jobs", [])
    return {
        "artifact_dir": str(out_dir),
        "status": result.get("status"),
        "outcome": result.get("outcome"),
        "gate_pass": result.get("gate_pass"),
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


def run_braket_smoke(args: argparse.Namespace) -> tuple[dict[str, Any], Path]:
    load_local_dotenv(REPO_ROOT / ".env")
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_s3_prefix = args.s3_prefix or f"{DEFAULT_OUTPUT_S3_PREFIX_ROOT}-{timestamp}"
    env = copy.deepcopy({str(key): str(value) for key, value in os.environ.items()})
    env.update(
        {
            "QROPE_REAL_HARDWARE_PROVIDER": "amazon_braket",
            "QROPE_BRAKET_DEVICE_ARN": args.device_arn,
            "QROPE_BRAKET_AWS_REGION": args.region,
            "QROPE_BRAKET_OUTPUT_S3_BUCKET": args.s3_bucket,
            "QROPE_BRAKET_OUTPUT_S3_PREFIX": output_s3_prefix,
            "QROPE_BRAKET_BUDGET_USD_CAP": str(args.budget_usd_cap),
            "QROPE_BRAKET_ESTIMATED_COST_USD": str(args.estimated_cost_usd),
            "QROPE_HARDWARE_ROW_LIMIT": str(args.row_limit),
            "QROPE_HARDWARE_SHOT_COUNT": str(args.shots),
            "QROPE_BRAKET_JOB_TIMEOUT_SEC": str(args.timeout_sec),
            "QROPE_BRAKET_POLL_INTERVAL_SEC": str(args.poll_interval_sec),
            "QROPE_HARDWARE_CIRCUIT_FAMILY": args.circuit_family,
        }
    )
    if args.profile:
        env["QROPE_BRAKET_AWS_PROFILE"] = args.profile

    bundle = generate_transformer_phase_wrap_attention_bundle(args.seed)
    result = run_hardware_packet(bundle.test[: args.row_limit], env=env)

    out_dir = LOG_ROOT / f"braket_hardware_smoke_{timestamp}"
    write_json(out_dir / "hardware_result.json", result)
    write_json(out_dir / "frozen_packet.json", result.get("packet", {}))
    write_json(out_dir / "preflight.json", result.get("preflight", {}))
    write_json(out_dir / "execution.json", result.get("execution", {}))
    write_json(out_dir / "evaluation.json", result.get("evaluation", {}))
    write_json(out_dir / "summary.json", _artifact_summary(result, out_dir))
    return result, out_dir


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run one bounded Amazon Braket Stage 4 hardware smoke packet.")
    parser.add_argument("--profile", default=os.environ.get("QROPE_BRAKET_AWS_PROFILE", os.environ.get("AWS_PROFILE", "")))
    parser.add_argument("--region", default=os.environ.get("QROPE_BRAKET_AWS_REGION", "us-west-1"))
    parser.add_argument("--device-arn", default=os.environ.get("QROPE_BRAKET_DEVICE_ARN", DEFAULT_DEVICE_ARN))
    parser.add_argument("--s3-bucket", default=os.environ.get("QROPE_BRAKET_OUTPUT_S3_BUCKET", ""))
    parser.add_argument("--s3-prefix", default=os.environ.get("QROPE_BRAKET_OUTPUT_S3_PREFIX", ""))
    parser.add_argument("--row-limit", type=int, default=1)
    parser.add_argument("--shots", type=int, default=10)
    parser.add_argument("--budget-usd-cap", type=float, default=1.0)
    parser.add_argument("--estimated-cost-usd", type=float, default=0.01)
    parser.add_argument("--timeout-sec", type=float, default=600.0)
    parser.add_argument("--poll-interval-sec", type=float, default=15.0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--circuit-family", default=PRODUCT_STATE_CIRCUIT_FAMILY)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    result, out_dir = run_braket_smoke(args)
    summary = _artifact_summary(result, out_dir)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if result.get("gate_pass") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
