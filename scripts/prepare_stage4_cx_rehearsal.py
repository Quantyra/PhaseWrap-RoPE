from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]

import sys

sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.automated_stage_gates import (
    ENTANGLING_CX_CIRCUIT_FAMILY,
    evaluate_hardware_execution,
    freeze_hardware_packet,
    generate_transformer_phase_wrap_attention_bundle,
    ideal_counts_for_hardware_row,
)


DEFAULT_OUTPUT_DIR = (
    REPO_ROOT
    / "logs"
    / "automated_stage_gates"
    / "stage4_cx_rehearsal"
    / "ideal_counts_rehearsal"
)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def prepare_rehearsal(output_dir: Path, *, rows: int, shots: int) -> dict[str, Any]:
    env = {
        "QROPE_REAL_HARDWARE_PROVIDER": "local_rehearsal",
        "QROPE_HARDWARE_BACKEND": "ideal_counts_rehearsal",
        "QROPE_HARDWARE_CIRCUIT_FAMILY": ENTANGLING_CX_CIRCUIT_FAMILY,
        "QROPE_HARDWARE_ROW_LIMIT": str(rows),
        "QROPE_HARDWARE_SHOT_COUNT": str(shots),
        "QROPE_HARDWARE_BUDGET_USD_CAP": "0",
    }
    bundle = generate_transformer_phase_wrap_attention_bundle(42)
    packet = freeze_hardware_packet(bundle.test[:rows], env)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    execution = {
        "status": "COMPLETED",
        "jobs": [
            {
                "job_id": "local-cx-rehearsal-no-hardware",
                "provider": packet["provider"],
                "backend": packet["backend"],
                "packet_id": packet["packet_id"],
                "submitted_at_utc": now,
                "completed_at_utc": now,
                "shot_count": packet["shot_count"],
                "circuit_count": len(packet["rows"]),
                "raw_counts_by_row": [
                    {
                        "row_id": row["row_id"],
                        "counts": ideal_counts_for_hardware_row(row, packet["shot_count"]),
                    }
                    for row in packet["rows"]
                ],
            }
        ],
        "backend_metadata": {
            "provider": packet["provider"],
            "backend": packet["backend"],
            "simulated": True,
            "hardware_submitted": False,
            "captured_at_utc": now,
        },
        "calibration_metadata": {
            "simulated": True,
            "hardware_submitted": False,
            "source": "ideal_counts_for_hardware_row",
            "captured_at_utc": now,
        },
    }
    evaluation = evaluate_hardware_execution(packet, execution)
    evaluation["fixture_type"] = "local ideal-count rehearsal; not real Stage 4 hardware evidence"
    evaluation["hardware_submitted"] = False
    evaluation["claim_boundary"] = (
        "Evaluator labels are recomputed with the hardware packet machinery, but this rehearsal uses ideal counts only."
    )
    summary = {
        "status": evaluation["status"],
        "outcome": "ideal-count-positive" if evaluation["gate_pass"] else "ideal-count-negative",
        "evaluation_outcome": evaluation["outcome"],
        "gate_pass": evaluation["gate_pass"],
        "hardware_submitted": False,
        "fixture_type": "local ideal-count rehearsal; not real Stage 4 hardware evidence",
        "claim_boundary": "This artifact checks CX packet/evaluator mechanics under ideal counts only. It is not hardware evidence.",
        "family": packet["circuit_family"],
        "provider": packet["provider"],
        "backend": packet["backend"],
        "packet_id": packet["packet_id"],
        "rows": packet["row_count"],
        "shots": packet["shot_count"],
        "witness": evaluation["witness"],
        "control": evaluation["control"],
        "fail_reasons": evaluation["fail_reasons"],
    }
    write_json(output_dir / "frozen_packet.json", packet)
    write_json(output_dir / "execution.json", execution)
    write_json(output_dir / "evaluation.json", evaluation)
    write_json(output_dir / "summary.json", summary)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare a no-hardware ideal-count rehearsal for the Stage 4 CX lane.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--rows", type=int, default=16)
    parser.add_argument("--shots", type=int, default=4096)
    args = parser.parse_args()
    summary = prepare_rehearsal(args.output_dir, rows=args.rows, shots=args.shots)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if summary["gate_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
