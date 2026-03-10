from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Aggregate Q-RoPE run metrics")
    parser.add_argument("--input", required=True, help="Input run root")
    parser.add_argument("--output", required=True, help="Output CSV file")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_root = Path(args.input)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, object]] = []
    for metrics_file in sorted(input_root.glob("*/metrics.json")):
        with metrics_file.open("r", encoding="utf-8") as f:
            rows.append(json.load(f))

    preferred_order = [
        "run_id",
        "variant",
        "dataset",
        "seed",
        "backend",
        "accuracy",
        "f1",
        "mae",
        "rank_correlation",
        "calibration_slope",
        "train_loss_final",
        "eval_loss",
        "qubit_count",
        "gate_count_total",
        "circuit_depth",
        "shot_count",
        "noise_model",
        "wall_time_sec",
        "timestamp_utc",
        "dry_run",
        "run_mode",
        "data_mode",
    ]
    seen_fields: set[str] = set()
    for row in rows:
        seen_fields.update(row.keys())
    fieldnames = [name for name in preferred_order if name in seen_fields]
    fieldnames.extend(sorted(seen_fields - set(fieldnames)))
    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote summary CSV: {output_path}")
    print(f"Rows: {len(rows)}")


if __name__ == "__main__":
    main()
