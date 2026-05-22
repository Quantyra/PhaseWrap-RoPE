from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from qrope.stage99_matched_fixed_width_encoding_packet_freezer import (
    ENCODING_FAMILIES,
    OBJECTIVE,
    STAGE99_SCHEMA_VERSION,
    SourceLane,
    _load_source_lanes,
    _matched_row,
    _max_abs_delta,
    _source_packet_paths,
    _stable_hash,
)


STAGE100_SCHEMA_VERSION = "qrope_stage100_matched_cx_encoding_packet_freezer_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_SOURCE_PACKET_DIR = DEFAULT_ARTIFACT_ROOT / "stage4_preregistered_replication_packets"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage100_matched_cx_encoding_packets"
DEFAULT_SOURCE_PACKET_FILES: tuple[str, ...] = (
    "ibm_cx_seed314_rows16_shots4096.json",
    "braket_cx_seed2718_rows8_shots1000.json",
)


def _openqasm3(row: dict[str, Any]) -> str:
    params = row["circuit_parameters"]
    return "\n".join(
        [
            "OPENQASM 3.0;",
            "qubit[2] q;",
            "bit[2] c;",
            f"ry({params['ry_q0']}) q[0];",
            f"ry({params['ry_q1']}) q[1];",
            "cnot q[0], q[1];",
            "c[0] = measure q[0];",
            "c[1] = measure q[1];",
            "",
        ]
    )


def _cx_matched_row(source_row: dict[str, Any], family: str, max_abs_delta: float) -> dict[str, Any]:
    row = _matched_row(source_row, family, max_abs_delta)
    row["circuit_parameters"] = {
        **row["circuit_parameters"],
        "template": "two_ry_cx_parity_z_readout_v1",
        "entangling_gate": "cx q0->q1",
    }
    row["ideal_predictions"] = {
        **row["ideal_predictions"],
        "observable": "0.5 + 0.25 * (E[Z0 after CX] + E[Z0 Z1 after CX])",
        "readout_note": "Under ideal CNOT readout, E[Z0 after CX] recovers component_a and E[Z0 Z1 after CX] recovers component_b.",
    }
    core = {key: value for key, value in row.items() if key != "row_hash"}
    row["row_hash"] = _stable_hash(core)
    row["openqasm3"] = _openqasm3(row)
    return row


def _packet_for_lane_family(lane: SourceLane, family: str) -> dict[str, Any]:
    rows = list(lane.payload.get("rows", []))
    max_delta = _max_abs_delta(rows)
    matched_rows = [_cx_matched_row(row, family, max_delta) for row in rows]
    packet_core = {
        "schema_version": STAGE100_SCHEMA_VERSION,
        "packet_version": "qrope_stage100_matched_cx_encoding_packet_v1",
        "packet_id": f"{lane.lane_id}__{family}",
        "source_stage": "stage4_preregistered_replication_packets",
        "source_packet_path": str(lane.path.as_posix()),
        "source_lane_id": lane.lane_id,
        "source_row_set_hash": lane.payload.get("preregistration", {}).get("row_set_hash"),
        "encoding_family": family,
        "provider": lane.payload.get("provider"),
        "backend": lane.payload.get("backend"),
        "row_count": len(matched_rows),
        "shot_count": lane.payload.get("config", {}).get("shot_count", lane.payload.get("shot_count")),
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "execution_status": "not_submitted",
        "fixed_width": {
            "measured_qubits": 2,
            "active_qubits": 2,
            "readout": "computational_basis",
            "circuit_template": "two_ry_cx_parity_z_readout_v1",
            "entangling_gate": "cx q0->q1",
            "score_observable": "0.5 + 0.25 * (E[Z0 after CX] + E[Z0 Z1 after CX])",
        },
        "matching_policy": {
            "row_set": "identical source rows across encoding families within each CX lane",
            "qubit_count": "fixed at two measured qubits",
            "depth_family": "two single-qubit RY preparations, one CNOT, computational-basis measurement",
            "hardware_scope": "packet freeze only; not hardware evidence",
            "product_state_pair": "Stage 99 freezes the matching no-entangling product-state packets.",
        },
        "claim_boundary": (
            "Matched fixed-width CX/parity score-encoding packet; supports future noisy-hardware comparison setup only, "
            "not a hardware robustness result."
        ),
        "rows": matched_rows,
    }
    return {
        **packet_core,
        "packet_hash": _stable_hash(packet_core),
    }


def run_stage100_freezer(
    *,
    source_packet_dir: Path = DEFAULT_SOURCE_PACKET_DIR,
    source_packet_files: tuple[str, ...] = DEFAULT_SOURCE_PACKET_FILES,
) -> dict[str, Any]:
    source_paths = _source_packet_paths(source_packet_dir, source_packet_files)
    lanes, missing = _load_source_lanes(source_paths)
    packets: list[dict[str, Any]] = []
    for lane in lanes:
        for family in ENCODING_FAMILIES:
            packets.append(_packet_for_lane_family(lane, family))

    packet_records = [
        {
            "packet_id": packet["packet_id"],
            "encoding_family": packet["encoding_family"],
            "source_lane_id": packet["source_lane_id"],
            "provider": packet["provider"],
            "row_count": packet["row_count"],
            "shot_count": packet["shot_count"],
            "packet_hash": packet["packet_hash"],
        }
        for packet in packets
    ]
    expected_packet_count = len(lanes) * len(ENCODING_FAMILIES)
    complete = bool(lanes) and len(packets) == expected_packet_count and not missing
    return {
        "schema_version": STAGE100_SCHEMA_VERSION,
        "stage": "stage100_matched_cx_encoding_packet_freezer",
        "status": "completed" if complete else "incomplete",
        "objective": OBJECTIVE,
        "decision": (
            "MATCHED_CX_ENCODING_PACKETS_FROZEN_NO_HARDWARE"
            if complete
            else "MATCHED_CX_ENCODING_PACKET_FREEZE_INCOMPLETE"
        ),
        "source_stage": "stage4_preregistered_replication_packets",
        "paired_product_packet_schema": STAGE99_SCHEMA_VERSION,
        "source_packet_paths": [str(path.as_posix()) for path in source_paths],
        "missing_source_packets": missing,
        "matched_encoding_families": list(ENCODING_FAMILIES),
        "lane_count": len(lanes),
        "packet_count": len(packets),
        "expected_packet_count": expected_packet_count,
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "fixed_width_policy": {
            "measured_qubits": 2,
            "active_qubits": 2,
            "readout": "computational_basis",
            "circuit_template": "two_ry_cx_parity_z_readout_v1",
            "entangling_gate": "cx q0->q1",
            "score_observable": "0.5 + 0.25 * (E[Z0 after CX] + E[Z0 Z1 after CX])",
        },
        "packet_records": packet_records,
        "packets": packets,
        "claim_boundary": {
            "supported": [
                "matched no-hardware packet freeze for five two-qubit CX/parity positional-score encoding families",
                "identical CX-lane row sets across PhaseWrap, RoPE-like, sinusoidal-like, ALIBI-like, and no-position/control encodings",
                "a fixed-width entangling score readout template paired with the Stage 99 product-state packet family",
            ],
            "excluded": [
                "a noisy-hardware robustness result",
                "a claim that PhaseWrap-RoPE outperforms RoPE on hardware",
                "a transformer-performance claim",
                "provider bitstring-order validation",
                "independent backend/date/calibration robustness",
            ],
        },
        "remaining_requirements": [
            "run known-state bitstring calibration counts per provider/backend/date",
            "execute Stage 99 product-state and Stage 100 CX/parity matched packets under fixed shot budgets only after calibration evidence is present",
            "compare readout error, rank retention, score distortion, and auditability metrics against the no-position/control family",
            "repeat selected packets across independent backend calibration windows before claiming robustness beyond recorded contexts",
        ],
    }


def write_stage100_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    packet_dir = output_dir / "packets"
    packet_dir.mkdir(parents=True, exist_ok=True)

    packet_paths: list[str] = []
    for packet in result["packets"]:
        path = packet_dir / f"{packet['packet_id']}.json"
        path.write_text(json.dumps(packet, indent=2, sort_keys=True), encoding="utf-8")
        packet_paths.append(str(path.as_posix()))

    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_stage": result["source_stage"],
        "paired_product_packet_schema": result["paired_product_packet_schema"],
        "source_packet_paths": result["source_packet_paths"],
        "missing_source_packets": result["missing_source_packets"],
        "matched_encoding_families": result["matched_encoding_families"],
        "lane_count": result["lane_count"],
        "packet_count": result["packet_count"],
        "expected_packet_count": result["expected_packet_count"],
        "no_hardware_submission": result["no_hardware_submission"],
        "provider_credentials_required": result["provider_credentials_required"],
        "fixed_width_policy": result["fixed_width_policy"],
        "packet_paths": packet_paths,
        "result_path": str((output_dir / "results.json").as_posix()),
        "summary_csv_path": str((output_dir / "summary.csv").as_posix()),
        "claim_boundary": result["claim_boundary"],
        "remaining_requirements": result["remaining_requirements"],
    }
    paths = {
        "manifest": str(output_dir / "manifest.json"),
        "result": str(output_dir / "results.json"),
        "summary_csv": str(output_dir / "summary.csv"),
        "packet_dir": str(packet_dir),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=("packet_id", "encoding_family", "source_lane_id", "provider", "row_count", "shot_count", "packet_hash"),
        )
        writer.writeheader()
        writer.writerows(result["packet_records"])
    return paths


def print_stage100_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"lane_count: {result['lane_count']}")
    print(f"packet_count: {result['packet_count']}")
    print("remaining_requirements:")
    for requirement in result["remaining_requirements"]:
        print(f"- {requirement}")
