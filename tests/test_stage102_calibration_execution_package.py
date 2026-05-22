from __future__ import annotations

import json

from qrope.stage102_calibration_execution_package import build_execution_template, run_stage102_package, write_stage102_outputs


def _write_stage101(root) -> None:
    payload = {
        "decision": "KNOWN_STATE_CALIBRATION_COUNTS_REQUIRED_BEFORE_HARDWARE_INTERPRETATION",
        "known_state_calibration_pass": False,
        "provider_records": [
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
        ],
    }
    (root / "stage101_results.json").write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def test_build_execution_template_sets_expected_keys_and_circuits() -> None:
    template = build_execution_template({"provider": "ibm_runtime", "expected_bitstring_order": "q1q0"})

    expected = {row["state"]: row["expected_dominant_key"] for row in template["raw_counts_by_state"]}
    assert expected == {"00": "00", "01": "10", "10": "01", "11": "11"}
    assert "x q[0];" in next(row["openqasm3"] for row in template["raw_counts_by_state"] if row["state"] == "10")
    assert "x q[1];" in next(row["openqasm3"] for row in template["raw_counts_by_state"] if row["state"] == "01")
    assert template["job_or_task_ids"] == []
    assert template["no_hardware_submission"] is True


def test_stage102_prepares_templates_from_stage101_provider_records(tmp_path) -> None:
    _write_stage101(tmp_path)

    result = run_stage102_package(stage101_results_path=tmp_path / "stage101_results.json")

    assert result["decision"] == "CALIBRATION_EXECUTION_TEMPLATES_PREPARED_COUNTS_STILL_REQUIRED"
    assert result["template_count"] == 2
    assert result["provider_credentials_required"] is False
    assert result["evidence_records"][0]["ready_for_stage101"] is False
    assert "backend_metadata" in result["evidence_records"][0]["missing_evidence"]
    assert "raw_counts_by_state" in result["evidence_records"][0]["missing_evidence"]


def test_stage102_reports_missing_stage101_source(tmp_path) -> None:
    result = run_stage102_package(stage101_results_path=tmp_path / "missing.json")

    assert result["status"] == "incomplete"
    assert result["decision"] == "CALIBRATION_EXECUTION_TEMPLATE_PACKAGE_INCOMPLETE"
    assert result["missing_source_artifacts"]


def test_stage102_outputs_are_written(tmp_path) -> None:
    _write_stage101(tmp_path)
    result = run_stage102_package(stage101_results_path=tmp_path / "stage101_results.json")

    paths = write_stage102_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")
    templates = sorted((tmp_path / "out" / "execution_templates").glob("*.json"))

    assert set(paths) == {"manifest", "result", "summary_csv", "template_dir"}
    assert manifest["template_count"] == 2
    assert len(templates) == 2
    assert "amazon_braket" in summary
