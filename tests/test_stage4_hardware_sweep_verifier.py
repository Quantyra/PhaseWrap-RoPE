from __future__ import annotations

import json
from pathlib import Path

from qrope.automated_stage_gates import (
    ENTANGLING_CX_CIRCUIT_FAMILY,
    PRODUCT_STATE_CIRCUIT_FAMILY,
    evaluate_hardware_execution,
    freeze_hardware_packet,
    generate_transformer_phase_wrap_attention_bundle,
    ideal_counts_for_hardware_row,
)
from scripts.verify_stage4_hardware_sweep import (
    MANIFEST_SCHEMA_VERSION,
    mean_absolute_error,
    rank_correlation,
    raw_counts_to_expectations,
    scan_public_docs_for_overclaims,
    validate_manifest,
    verify_manifest,
)


SYNTHETIC_NOTICE = "synthetic verifier fixture; not real Stage 4 evidence"


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _synthetic_result(tmp_path: Path, family: str = PRODUCT_STATE_CIRCUIT_FAMILY) -> tuple[Path, dict]:
    env = {
        "QROPE_REAL_HARDWARE_PROVIDER": "ibm_runtime",
        "QROPE_HARDWARE_BACKEND": "synthetic_backend",
        "QROPE_HARDWARE_CIRCUIT_FAMILY": family,
        "QROPE_HARDWARE_ROW_LIMIT": "4",
        "QROPE_HARDWARE_SHOT_COUNT": "256",
        "QROPE_HARDWARE_BUDGET_USD_CAP": "1",
        "QROPE_HARDWARE_ESTIMATED_COST_USD": "0",
        "IBM_QUANTUM_TOKEN": "synthetic-token",
    }
    bundle = generate_transformer_phase_wrap_attention_bundle(42)
    packet = freeze_hardware_packet(bundle.test[:4], env)
    execution = {
        "status": "COMPLETED",
        "jobs": [
            {
                "job_id": "synthetic-job-1",
                "provider": packet["provider"],
                "backend": packet["backend"],
                "shot_count": packet["shot_count"],
                "submitted_at_utc": "2026-01-01T00:00:00Z",
                "completed_at_utc": "2026-01-01T00:01:00Z",
                "raw_counts_by_row": [
                    {
                        "row_id": row["row_id"],
                        "counts": ideal_counts_for_hardware_row(row, packet["shot_count"]),
                    }
                    for row in packet["rows"]
                ],
            }
        ],
        "backend_metadata": {"provider": packet["provider"], "backend": packet["backend"]},
        "calibration_metadata": {"captured_at_utc": "2026-01-01T00:01:00Z", "fixture": SYNTHETIC_NOTICE},
    }
    evaluation = evaluate_hardware_execution(packet, execution)
    result_dir = tmp_path / family
    _write_json(result_dir / "frozen_packet.json", packet)
    _write_json(result_dir / "execution.json", execution)
    _write_json(result_dir / "evaluation.json", evaluation)
    _write_json(result_dir / "summary.json", {"status": evaluation["status"], "outcome": evaluation["outcome"], "gate_pass": evaluation["gate_pass"]})
    record = {
        "record_id": f"synthetic__{family}",
        "provider": packet["provider"],
        "backend": packet["backend"],
        "backend_label": "Synthetic Backend",
        "family": family,
        "status": "completed",
        "shots": packet["shot_count"],
        "row_count": packet["row_count"],
        "bitstring_order": "q1q0",
        "job_ids": ["synthetic-job-1"],
        "packet_id": packet["packet_id"],
        "packet_path": str(result_dir / "frozen_packet.json"),
        "execution_path": str(result_dir / "execution.json"),
        "evaluation_path": str(result_dir / "evaluation.json"),
        "summary_path": str(result_dir / "summary.json"),
        "calibration_metadata_path": str(result_dir / "execution.json") + "#/calibration_metadata",
        "raw_count_file_paths": [str(result_dir / "execution.json") + "#/jobs/0/raw_counts_by_row"],
        "verifier_output_path": None,
        "fixture_notice": SYNTHETIC_NOTICE,
    }
    return result_dir, record


def _manifest(tmp_path: Path, records: list[dict]) -> Path:
    manifest = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "sweep_id": "synthetic-sweep-fixture",
        "packet_id": None,
        "witness_families": [PRODUCT_STATE_CIRCUIT_FAMILY, ENTANGLING_CX_CIRCUIT_FAMILY],
        "backends": [{"provider": "ibm_runtime", "backend": "synthetic_backend"}],
        "bounded_claim_statement": "Synthetic fixture for verifier mechanics only; not real Stage 4 evidence.",
        "claim_boundary": {"supported": ["verifier mechanics"], "excluded": ["real hardware evidence"]},
        "records": records,
    }
    path = tmp_path / "manifest.json"
    _write_json(path, manifest)
    return path


def test_manifest_schema_validation_accepts_synthetic_completed_record(tmp_path: Path) -> None:
    _, record = _synthetic_result(tmp_path)
    manifest = json.loads(_manifest(tmp_path, [record]).read_text(encoding="utf-8"))
    assert validate_manifest(manifest) == []


def test_manifest_schema_requires_bitstring_order_for_completed_records(tmp_path: Path) -> None:
    _, record = _synthetic_result(tmp_path)
    record.pop("bitstring_order")
    manifest = json.loads(_manifest(tmp_path, [record]).read_text(encoding="utf-8"))
    assert "records[0] completed record bitstring_order must be q1q0 or q0q1" in validate_manifest(manifest)


def test_raw_count_to_expectation_conversion() -> None:
    expectations = raw_counts_to_expectations({"00": 3, "01": 1, "10": 1, "11": 3})
    assert expectations == {"shots": 8, "z0": 0.0, "z1": 0.0, "zz": 0.5, "valid": True}


def test_provider_aware_raw_count_to_expectation_conversion() -> None:
    current = raw_counts_to_expectations({"01": 8}, bitstring_order="q1q0")
    braket = raw_counts_to_expectations({"01": 8}, bitstring_order="q0q1")
    assert current["z0"] == -1.0
    assert current["z1"] == 1.0
    assert braket["z0"] == 1.0
    assert braket["z1"] == -1.0


def test_product_state_witness_metric_recomputation(tmp_path: Path) -> None:
    _, record = _synthetic_result(tmp_path, PRODUCT_STATE_CIRCUIT_FAMILY)
    verification = verify_manifest(_manifest(tmp_path, [record]))
    assert verification["pass"] is True
    row = verification["records"][0]["table_row"]
    assert row["family"] == PRODUCT_STATE_CIRCUIT_FAMILY
    assert row["witness_mae"] < row["control_mae"]


def test_nested_packet_summary_is_accepted(tmp_path: Path) -> None:
    result_dir, record = _synthetic_result(tmp_path, PRODUCT_STATE_CIRCUIT_FAMILY)
    evaluation = json.loads((result_dir / "evaluation.json").read_text(encoding="utf-8"))
    _write_json(result_dir / "summary.json", {"result": {"status": evaluation["status"], "evaluation": evaluation}})
    verification = verify_manifest(_manifest(tmp_path, [record]))
    assert verification["pass"] is True


def test_cx_witness_metric_recomputation(tmp_path: Path) -> None:
    _, record = _synthetic_result(tmp_path, ENTANGLING_CX_CIRCUIT_FAMILY)
    verification = verify_manifest(_manifest(tmp_path, [record]))
    assert verification["pass"] is True
    row = verification["records"][0]["table_row"]
    assert row["family"] == ENTANGLING_CX_CIRCUIT_FAMILY
    assert row["witness_mae"] < row["control_mae"]
    record_result = verification["records"][0]
    assert record_result["recorded_evaluation"]["witness"] == record_result["recomputed_evaluation"]["witness"]
    assert record_result["recorded_evaluation"]["control"] == record_result["recomputed_evaluation"]["control"]


def test_mae_calculation() -> None:
    assert mean_absolute_error([0.0, 1.0], [0.25, 0.75]) == 0.25


def test_rank_correlation_calculation() -> None:
    assert rank_correlation([0.0, 0.5, 1.0], [0.0, 0.5, 1.0]) == 1.0


def test_missing_evidence_files_fail_clearly(tmp_path: Path) -> None:
    record = {
        "record_id": "missing-real-record",
        "provider": "ibm_runtime",
        "backend": "ibm_kingston",
        "family": PRODUCT_STATE_CIRCUIT_FAMILY,
        "status": "missing_evidence",
        "shots": 4096,
        "row_count": None,
        "bitstring_order": "q1q0",
        "missing_evidence": ["execution.json with raw_counts_by_row"],
    }
    verification = verify_manifest(_manifest(tmp_path, [record]))
    assert verification["pass"] is False
    assert verification["missing_evidence"][0]["record_id"] == "missing-real-record"
    assert "execution.json with raw_counts_by_row" in verification["missing_evidence"][0]["missing_evidence"]


def test_metric_mismatch_fails(tmp_path: Path) -> None:
    result_dir, record = _synthetic_result(tmp_path)
    evaluation_path = result_dir / "evaluation.json"
    evaluation = json.loads(evaluation_path.read_text(encoding="utf-8"))
    evaluation["witness"]["mae"] = round(evaluation["witness"]["mae"] + 0.01, 6)
    _write_json(evaluation_path, evaluation)
    verification = verify_manifest(_manifest(tmp_path, [record]))
    assert verification["pass"] is False
    witness_mae_check = next(check for check in verification["records"][0]["checks"] if check["name"] == "witness_mae")
    assert witness_mae_check["pass"] is False


def test_expected_negative_hardware_record_verifies_without_positive_gate(tmp_path: Path) -> None:
    result_dir, record = _synthetic_result(tmp_path, ENTANGLING_CX_CIRCUIT_FAMILY)
    evaluation_path = result_dir / "evaluation.json"
    summary_path = result_dir / "summary.json"
    evaluation = json.loads(evaluation_path.read_text(encoding="utf-8"))
    evaluation.update(
        {
            "status": "FAIL_STOP",
            "outcome": "hardware-negative",
            "gate_pass": False,
            "hardware_direction_positive": False,
            "direction_agreement": False,
            "witness": {"mae": 0.3, "rank_correlation": 0.0},
            "control": {"mae": 0.1, "rank_correlation": 0.5},
            "fail_reasons": ["synthetic negative verifier fixture"],
        }
    )
    _write_json(evaluation_path, evaluation)
    _write_json(
        summary_path,
        {"status": "FAIL_STOP", "outcome": "hardware-negative", "gate_pass": False},
    )
    execution = json.loads((result_dir / "execution.json").read_text(encoding="utf-8"))
    execution["jobs"][0]["raw_counts_by_row"] = [
        {
            "row_id": item["row_id"],
            "counts": {"00": 128, "01": 128},
        }
        for item in execution["jobs"][0]["raw_counts_by_row"]
    ]
    _write_json(result_dir / "execution.json", execution)
    recomputed = evaluate_hardware_execution(
        json.loads((result_dir / "frozen_packet.json").read_text(encoding="utf-8")),
        execution,
    )
    _write_json(evaluation_path, recomputed)
    _write_json(
        summary_path,
        {"status": recomputed["status"], "outcome": recomputed["outcome"], "gate_pass": recomputed["gate_pass"]},
    )
    record["expected_outcome"] = "hardware-negative"
    verification = verify_manifest(_manifest(tmp_path, [record]))
    assert verification["pass"] is True
    checks = {check["name"]: check["pass"] for check in verification["records"][0]["checks"]}
    assert checks["expected_outcome_matches"] is True
    assert checks["negative_record_does_not_support_positive_gate"] is True


def test_overclaim_guardrail_flags_forbidden_supported_claim(tmp_path: Path) -> None:
    doc = tmp_path / "doc.md"
    doc.write_text("This would say quantum advantage proven if it were a supported claim.", encoding="utf-8")
    result = scan_public_docs_for_overclaims([doc])
    assert result["pass"] is False
    assert result["findings"][0]["phrase"] == "quantum advantage proven"
