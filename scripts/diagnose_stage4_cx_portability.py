from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qrope.automated_stage_gates import (  # noqa: E402
    ENTANGLING_CX_CIRCUIT_FAMILY,
    circuit_label_from_signed_score,
    evaluate_hardware_execution,
    evaluate_prediction_values,
    ideal_counts_for_hardware_row,
)


DEFAULT_MANIFEST = (
    REPO_ROOT / "logs" / "automated_stage_gates" / "stage4_hardware_sweep" / "manifest.json"
)
DEFAULT_OUTPUT = (
    REPO_ROOT
    / "logs"
    / "automated_stage_gates"
    / "stage4_cx_portability_diagnostic"
    / "offline_diagnostic.json"
)
DIAGNOSTIC_VERSION = "qrope_stage4_cx_portability_diagnostic_v1"


BIT_ORDERS = {
    "q1q0_current": (1, 0),
    "q0q1_reversed": (0, 1),
}

WITNESS_SOURCES = (
    "z1_current_target",
    "z0_control_as_target",
    "neg_z1",
    "neg_z0",
    "zz_product",
    "neg_zz",
)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def resolve_path(raw_path: str) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        return path
    return REPO_ROOT / path


def display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def counts_to_expectations_for_bit_order(counts: dict[str, int], bit_order: tuple[int, int]) -> dict[str, Any]:
    shots = sum(int(value) for value in counts.values())
    if shots <= 0:
        return {"shots": 0, "z0": 0.0, "z1": 0.0, "zz": 0.0, "valid": False}
    q0_index, q1_index = bit_order
    z0_total = 0.0
    z1_total = 0.0
    zz_total = 0.0
    valid_shots = 0
    for raw_key, raw_count in counts.items():
        key = str(raw_key).replace(" ", "")
        if len(key) < 2:
            continue
        count = int(raw_count)
        z0 = 1.0 if key[q0_index] == "0" else -1.0
        z1 = 1.0 if key[q1_index] == "0" else -1.0
        z0_total += z0 * count
        z1_total += z1 * count
        zz_total += z0 * z1 * count
        valid_shots += count
    if valid_shots <= 0:
        return {"shots": shots, "z0": 0.0, "z1": 0.0, "zz": 0.0, "valid": False}
    return {
        "shots": shots,
        "z0": round(z0_total / valid_shots, 12),
        "z1": round(z1_total / valid_shots, 12),
        "zz": round(zz_total / valid_shots, 12),
        "valid": True,
    }


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def _witness_value(source: str, expectations: dict[str, Any]) -> float:
    if source == "z1_current_target":
        return expectations["z1"]
    if source == "z0_control_as_target":
        return expectations["z0"]
    if source == "neg_z1":
        return -expectations["z1"]
    if source == "neg_z0":
        return -expectations["z0"]
    if source == "zz_product":
        return expectations["zz"]
    if source == "neg_zz":
        return -expectations["zz"]
    raise ValueError(f"unsupported witness source: {source}")


def _counts_by_row(execution: dict[str, Any]) -> dict[str, dict[str, int]]:
    rows: dict[str, dict[str, int]] = {}
    for job in execution.get("jobs", []):
        for item in job.get("raw_counts_by_row", []):
            rows[str(item["row_id"])] = {str(k): int(v) for k, v in item.get("counts", {}).items()}
    return rows


def evaluate_cx_convention(
    packet: dict[str, Any],
    execution: dict[str, Any],
    *,
    bit_order: tuple[int, int],
    witness_source: str,
) -> dict[str, Any]:
    labels: list[float] = []
    witness_predictions: list[float] = []
    control_predictions: list[float] = []
    per_row: list[dict[str, Any]] = []
    counts_by_row = _counts_by_row(execution)
    for row in packet["rows"]:
        counts = counts_by_row.get(row["row_id"], {})
        expectations = counts_to_expectations_for_bit_order(counts, bit_order)
        labels.append(float(row["label"]))
        scale = float(row["circuit_parameters"]["score_scale"])
        witness_prediction = circuit_label_from_signed_score(scale * _witness_value(witness_source, expectations))
        control_prediction = _clamp(0.5 + 0.25 * (expectations["z0"] + expectations["zz"]))
        witness_predictions.append(witness_prediction)
        control_predictions.append(control_prediction)
        per_row.append(
            {
                "row_id": row["row_id"],
                "label": row["label"],
                "expectations": expectations,
                "hardware_predictions": {
                    "witness": round(witness_prediction, 12),
                    "control": round(control_prediction, 12),
                },
            }
        )
    witness = evaluate_prediction_values(labels, witness_predictions)
    control = evaluate_prediction_values(labels, control_predictions)
    gate_pass = witness["mae"] < control["mae"] and witness["rank_correlation"] > control["rank_correlation"]
    return {
        "witness": witness,
        "control": control,
        "gate_pass": gate_pass,
        "outcome": "hardware-positive-under-convention" if gate_pass else "hardware-negative-under-convention",
        "per_row_results": per_row,
    }


def evaluate_ideal_cx_packet(packet: dict[str, Any]) -> dict[str, Any]:
    execution = {
        "status": "COMPLETED",
        "jobs": [
            {
                "job_id": "ideal-counts-diagnostic",
                "provider": packet.get("provider"),
                "backend": "ideal_counts",
                "shot_count": packet.get("shot_count"),
                "raw_counts_by_row": [
                    {
                        "row_id": row["row_id"],
                        "counts": ideal_counts_for_hardware_row(row, int(packet.get("shot_count", 4096))),
                    }
                    for row in packet["rows"]
                ],
            }
        ],
        "backend_metadata": {"source": "ideal_counts_for_hardware_row"},
        "calibration_metadata": {"source": "offline_diagnostic"},
    }
    return evaluate_hardware_execution(packet, execution)


def diagnose_record(manifest_path: Path, record: dict[str, Any]) -> dict[str, Any]:
    packet = read_json(resolve_path(record["packet_path"]))
    execution = read_json(resolve_path(record["execution_path"]))
    recorded = read_json(resolve_path(record["evaluation_path"]))
    convention_results = []
    for bit_order_name, bit_order in BIT_ORDERS.items():
        for witness_source in WITNESS_SOURCES:
            result = evaluate_cx_convention(
                packet,
                execution,
                bit_order=bit_order,
                witness_source=witness_source,
            )
            convention_results.append(
                {
                    "bit_order": bit_order_name,
                    "witness_source": witness_source,
                    "witness": result["witness"],
                    "control": result["control"],
                    "gate_pass": result["gate_pass"],
                    "outcome": result["outcome"],
                }
            )
    recovered = [item for item in convention_results if item["gate_pass"]]
    best_by_mae = min(convention_results, key=lambda item: item["witness"]["mae"])
    best_by_rank = max(convention_results, key=lambda item: item["witness"]["rank_correlation"])
    generic_decoder_reference = next(
        item
        for item in convention_results
        if item["bit_order"] == "q1q0_current" and item["witness_source"] == "z1_current_target"
    )
    ideal = evaluate_ideal_cx_packet(packet)
    return {
        "record_id": record.get("record_id"),
        "provider": record.get("provider"),
        "backend": record.get("backend"),
        "backend_label": record.get("backend_label"),
        "artifact_dir": display_path(resolve_path(record["packet_path"]).parent),
        "recorded_outcome": recorded.get("outcome"),
        "recorded_status": recorded.get("status"),
        "recorded_witness": recorded.get("witness"),
        "recorded_control": recorded.get("control"),
        "historical_generic_decoder_reference": generic_decoder_reference,
        "ideal_counts_reference": {
            "outcome": ideal.get("outcome"),
            "gate_pass": ideal.get("gate_pass"),
            "witness": ideal.get("witness"),
            "control": ideal.get("control"),
        },
        "convention_results": convention_results,
        "recovered_positive_conventions": recovered,
        "best_by_witness_mae": best_by_mae,
        "best_by_witness_rank": best_by_rank,
        "diagnosis": {
            "bit_order_or_sign_flip_recovers_positive_gate": bool(recovered),
            "current_negative_is_convention_explained": bool(recovered),
        },
    }


def diagnose_manifest(manifest_path: Path) -> dict[str, Any]:
    manifest = read_json(manifest_path)
    records = [
        record
        for record in manifest.get("records", [])
        if record.get("family") == ENTANGLING_CX_CIRCUIT_FAMILY and record.get("status") == "completed"
    ]
    diagnostics = [diagnose_record(manifest_path, record) for record in records]
    braket_negative = [
        item
        for item in diagnostics
        if item.get("provider") == "amazon_braket"
        and item["historical_generic_decoder_reference"].get("outcome") == "hardware-negative-under-convention"
    ]
    recovered = [
        item
        for item in braket_negative
        if item["diagnosis"]["bit_order_or_sign_flip_recovers_positive_gate"]
    ]
    common_recovery = []
    if braket_negative:
        convention_sets = [
            {
                (item["bit_order"], item["witness_source"])
                for item in record["recovered_positive_conventions"]
            }
            for record in braket_negative
        ]
        common_recovery = sorted(set.intersection(*convention_sets)) if convention_sets else []
    conclusion = (
        "No tested bit-order, target-qubit, sign, or ZZ-parity reinterpretation recovers the Braket CX "
        "negative records as positive. The current evidence is therefore not explained by a simple "
        "classical decoding convention mismatch."
        if braket_negative and not recovered
        else (
            "All historical generic-decoder Braket CX negative records recover under a common q0q1 bitstring interpretation with "
            "the original Z1-after-CX target witness. This points to a provider bitstring-order decoding "
            "mismatch rather than a physical CX portability failure."
            if len(recovered) == len(braket_negative) and ("q0q1_reversed", "z1_current_target") in common_recovery
            else "At least one Braket CX negative record has a convention reinterpretation that passes the gate; inspect recovered_positive_conventions before treating it as a backend failure."
        )
    )
    return {
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "manifest_path": display_path(manifest_path),
        "records": diagnostics,
        "summary": {
            "cx_completed_records": len(diagnostics),
            "braket_negative_records": len(braket_negative),
            "braket_negative_records_recovered_by_convention": len(recovered),
            "common_recovered_positive_conventions": [
                {"bit_order": bit_order, "witness_source": witness_source}
                for bit_order, witness_source in common_recovery
            ],
            "conclusion": conclusion,
            "next_questions": [
                "Provider-aware bitstring order is now explicit in the sweep manifest.",
                "The sweep verifier now recomputes Amazon Braket records with q0q1 decoding and preserves the generic-decoder diagnostic separately.",
                "If portability questions remain, compare logical CX against native CZ or XX-family witness circuits in a new dated evidence packet.",
            ],
        },
    }


def print_summary(report: dict[str, Any]) -> None:
    print("backend | current_recorded | generic_q1q0 | recovered_by_convention | best_witness_mae | best_witness_rank")
    print("--- | --- | --- | --- | --- | ---")
    for record in report["records"]:
        print(
            " | ".join(
                [
                    str(record.get("backend_label") or record.get("backend")),
                    str(record.get("recorded_outcome")),
                    str(record["historical_generic_decoder_reference"].get("outcome")),
                    str(record["diagnosis"]["bit_order_or_sign_flip_recovers_positive_gate"]),
                    str(record["best_by_witness_mae"]["witness"]["mae"]),
                    str(record["best_by_witness_rank"]["witness"]["rank_correlation"]),
                ]
            )
        )
    print(json.dumps(report["summary"], indent=2))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Diagnose Stage 4 CX portability failures from saved raw counts.")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    report = diagnose_manifest(args.manifest)
    write_json(args.output, report)
    print_summary(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
