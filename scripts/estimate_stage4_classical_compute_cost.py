from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SWEEP_VERIFICATION = REPO_ROOT / "logs" / "automated_stage_gates" / "stage4_hardware_sweep" / "offline_verification.json"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "logs" / "automated_stage_gates" / "stage4_classical_compute_cost"
SCHEMA_VERSION = "qrope_stage4_classical_compute_cost_v1"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _parse_timestamp(raw: str | None) -> datetime | None:
    if not raw:
        return None
    text = str(raw).strip()
    if text.endswith("Z"):
        text = f"{text[:-1]}+00:00"
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def elapsed_seconds(start: str | None, end: str | None) -> float | None:
    start_time = _parse_timestamp(start)
    end_time = _parse_timestamp(end)
    if start_time is None or end_time is None:
        return None
    return round(max(0.0, (end_time - start_time).total_seconds()), 6)


def estimate_classical_ops(row_count: int, bitstring_bins_per_row: int = 4) -> dict[str, int]:
    expectation_ops_per_bin = 9
    prediction_ops_per_row = 18
    metric_ops_per_row = 8
    rank_sort_ops_per_row = 2
    expectation_ops = row_count * bitstring_bins_per_row * expectation_ops_per_bin
    prediction_ops = row_count * prediction_ops_per_row
    metric_ops = row_count * metric_ops_per_row
    rank_proxy_ops = row_count * rank_sort_ops_per_row
    total = expectation_ops + prediction_ops + metric_ops + rank_proxy_ops
    return {
        "bitstring_bins_per_row": bitstring_bins_per_row,
        "expectation_ops": expectation_ops,
        "prediction_ops": prediction_ops,
        "metric_ops": metric_ops,
        "rank_proxy_ops": rank_proxy_ops,
        "total_static_ops": total,
    }


def estimate_record(record: dict[str, Any], *, assumed_ops_per_second: float) -> dict[str, Any]:
    row_count = int(record.get("row_count") or 0)
    shots = int(record.get("shots") or 0)
    ops = estimate_classical_ops(row_count)
    estimated_seconds = round(float(ops["total_static_ops"]) / assumed_ops_per_second, 9)
    hardware_elapsed = elapsed_seconds(record.get("submitted_at_utc"), record.get("completed_at_utc"))
    return {
        "record_id": record.get("record_id"),
        "provider": record.get("provider"),
        "backend": record.get("backend_label") or record.get("backend"),
        "family": record.get("family"),
        "rows": row_count,
        "shots_per_row": shots,
        "total_hardware_shots": row_count * shots,
        "submitted_at_utc": record.get("submitted_at_utc"),
        "completed_at_utc": record.get("completed_at_utc"),
        "recorded_hardware_elapsed_seconds": hardware_elapsed,
        "classical_static_ops": ops["total_static_ops"],
        "classical_estimated_seconds_at_assumed_rate": estimated_seconds,
        "classical_estimated_cost_usd": 0.0,
        "hardware_cost_usd": "not_reconstructed_from_public_artifacts",
    }


def build_cost_estimate(
    verification: dict[str, Any],
    *,
    assumed_ops_per_second: float = 1_000_000.0,
) -> dict[str, Any]:
    if assumed_ops_per_second <= 0.0:
        raise ValueError("assumed_ops_per_second must be positive")
    records = [
        estimate_record(record, assumed_ops_per_second=assumed_ops_per_second)
        for record in verification.get("records", [])
        if record.get("pass") is True
    ]
    total_static_ops = sum(int(record["classical_static_ops"]) for record in records)
    total_hardware_shots = sum(int(record["total_hardware_shots"]) for record in records)
    hardware_elapsed_values = [
        float(record["recorded_hardware_elapsed_seconds"])
        for record in records
        if record.get("recorded_hardware_elapsed_seconds") is not None
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "source_verification_path": "logs/automated_stage_gates/stage4_hardware_sweep/offline_verification.json",
        "record_count": len(records),
        "assumptions": {
            "method": "static_operation_count_estimate",
            "assumed_ops_per_second": assumed_ops_per_second,
            "local_verifier_incremental_cost_usd": 0.0,
            "hardware_cost_usd": "not reconstructed because public artifacts do not contain complete provider billing records",
            "scope": "Classical recomputation of committed Stage 4 raw-count artifacts, not hardware queueing or quantum sampling.",
        },
        "totals": {
            "total_hardware_shots": total_hardware_shots,
            "total_classical_static_ops": total_static_ops,
            "classical_estimated_seconds_at_assumed_rate": round(float(total_static_ops) / assumed_ops_per_second, 9),
            "classical_estimated_cost_usd": 0.0,
            "sum_recorded_hardware_elapsed_seconds": round(sum(hardware_elapsed_values), 6),
        },
        "claim_boundary": {
            "supported": [
                "Static local recomputation of the committed Stage 4 evidence is computationally tiny.",
                "The estimate is reproducible from committed verifier output and does not require provider credentials.",
            ],
            "excluded": [
                "provider billing reconstruction",
                "hardware queue time prediction",
                "quantum advantage or disadvantage claim",
                "production transformer runtime claim",
            ],
        },
        "records": records,
    }


def write_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "source_verification_path": result["source_verification_path"],
        "result_path": str((output_dir / "results.json").as_posix()),
        "summary_csv_path": str((output_dir / "summary.csv").as_posix()),
        "record_count": result["record_count"],
        "assumptions": result["assumptions"],
        "claim_boundary": result["claim_boundary"],
    }
    paths = {
        "manifest": str(output_dir / "manifest.json"),
        "results": str(output_dir / "results.json"),
        "summary_csv": str(output_dir / "summary.csv"),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(result["records"][0].keys()))
        writer.writeheader()
        writer.writerows(result["records"])
    return paths


def print_summary(result: dict[str, Any]) -> None:
    headers = (
        "backend",
        "family",
        "rows",
        "total_hardware_shots",
        "recorded_hardware_elapsed_seconds",
        "classical_static_ops",
        "classical_estimated_seconds_at_assumed_rate",
    )
    print(" | ".join(headers))
    print(" | ".join("---" for _ in headers))
    for row in result["records"]:
        print(" | ".join(str(row.get(header, "")) for header in headers))
    print(json.dumps({"record_count": result["record_count"], "totals": result["totals"]}, indent=2, sort_keys=True))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Estimate classical compute timing/cost for committed Stage 4 sweep recomputation.")
    parser.add_argument("--verification", type=Path, default=DEFAULT_SWEEP_VERIFICATION)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--assumed-ops-per-second", type=float, default=1_000_000.0)
    args = parser.parse_args(argv)

    result = build_cost_estimate(
        read_json(args.verification),
        assumed_ops_per_second=args.assumed_ops_per_second,
    )
    paths = write_outputs(result, args.output_dir)
    print_summary(result)
    print(f"wrote {paths['manifest']}")
    print(f"wrote {paths['results']}")
    print(f"wrote {paths['summary_csv']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
