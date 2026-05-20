from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = REPO_ROOT / "logs" / "automated_stage_gates" / "stage4_bitstring_calibration"
SCHEMA_VERSION = "qrope_stage4_bitstring_calibration_manifest_v1"
STATES = ("00", "01", "10", "11")
TARGETS = (
    ("ibm_runtime", "IBM provider path", "q1q0"),
    ("amazon_braket", "Amazon Braket provider path", "q0q1"),
)


def build_manifest(output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, Any]:
    records = []
    for provider, label, expected_order in TARGETS:
        packet_path = output_dir / f"{provider}_known_state_packet.json"
        records.append(
            {
                "record_id": f"{provider}__known_state_bitstring_order_v1",
                "provider": provider,
                "provider_label": label,
                "expected_bitstring_order": expected_order,
                "states": list(STATES),
                "shots_per_state": 1000,
                "packet_path": str(packet_path.relative_to(REPO_ROOT).as_posix()),
                "execution_path": None,
                "status": "missing_evidence",
                "missing_evidence": [
                    "real execution raw counts for |00>, |01>, |10>, and |11>",
                    "task or job IDs",
                    "backend metadata",
                    "timestamps",
                ],
            }
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "prepared_at_utc": "2026-05-20T00:00:00Z",
        "no_hardware_submission": True,
        "purpose": "Predeclare provider known-state packets for bitstring-order calibration.",
        "records": records,
        "claim_boundary": {
            "supported": [
                "Calibration packet structure is fixed before future execution.",
                "Verifier will fail clearly until real raw counts are supplied.",
            ],
            "excluded": [
                "completed provider calibration",
                "new hardware evidence",
                "provider-wide bitstring-order claim",
            ],
        },
    }


def build_packet(provider: str, expected_order: str) -> dict[str, Any]:
    return {
        "schema_version": "qrope_stage4_bitstring_calibration_packet_v1",
        "provider": provider,
        "expected_bitstring_order": expected_order,
        "no_hardware_submission": True,
        "states": [
            {
                "state": state,
                "preparation": f"prepare computational basis |{state}> on q0,q1",
                "expected_dominant_key": state if expected_order == "q0q1" else state[::-1],
            }
            for state in STATES
        ],
        "required_execution_fields": [
            "job_or_task_ids",
            "backend_metadata",
            "submitted_at_utc",
            "completed_at_utc",
            "raw_counts_by_state",
        ],
    }


def write_outputs(output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = build_manifest(output_dir)
    for record in manifest["records"]:
        packet = build_packet(str(record["provider"]), str(record["expected_bitstring_order"]))
        (REPO_ROOT / record["packet_path"]).write_text(json.dumps(packet, indent=2, sort_keys=True), encoding="utf-8")
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    return {"manifest": str(manifest_path)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Prepare no-hardware Stage 4 provider bitstring calibration packet specs.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)
    paths = write_outputs(args.output_dir)
    print(f"wrote {paths['manifest']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
