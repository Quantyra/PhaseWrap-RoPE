from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.verify_stage4_hardware_sweep import verify_sweep_manifest


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SIM_DIR = REPO_ROOT / "logs" / "automated_stage_gates" / "stage4_simulation_sweep"
DEFAULT_MANIFEST = DEFAULT_SIM_DIR / "manifest.json"
DEFAULT_OUTPUT = DEFAULT_SIM_DIR / "offline_verification.json"


def normalize_simulation_verification(verification: dict) -> dict:
    verification["verifier"] = "phasewrap_rope_stage4_simulation_sweep_offline_verifier_v1"
    verification["no_hardware_submission"] = True
    verification["hardware_cost_usd"] = 0
    for row in verification.get("table", []):
        if row.get("outcome") == "hardware-positive":
            row["outcome"] = "simulation-positive"
        elif row.get("outcome") == "hardware-negative":
            row["outcome"] = "simulation-negative"
        elif row.get("outcome") == "hardware-inconclusive":
            row["outcome"] = "simulation-inconclusive"
    for record in verification.get("records", []):
        metrics = record.get("recomputed_metrics")
        if not isinstance(metrics, dict):
            continue
        if metrics.get("outcome") == "hardware-positive":
            metrics["outcome"] = "simulation-positive"
        elif metrics.get("outcome") == "hardware-negative":
            metrics["outcome"] = "simulation-negative"
        elif metrics.get("outcome") == "hardware-inconclusive":
            metrics["outcome"] = "simulation-inconclusive"
    return verification


def print_table(rows: list[dict]) -> None:
    headers = [
        "backend",
        "provider",
        "family",
        "shots",
        "rows",
        "witness_mae",
        "witness_rank_corr",
        "control_mae",
        "control_rank_corr",
        "outcome",
    ]
    print(" | ".join(headers))
    print(" | ".join("---" for _ in headers))
    for row in rows:
        print(" | ".join(str(row.get(header, "")) for header in headers))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Offline verifier for the PhaseWrap-RoPE Stage 4 simulation sweep.")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)

    verification = normalize_simulation_verification(verify_sweep_manifest(args.manifest))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(verification, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if verification["table"]:
        print_table(verification["table"])
    print(
        json.dumps(
            {
                "pass": verification["pass"],
                "sweep_id": verification.get("sweep_id"),
                "missing_records": verification.get("missing_records"),
                "manifest_errors": verification.get("manifest_errors"),
                "output": str(args.output),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if verification["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
