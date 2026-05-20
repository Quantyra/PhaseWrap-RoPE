from __future__ import annotations

import json

from scripts.prepare_stage4_bitstring_calibration_packets import SCHEMA_VERSION, build_manifest, build_packet, write_outputs
from scripts.verify_stage4_bitstring_calibration import verify_execution, verify_manifest


def test_calibration_manifest_is_missing_evidence_by_default(tmp_path) -> None:
    paths = write_outputs(tmp_path)
    result = verify_manifest(tmp_path / "manifest.json")
    assert json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))["schema_version"] == SCHEMA_VERSION
    assert paths["manifest"].endswith("manifest.json")
    assert result["pass"] is False
    assert len(result["missing_evidence"]) == 2


def test_packet_expected_keys_follow_declared_order() -> None:
    ibm = build_packet("ibm_runtime", "q1q0")
    braket = build_packet("amazon_braket", "q0q1")
    assert [row["expected_dominant_key"] for row in ibm["states"]] == ["00", "10", "01", "11"]
    assert [row["expected_dominant_key"] for row in braket["states"]] == ["00", "01", "10", "11"]


def test_verify_execution_accepts_synthetic_completed_counts() -> None:
    packet = build_packet("amazon_braket", "q0q1")
    execution = {
        "raw_counts_by_state": [
            {"state": "00", "counts": {"00": 99, "01": 1}},
            {"state": "01", "counts": {"01": 99, "00": 1}},
            {"state": "10", "counts": {"10": 99, "11": 1}},
            {"state": "11", "counts": {"11": 99, "10": 1}},
        ]
    }
    checks = verify_execution(packet, execution)
    assert all(check["pass"] for check in checks)


def test_verify_manifest_accepts_completed_synthetic_record(tmp_path) -> None:
    manifest = build_manifest(tmp_path)
    manifest["records"] = manifest["records"][:1]
    record = manifest["records"][0]
    packet = build_packet("ibm_runtime", "q1q0")
    execution = {
        "raw_counts_by_state": [
            {"state": "00", "counts": {"00": 100}},
            {"state": "01", "counts": {"10": 100}},
            {"state": "10", "counts": {"01": 100}},
            {"state": "11", "counts": {"11": 100}},
        ]
    }
    record["status"] = "completed"
    record["execution_path"] = "execution.json"
    (tmp_path / "ibm_runtime_known_state_packet.json").write_text(json.dumps(packet), encoding="utf-8")
    (tmp_path / "execution.json").write_text(json.dumps(execution), encoding="utf-8")
    (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    result = verify_manifest(tmp_path / "manifest.json")
    assert result["pass"] is True
