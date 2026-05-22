from __future__ import annotations

import csv
import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any


STAGE99_SCHEMA_VERSION = "qrope_stage99_matched_fixed_width_encoding_packet_freezer_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_SOURCE_PACKET_DIR = DEFAULT_ARTIFACT_ROOT / "stage4_preregistered_replication_packets"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage99_matched_fixed_width_encoding_packets"
DEFAULT_SOURCE_PACKET_FILES: tuple[str, ...] = (
    "ibm_product_seed314_rows16_shots4096.json",
    "ibm_product_seed577_rows16_shots4096.json",
    "braket_product_seed2718_rows8_shots1000.json",
)
ENCODING_FAMILIES: tuple[str, ...] = (
    "phasewrap",
    "rope_like",
    "sinusoidal_like",
    "alibi_like",
    "no_position_control",
)
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)


@dataclass(frozen=True)
class SourceLane:
    path: Path
    payload: dict[str, Any]

    @property
    def lane_id(self) -> str:
        return str(self.payload.get("preregistration", {}).get("lane_id", self.path.stem))


def _stable_hash(payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _clamp(value: float, low: float = -1.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def _round_float(value: float) -> float:
    return round(float(value), 12)


def _cos_component(delta: float, period: float) -> float:
    return _clamp(math.cos(2.0 * math.pi * delta / period))


def _row_delta(row: dict[str, Any]) -> float:
    source = row.get("source", {})
    return float(source["reference_delta"]) - float(source["candidate_delta"])


def _max_abs_delta(rows: list[dict[str, Any]]) -> float:
    return max(1.0, max(abs(_row_delta(row)) for row in rows))


def _components_for_family(family: str, delta: float, max_abs_delta: float) -> tuple[float, float]:
    if family == "phasewrap":
        return _cos_component(delta, 8.0), _cos_component(delta, 12.0)
    if family == "rope_like":
        return _cos_component(delta, 32.0), _cos_component(delta, 64.0)
    if family == "sinusoidal_like":
        return _cos_component(delta, 4.0), _cos_component(delta, 16.0)
    if family == "alibi_like":
        component = _clamp(1.0 - 2.0 * abs(delta) / max_abs_delta)
        return component, component
    if family == "no_position_control":
        return 0.0, 0.0
    raise ValueError(f"Unknown encoding family: {family}")


def _load_source_lanes(source_packet_paths: list[Path]) -> tuple[list[SourceLane], list[str]]:
    lanes: list[SourceLane] = []
    missing: list[str] = []
    for path in source_packet_paths:
        if not path.exists():
            missing.append(str(path.as_posix()))
            continue
        lanes.append(SourceLane(path=path, payload=json.loads(path.read_text(encoding="utf-8"))))
    return lanes, missing


def _matched_row(source_row: dict[str, Any], family: str, max_abs_delta: float) -> dict[str, Any]:
    delta = _row_delta(source_row)
    component_a, component_b = _components_for_family(family, delta, max_abs_delta)
    ry_q0 = math.acos(_clamp(component_a))
    ry_q1 = math.acos(_clamp(component_b))
    target_score = _clamp(0.5 + 0.25 * (component_a + component_b), 0.0, 1.0)
    row_core = {
        "row_id": source_row["row_id"],
        "source_row_hash": source_row.get("row_hash"),
        "encoding_family": family,
        "source": source_row.get("source", {}),
        "delta": _round_float(delta),
        "components": {
            "component_a": _round_float(component_a),
            "component_b": _round_float(component_b),
        },
        "circuit_parameters": {
            "template": "two_ry_product_state_z_readout_v1",
            "ry_q0": _round_float(ry_q0),
            "ry_q1": _round_float(ry_q1),
            "z0_target": _round_float(component_a),
            "z1_target": _round_float(component_b),
        },
        "ideal_predictions": {
            "score": _round_float(target_score),
            "observable": "0.5 + 0.25 * (E[Z0] + E[Z1])",
        },
    }
    return {
        **row_core,
        "row_hash": _stable_hash(row_core),
    }


def _packet_for_lane_family(lane: SourceLane, family: str) -> dict[str, Any]:
    rows = list(lane.payload.get("rows", []))
    max_delta = _max_abs_delta(rows)
    matched_rows = [_matched_row(row, family, max_delta) for row in rows]
    packet_core = {
        "schema_version": STAGE99_SCHEMA_VERSION,
        "packet_version": "qrope_stage99_matched_fixed_width_encoding_packet_v1",
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
            "circuit_template": "two_ry_product_state_z_readout_v1",
            "entangling_gate": None,
            "score_observable": "0.5 + 0.25 * (E[Z0] + E[Z1])",
        },
        "matching_policy": {
            "row_set": "identical source rows across encoding families within each lane",
            "qubit_count": "fixed at two measured qubits",
            "depth_family": "two single-qubit RY preparations plus computational-basis measurement",
            "hardware_scope": "packet freeze only; not hardware evidence",
        },
        "claim_boundary": (
            "Matched fixed-width score-encoding packet; supports future noisy-hardware comparison setup only, "
            "not a hardware robustness result."
        ),
        "rows": matched_rows,
    }
    return {
        **packet_core,
        "packet_hash": _stable_hash(packet_core),
    }


def _source_packet_paths(source_packet_dir: Path, source_packet_files: tuple[str, ...]) -> list[Path]:
    return [source_packet_dir / file_name for file_name in source_packet_files]


def run_stage99_freezer(
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
        "schema_version": STAGE99_SCHEMA_VERSION,
        "stage": "stage99_matched_fixed_width_encoding_packet_freezer",
        "status": "completed" if complete else "incomplete",
        "objective": OBJECTIVE,
        "decision": (
            "MATCHED_FIXED_WIDTH_ENCODING_PACKETS_FROZEN_NO_HARDWARE"
            if complete
            else "MATCHED_FIXED_WIDTH_ENCODING_PACKET_FREEZE_INCOMPLETE"
        ),
        "source_stage": "stage4_preregistered_replication_packets",
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
            "circuit_template": "two_ry_product_state_z_readout_v1",
            "score_observable": "0.5 + 0.25 * (E[Z0] + E[Z1])",
        },
        "packet_records": packet_records,
        "packets": packets,
        "claim_boundary": {
            "supported": [
                "matched no-hardware packet freeze for five two-qubit positional-score encoding families",
                "identical row sets within each source lane across PhaseWrap, RoPE-like, sinusoidal-like, ALIBI-like, and no-position/control encodings",
                "a fixed-width product-state score readout template for future noisy-hardware execution planning",
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
            "review whether the product-state template is sufficient or whether a matched CX witness variant is also required",
            "run known-state bitstring calibration counts per provider/backend/date",
            "execute matched packets under fixed shot budgets only after calibration evidence is present",
            "repeat selected packets across independent backend calibration windows before claiming robustness beyond recorded contexts",
        ],
    }


def write_stage99_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
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


def print_stage99_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"lane_count: {result['lane_count']}")
    print(f"packet_count: {result['packet_count']}")
    print("remaining_requirements:")
    for requirement in result["remaining_requirements"]:
        print(f"- {requirement}")
