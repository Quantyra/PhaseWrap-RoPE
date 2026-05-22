from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.automated_stage_gates import (  # noqa: E402
    ENTANGLING_CX_CIRCUIT_FAMILY,
    PRODUCT_STATE_CIRCUIT_FAMILY,
    freeze_hardware_packet,
    generate_transformer_phase_wrap_attention_bundle,
)


SCHEMA_VERSION = "qrope_stage4_preregistered_replication_packets_v1"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "logs" / "automated_stage_gates" / "stage4_preregistered_replication_packets"
PREREGISTERED_TIMESTAMP = "2026-05-20T00:00:00Z"

LANES = (
    {
        "lane_id": "ibm_product_seed314_rows16_shots4096",
        "seed": 314,
        "provider": "ibm_runtime",
        "backend": "PREREGISTERED_IBM_BACKEND_TO_BE_SELECTED",
        "family": PRODUCT_STATE_CIRCUIT_FAMILY,
        "shots": 4096,
        "rows": 16,
    },
    {
        "lane_id": "ibm_cx_seed314_rows16_shots4096",
        "seed": 314,
        "provider": "ibm_runtime",
        "backend": "PREREGISTERED_IBM_BACKEND_TO_BE_SELECTED",
        "family": ENTANGLING_CX_CIRCUIT_FAMILY,
        "shots": 4096,
        "rows": 16,
    },
    {
        "lane_id": "ibm_product_seed577_rows16_shots4096",
        "seed": 577,
        "provider": "ibm_runtime",
        "backend": "PREREGISTERED_IBM_BACKEND_TO_BE_SELECTED",
        "family": PRODUCT_STATE_CIRCUIT_FAMILY,
        "shots": 4096,
        "rows": 16,
    },
    {
        "lane_id": "ibm_cx_seed577_rows16_shots4096",
        "seed": 577,
        "provider": "ibm_runtime",
        "backend": "PREREGISTERED_IBM_BACKEND_TO_BE_SELECTED",
        "family": ENTANGLING_CX_CIRCUIT_FAMILY,
        "shots": 4096,
        "rows": 16,
    },
    {
        "lane_id": "braket_product_seed2718_rows8_shots1000",
        "seed": 2718,
        "provider": "amazon_braket",
        "backend": "arn:aws:braket:REGION::device/qpu/PROVIDER/DEVICE_TO_BE_SELECTED",
        "family": PRODUCT_STATE_CIRCUIT_FAMILY,
        "shots": 1000,
        "rows": 8,
    },
    {
        "lane_id": "braket_cx_seed2718_rows8_shots1000",
        "seed": 2718,
        "provider": "amazon_braket",
        "backend": "arn:aws:braket:REGION::device/qpu/PROVIDER/DEVICE_TO_BE_SELECTED",
        "family": ENTANGLING_CX_CIRCUIT_FAMILY,
        "shots": 1000,
        "rows": 8,
    },
)


def stable_hash(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _env_for_lane(lane: dict[str, Any]) -> dict[str, str]:
    env = {
        "QROPE_REAL_HARDWARE_PROVIDER": str(lane["provider"]),
        "QROPE_HARDWARE_BACKEND": str(lane["backend"]),
        "QROPE_HARDWARE_CIRCUIT_FAMILY": str(lane["family"]),
        "QROPE_HARDWARE_ROW_LIMIT": str(lane["rows"]),
        "QROPE_HARDWARE_SHOT_COUNT": str(lane["shots"]),
        "QROPE_HARDWARE_BUDGET_USD_CAP": "0",
        "QROPE_HARDWARE_ESTIMATED_COST_USD": "0",
        "QROPE_BRAKET_OUTPUT_S3_PREFIX": f"phasewrap-rope/preregistered/{lane['lane_id']}",
    }
    if lane["provider"] == "amazon_braket":
        env.update(
            {
                "QROPE_BRAKET_AWS_REGION": "REGION_TO_BE_SELECTED",
                "QROPE_BRAKET_OUTPUT_S3_BUCKET": "BUCKET_TO_BE_SELECTED",
            }
        )
    return env


def build_preregistered_packet(lane: dict[str, Any]) -> dict[str, Any]:
    bundle = generate_transformer_phase_wrap_attention_bundle(int(lane["seed"]))
    packet = freeze_hardware_packet(bundle.test[: int(lane["rows"])], _env_for_lane(lane))
    packet["frozen_at_utc"] = PREREGISTERED_TIMESTAMP
    row_set = {
        "seed": lane["seed"],
        "family": lane["family"],
        "shots": lane["shots"],
        "rows": [
            {
                "row_id": row["row_id"],
                "row_hash": row["row_hash"],
                "source": row["source"],
                "label": row["label"],
                "local_score": row["local_score"],
                "circuit_parameters": row["circuit_parameters"],
            }
            for row in packet["rows"]
        ],
    }
    packet["preregistration"] = {
        "lane_id": lane["lane_id"],
        "schema_version": SCHEMA_VERSION,
        "preregistered_at_utc": PREREGISTERED_TIMESTAMP,
        "row_set_hash": stable_hash(row_set),
        "execution_status": "not_submitted",
        "backend_policy": "Replace placeholder backend only at execution time, preserving row_set_hash, family, rows, and shots.",
        "claim_boundary": "Preregistered future replication packet; not hardware evidence until real execution artifacts are added.",
    }
    return packet


def build_manifest(output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, Any]:
    records = []
    for lane in LANES:
        packet = build_preregistered_packet(lane)
        packet_path = output_dir / f"{lane['lane_id']}.json"
        records.append(
            {
                "lane_id": lane["lane_id"],
                "seed": lane["seed"],
                "provider": lane["provider"],
                "backend_placeholder": lane["backend"],
                "family": lane["family"],
                "shots": lane["shots"],
                "rows": lane["rows"],
                "packet_path": str(packet_path.relative_to(REPO_ROOT).as_posix()),
                "packet_id": packet["packet_id"],
                "row_set_hash": packet["preregistration"]["row_set_hash"],
                "execution_status": "not_submitted",
            }
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "preregistered_at_utc": PREREGISTERED_TIMESTAMP,
        "purpose": "Freeze future Stage 4 replication row sets before additional hardware execution.",
        "no_hardware_submission": True,
        "records": records,
        "claim_boundary": {
            "supported": [
                "Future replication row sets, circuit families, row counts, and shot counts are fixed before execution.",
                "The artifact can be checked without provider credentials.",
            ],
            "excluded": [
                "new hardware evidence",
                "provider availability",
                "provider billing approval",
                "quantum advantage",
                "general cross-backend robustness",
            ],
        },
    }


def write_outputs(output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = build_manifest(output_dir)
    for lane in LANES:
        packet = build_preregistered_packet(lane)
        (output_dir / f"{lane['lane_id']}.json").write_text(
            json.dumps(packet, indent=2, sort_keys=True),
            encoding="utf-8",
        )
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    return {
        "manifest": str(output_dir / "manifest.json"),
        **{lane["lane_id"]: str(output_dir / f"{lane['lane_id']}.json") for lane in LANES},
    }


def print_summary(manifest: dict[str, Any]) -> None:
    headers = ("lane_id", "provider", "family", "shots", "rows", "row_set_hash", "execution_status")
    print(" | ".join(headers))
    print(" | ".join("---" for _ in headers))
    for row in manifest["records"]:
        print(" | ".join(str(row.get(header, "")) for header in headers))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Preregister Stage 4 replication packet row sets without submitting hardware.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args(argv)
    paths = write_outputs(args.output_dir)
    manifest = json.loads(Path(paths["manifest"]).read_text(encoding="utf-8"))
    print_summary(manifest)
    print(f"wrote {paths['manifest']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
