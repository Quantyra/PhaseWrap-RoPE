from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DIR = REPO_ROOT / "logs" / "automated_stage_gates" / "stage4_bitstring_calibration"
DEFAULT_MANIFEST = DEFAULT_DIR / "manifest.json"
DEFAULT_OUTPUT = DEFAULT_DIR / "offline_verification.json"
SCHEMA_VERSION = "qrope_stage4_bitstring_calibration_manifest_v1"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _dominant_key(counts: dict[str, int]) -> str | None:
    if not counts:
        return None
    return max(((str(key), int(value)) for key, value in counts.items()), key=lambda item: (item[1], item[0]))[0]


def verify_execution(packet: dict[str, Any], execution: dict[str, Any]) -> list[dict[str, Any]]:
    counts_by_state = {
        str(item.get("state")): {str(key): int(value) for key, value in item.get("counts", {}).items()}
        for item in execution.get("raw_counts_by_state", [])
    }
    checks = []
    for state in packet.get("states", []):
        prepared = str(state["state"])
        expected_key = str(state["expected_dominant_key"])
        dominant = _dominant_key(counts_by_state.get(prepared, {}))
        checks.append(
            {
                "state": prepared,
                "expected_dominant_key": expected_key,
                "dominant_key": dominant,
                "pass": dominant == expected_key,
            }
        )
    return checks


def verify_manifest(manifest_path: Path = DEFAULT_MANIFEST) -> dict[str, Any]:
    manifest = read_json(manifest_path)
    base_dir = manifest_path.parent
    records = []
    for record in manifest.get("records", []):
        base = {
            "record_id": record.get("record_id"),
            "provider": record.get("provider"),
            "expected_bitstring_order": record.get("expected_bitstring_order"),
            "status": record.get("status"),
        }
        if record.get("status") != "completed":
            records.append(
                {
                    **base,
                    "pass": False,
                    "outcome": "missing-evidence",
                    "missing_evidence": record.get("missing_evidence", []),
                }
            )
            continue
        packet_path = Path(str(record["packet_path"]))
        execution_path = Path(str(record["execution_path"]))
        if not packet_path.is_absolute():
            packet_path = REPO_ROOT / packet_path
            if not packet_path.exists():
                packet_path = base_dir / str(record["packet_path"])
        if not execution_path.is_absolute():
            execution_path = REPO_ROOT / execution_path
            if not execution_path.exists():
                execution_path = base_dir / str(record["execution_path"])
        packet = read_json(packet_path)
        execution = read_json(execution_path)
        checks = verify_execution(packet, execution)
        records.append({**base, "pass": all(check["pass"] for check in checks), "outcome": "calibration-verified", "checks": checks})
    return {
        "schema_version": manifest.get("schema_version"),
        "verifier": "qrope_stage4_bitstring_calibration_offline_verifier_v1",
        "records": records,
        "missing_evidence": [record for record in records if record["outcome"] == "missing-evidence"],
        "pass": manifest.get("schema_version") == SCHEMA_VERSION and bool(records) and all(record["pass"] for record in records),
        "claim_boundary": manifest.get("claim_boundary"),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify Stage 4 provider bitstring known-state calibration artifacts.")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    result = verify_manifest(args.manifest)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"pass": result["pass"], "records": len(result["records"]), "missing_evidence": len(result["missing_evidence"])}, indent=2))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
