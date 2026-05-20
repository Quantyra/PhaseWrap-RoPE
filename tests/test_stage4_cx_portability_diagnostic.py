from __future__ import annotations

import json
from pathlib import Path

from qrope.automated_stage_gates import (
    ENTANGLING_CX_CIRCUIT_FAMILY,
    evaluate_hardware_execution,
    freeze_hardware_packet,
    generate_transformer_phase_wrap_attention_bundle,
    ideal_counts_for_hardware_row,
)
from scripts.diagnose_stage4_cx_portability import (
    counts_to_expectations_for_bit_order,
    diagnose_manifest,
    evaluate_cx_convention,
)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def test_bit_order_expectation_decoder_distinguishes_q1q0_from_q0q1() -> None:
    counts = {"01": 10}
    assert counts_to_expectations_for_bit_order(counts, (1, 0))["z0"] == -1.0
    assert counts_to_expectations_for_bit_order(counts, (1, 0))["z1"] == 1.0
    assert counts_to_expectations_for_bit_order(counts, (0, 1))["z0"] == 1.0
    assert counts_to_expectations_for_bit_order(counts, (0, 1))["z1"] == -1.0


def test_cx_convention_diagnostic_matches_standard_ideal_counts() -> None:
    bundle = generate_transformer_phase_wrap_attention_bundle(42)
    packet = freeze_hardware_packet(
        bundle.test,
        {
            "QROPE_REAL_HARDWARE_PROVIDER": "amazon_braket",
            "QROPE_BRAKET_DEVICE_ARN": "arn:aws:braket:us-west-1::device/qpu/rigetti/Cepheus-1-108Q",
            "QROPE_BRAKET_AWS_PROFILE": "synthetic",
            "QROPE_BRAKET_OUTPUT_S3_BUCKET": "amazon-braket-synthetic",
            "QROPE_HARDWARE_CIRCUIT_FAMILY": ENTANGLING_CX_CIRCUIT_FAMILY,
            "QROPE_HARDWARE_ROW_LIMIT": "4",
            "QROPE_HARDWARE_SHOT_COUNT": "256",
            "QROPE_HARDWARE_BUDGET_USD_CAP": "1",
            "QROPE_BRAKET_ESTIMATED_COST_USD": "0",
        },
    )
    execution = {
        "status": "COMPLETED",
        "jobs": [
            {
                "job_id": "synthetic-cx",
                "provider": packet["provider"],
                "backend": packet["backend"],
                "shot_count": packet["shot_count"],
                "raw_counts_by_row": [
                    {"row_id": row["row_id"], "counts": ideal_counts_for_hardware_row(row, packet["shot_count"])}
                    for row in packet["rows"]
                ],
            }
        ],
        "backend_metadata": {"fixture": True},
        "calibration_metadata": {"fixture": True},
    }
    standard = evaluate_hardware_execution(packet, execution)
    diagnostic = evaluate_cx_convention(
        packet,
        execution,
        bit_order=(1, 0),
        witness_source="z1_current_target",
    )
    assert diagnostic["witness"] == standard["witness"]
    assert diagnostic["control"] == standard["control"]
    assert diagnostic["gate_pass"] is True


def test_manifest_diagnostic_reports_unrecovered_negative_record(tmp_path: Path) -> None:
    bundle = generate_transformer_phase_wrap_attention_bundle(42)
    packet = freeze_hardware_packet(
        bundle.test,
        {
            "QROPE_REAL_HARDWARE_PROVIDER": "amazon_braket",
            "QROPE_BRAKET_DEVICE_ARN": "arn:aws:braket:us-west-1::device/qpu/rigetti/Cepheus-1-108Q",
            "QROPE_BRAKET_AWS_PROFILE": "synthetic",
            "QROPE_BRAKET_OUTPUT_S3_BUCKET": "amazon-braket-synthetic",
            "QROPE_HARDWARE_CIRCUIT_FAMILY": ENTANGLING_CX_CIRCUIT_FAMILY,
            "QROPE_HARDWARE_ROW_LIMIT": "4",
            "QROPE_HARDWARE_SHOT_COUNT": "256",
            "QROPE_HARDWARE_BUDGET_USD_CAP": "1",
            "QROPE_BRAKET_ESTIMATED_COST_USD": "0",
        },
    )
    execution = {
        "status": "COMPLETED",
        "jobs": [
            {
                "job_id": "synthetic-negative",
                "provider": packet["provider"],
                "backend": packet["backend"],
                "shot_count": packet["shot_count"],
                "raw_counts_by_row": [
                    {"row_id": row["row_id"], "counts": {"00": 64, "01": 64, "10": 64, "11": 64}}
                    for row in packet["rows"]
                ],
            }
        ],
        "backend_metadata": {"fixture": True},
        "calibration_metadata": {"fixture": True},
    }
    evaluation = evaluate_hardware_execution(packet, execution)
    result_dir = tmp_path / "negative"
    _write_json(result_dir / "frozen_packet.json", packet)
    _write_json(result_dir / "execution.json", execution)
    _write_json(result_dir / "evaluation.json", evaluation)
    _write_json(result_dir / "summary.json", {"status": evaluation["status"], "outcome": evaluation["outcome"]})
    manifest = {
        "records": [
            {
                "record_id": "synthetic_negative",
                "provider": "amazon_braket",
                "backend": packet["backend"],
                "backend_label": "Synthetic Braket",
                "family": ENTANGLING_CX_CIRCUIT_FAMILY,
                "status": "completed",
                "packet_path": str(result_dir / "frozen_packet.json"),
                "execution_path": str(result_dir / "execution.json"),
                "evaluation_path": str(result_dir / "evaluation.json"),
                "summary_path": str(result_dir / "summary.json"),
            }
        ]
    }
    manifest_path = tmp_path / "manifest.json"
    _write_json(manifest_path, manifest)
    report = diagnose_manifest(manifest_path)
    assert report["summary"]["braket_negative_records"] == 1
    assert report["summary"]["braket_negative_records_recovered_by_convention"] == 0


def test_manifest_diagnostic_reports_common_braket_recovery_convention(tmp_path: Path) -> None:
    bundle = generate_transformer_phase_wrap_attention_bundle(42)
    packet = freeze_hardware_packet(
        bundle.test,
        {
            "QROPE_REAL_HARDWARE_PROVIDER": "amazon_braket",
            "QROPE_BRAKET_DEVICE_ARN": "arn:aws:braket:us-west-1::device/qpu/rigetti/Cepheus-1-108Q",
            "QROPE_BRAKET_AWS_PROFILE": "synthetic",
            "QROPE_BRAKET_OUTPUT_S3_BUCKET": "amazon-braket-synthetic",
            "QROPE_HARDWARE_CIRCUIT_FAMILY": ENTANGLING_CX_CIRCUIT_FAMILY,
            "QROPE_HARDWARE_ROW_LIMIT": "4",
            "QROPE_HARDWARE_SHOT_COUNT": "256",
            "QROPE_HARDWARE_BUDGET_USD_CAP": "1",
            "QROPE_BRAKET_ESTIMATED_COST_USD": "0",
        },
    )
    q1q0_counts = [ideal_counts_for_hardware_row(row, packet["shot_count"]) for row in packet["rows"]]
    # Simulate Braket returning the same physical samples as q0q1 strings.
    q0q1_counts = [
        {key[::-1]: value for key, value in counts.items()}
        for counts in q1q0_counts
    ]
    execution = {
        "status": "COMPLETED",
        "jobs": [
            {
                "job_id": "synthetic-braket-q0q1",
                "provider": packet["provider"],
                "backend": packet["backend"],
                "shot_count": packet["shot_count"],
                "raw_counts_by_row": [
                    {"row_id": row["row_id"], "counts": counts}
                    for row, counts in zip(packet["rows"], q0q1_counts)
                ],
            }
        ],
        "backend_metadata": {"fixture": True},
        "calibration_metadata": {"fixture": True},
    }
    evaluation = evaluate_hardware_execution(packet, execution)
    assert evaluation["outcome"] == "hardware-negative"
    result_dir = tmp_path / "braket_q0q1"
    _write_json(result_dir / "frozen_packet.json", packet)
    _write_json(result_dir / "execution.json", execution)
    _write_json(result_dir / "evaluation.json", evaluation)
    _write_json(result_dir / "summary.json", {"status": evaluation["status"], "outcome": evaluation["outcome"]})
    manifest = {
        "records": [
            {
                "record_id": "synthetic_braket_q0q1",
                "provider": "amazon_braket",
                "backend": packet["backend"],
                "backend_label": "Synthetic Braket",
                "family": ENTANGLING_CX_CIRCUIT_FAMILY,
                "status": "completed",
                "packet_path": str(result_dir / "frozen_packet.json"),
                "execution_path": str(result_dir / "execution.json"),
                "evaluation_path": str(result_dir / "evaluation.json"),
                "summary_path": str(result_dir / "summary.json"),
            }
        ]
    }
    manifest_path = tmp_path / "manifest.json"
    _write_json(manifest_path, manifest)
    report = diagnose_manifest(manifest_path)
    assert report["summary"]["braket_negative_records_recovered_by_convention"] == 1
    assert {
        "bit_order": "q0q1_reversed",
        "witness_source": "z1_current_target",
    } in report["summary"]["common_recovered_positive_conventions"]
