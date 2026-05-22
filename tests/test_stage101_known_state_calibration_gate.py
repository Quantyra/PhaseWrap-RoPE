from __future__ import annotations

import json

from qrope.stage101_known_state_calibration_gate import (
    infer_bitstring_order,
    run_stage101_gate,
    verify_provider_execution,
    write_stage101_outputs,
)


def _write_json(root, relative: str, payload: dict[str, object]) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _calibration_manifest() -> dict[str, object]:
    return {
        "records": [
            {
                "provider": "ibm_runtime",
                "expected_bitstring_order": "q1q0",
                "packet_path": "ibm_runtime_known_state_packet.json",
            },
            {
                "provider": "amazon_braket",
                "expected_bitstring_order": "q0q1",
                "packet_path": "amazon_braket_known_state_packet.json",
            },
        ]
    }


def _execution_for_order(order: str) -> dict[str, object]:
    if order == "q0q1":
        counts = [
            {"state": "00", "counts": {"00": 96, "01": 4}},
            {"state": "01", "counts": {"01": 95, "00": 5}},
            {"state": "10", "counts": {"10": 94, "11": 6}},
            {"state": "11", "counts": {"11": 97, "10": 3}},
        ]
    else:
        counts = [
            {"state": "00", "counts": {"00": 96, "01": 4}},
            {"state": "01", "counts": {"10": 95, "00": 5}},
            {"state": "10", "counts": {"01": 94, "11": 6}},
            {"state": "11", "counts": {"11": 97, "10": 3}},
        ]
    return {
        "job_or_task_ids": ["job-1"],
        "backend_metadata": {"backend": "test"},
        "submitted_at_utc": "2026-05-21T00:00:00Z",
        "completed_at_utc": "2026-05-21T00:01:00Z",
        "raw_counts_by_state": counts,
    }


def test_infer_bitstring_order_from_known_state_counts() -> None:
    result = infer_bitstring_order(_execution_for_order("q1q0"))

    assert result["outcome"] == "calibration_verified"
    assert result["inferred_bitstring_order"] == "q1q0"


def test_verify_provider_execution_rejects_missing_fields() -> None:
    result = verify_provider_execution("ibm_runtime", "q1q0", {"raw_counts_by_state": []})

    assert result["pass"] is False
    assert result["outcome"] == "missing_required_fields"
    assert "job_or_task_ids" in result["missing_evidence"]


def test_stage101_blocks_without_real_execution_counts(tmp_path) -> None:
    _write_json(tmp_path, "stage99.json", {"decision": "MATCHED_FIXED_WIDTH_ENCODING_PACKETS_FROZEN_NO_HARDWARE"})
    _write_json(tmp_path, "stage100.json", {"decision": "MATCHED_CX_ENCODING_PACKETS_FROZEN_NO_HARDWARE"})
    _write_json(tmp_path, "calibration_manifest.json", _calibration_manifest())
    _write_json(tmp_path, "calibration_verification.json", {"pass": False})

    result = run_stage101_gate(
        stage99_manifest_path=tmp_path / "stage99.json",
        stage100_manifest_path=tmp_path / "stage100.json",
        calibration_manifest_path=tmp_path / "calibration_manifest.json",
        calibration_verification_path=tmp_path / "calibration_verification.json",
    )

    assert result["packet_freeze_ready"] is True
    assert result["known_state_calibration_pass"] is False
    assert result["decision"] == "KNOWN_STATE_CALIBRATION_COUNTS_REQUIRED_BEFORE_HARDWARE_INTERPRETATION"
    assert all(record["outcome"] == "missing_evidence" for record in result["verification_records"])


def test_stage101_passes_with_matching_synthetic_execution_counts(tmp_path) -> None:
    _write_json(tmp_path, "stage99.json", {"decision": "MATCHED_FIXED_WIDTH_ENCODING_PACKETS_FROZEN_NO_HARDWARE"})
    _write_json(tmp_path, "stage100.json", {"decision": "MATCHED_CX_ENCODING_PACKETS_FROZEN_NO_HARDWARE"})
    _write_json(tmp_path, "calibration_manifest.json", _calibration_manifest())
    _write_json(tmp_path, "calibration_verification.json", {"pass": False})
    _write_json(tmp_path, "executions/ibm_runtime_known_state_execution.json", _execution_for_order("q1q0"))
    _write_json(tmp_path, "executions/amazon_braket_known_state_execution.json", _execution_for_order("q0q1"))

    result = run_stage101_gate(
        stage99_manifest_path=tmp_path / "stage99.json",
        stage100_manifest_path=tmp_path / "stage100.json",
        calibration_manifest_path=tmp_path / "calibration_manifest.json",
        calibration_verification_path=tmp_path / "calibration_verification.json",
        execution_dir=tmp_path / "executions",
    )

    assert result["known_state_calibration_pass"] is True
    assert result["decision"] == "KNOWN_STATE_CALIBRATION_VERIFIED_READY_FOR_MATCHED_HARDWARE_EXECUTION"


def test_stage101_outputs_are_written(tmp_path) -> None:
    _write_json(tmp_path, "stage99.json", {"decision": "MATCHED_FIXED_WIDTH_ENCODING_PACKETS_FROZEN_NO_HARDWARE"})
    _write_json(tmp_path, "stage100.json", {"decision": "MATCHED_CX_ENCODING_PACKETS_FROZEN_NO_HARDWARE"})
    _write_json(tmp_path, "calibration_manifest.json", _calibration_manifest())
    _write_json(tmp_path, "calibration_verification.json", {"pass": False})
    result = run_stage101_gate(
        stage99_manifest_path=tmp_path / "stage99.json",
        stage100_manifest_path=tmp_path / "stage100.json",
        calibration_manifest_path=tmp_path / "calibration_manifest.json",
        calibration_verification_path=tmp_path / "calibration_verification.json",
    )

    paths = write_stage101_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert manifest["stage"] == "stage101_known_state_calibration_gate"
    assert "ibm_runtime" in summary
