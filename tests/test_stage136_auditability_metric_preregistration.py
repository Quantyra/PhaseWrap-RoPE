from __future__ import annotations

import json
from pathlib import Path

from qrope.stage136_auditability_metric_preregistration import run_stage136_preregistration, write_stage136_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _packet(packet_id: str, family: str, template: str = "two_ry_product_state_z_readout_v1") -> dict:
    return {
        "packet_id": packet_id,
        "source_lane_id": "lane_0",
        "source_row_set_hash": "lane-0-row-set",
        "encoding_family": family,
        "provider": "ibm_runtime",
        "row_count": 1,
        "shot_count": 128,
        "fixed_width": {
            "circuit_template": template,
            "measured_qubits": 2,
            "active_qubits": 2,
            "readout": "computational_basis",
        },
        "packet_hash": f"hash-{packet_id}",
        "rows": [
            {
                "row_id": "row_0",
                "source_row_hash": "source-row-hash",
                "encoding_family": family,
                "source": {"reference_delta": 1, "candidate_delta": 0},
                "delta": 1.0,
                "components": {"component_a": 0.5, "component_b": 0.25},
                "circuit_parameters": {
                    "template": template,
                    "ry_q0": 1.0,
                    "ry_q1": 1.2,
                    "z0_target": 0.5,
                    "z1_target": 0.25,
                },
                "ideal_predictions": {"score": 0.6875},
                "row_hash": f"row-hash-{packet_id}",
            }
        ],
    }


def _write_fixture(tmp_path, *, missing_row_field: bool = False):
    families = ("phasewrap", "rope_like", "sinusoidal_like", "alibi_like", "no_position_control")
    product_paths = []
    cx_paths = []
    for family in families:
        product = _packet(f"product__{family}", family)
        cx = _packet(f"cx__{family}", family, "two_ry_cx_parity_z_readout_v1")
        if missing_row_field and family == "phasewrap":
            del product["rows"][0]["components"]
        product_path = tmp_path / "product" / f"{family}.json"
        cx_path = tmp_path / "cx" / f"{family}.json"
        _write_json(product_path, product)
        _write_json(cx_path, cx)
        product_paths.append(str(product_path.as_posix()))
        cx_paths.append(str(cx_path.as_posix()))
    _write_json(tmp_path / "stage99_manifest.json", {"packet_paths": product_paths})
    _write_json(tmp_path / "stage100_manifest.json", {"packet_paths": cx_paths})
    return tmp_path / "stage99_manifest.json", tmp_path / "stage100_manifest.json"


def test_stage136_reports_ready_contract_for_complete_matched_packets(tmp_path) -> None:
    stage99, stage100 = _write_fixture(tmp_path)

    result = run_stage136_preregistration(stage99_manifest_path=stage99, stage100_manifest_path=stage100)

    assert result["decision"] == "AUDITABILITY_METRIC_CONTRACT_READY_HARDWARE_COUNTS_REQUIRED"
    assert result["packet_count"] == 10
    assert result["ready_packet_count"] == 10
    assert result["lane_family_record_count"] == 2
    assert all(record["all_packet_audit_traces_ready"] for record in result["lane_family_records"])
    assert result["no_hardware_submission"] is True


def test_stage136_blocks_when_audit_trace_fields_are_missing(tmp_path) -> None:
    stage99, stage100 = _write_fixture(tmp_path, missing_row_field=True)

    result = run_stage136_preregistration(stage99_manifest_path=stage99, stage100_manifest_path=stage100)

    assert result["decision"] == "AUDITABILITY_METRIC_CONTRACT_INCOMPLETE"
    assert result["ready_packet_count"] == 9
    broken = [record for record in result["packet_records"] if not record["ready"]]
    assert broken
    assert "row_audit_fields_missing" in broken[0]["missing_audit_fields"]


def test_stage136_blocks_when_comparator_group_is_incomplete(tmp_path) -> None:
    stage99, stage100 = _write_fixture(tmp_path)
    manifest = json.loads(stage99.read_text(encoding="utf-8"))
    manifest["packet_paths"] = [path for path in manifest["packet_paths"] if not path.endswith("rope_like.json")]
    stage99.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")

    result = run_stage136_preregistration(stage99_manifest_path=stage99, stage100_manifest_path=stage100)

    assert result["decision"] == "AUDITABILITY_METRIC_CONTRACT_INCOMPLETE"
    incomplete = [record for record in result["lane_family_records"] if not record["all_packet_audit_traces_ready"]]
    assert incomplete
    assert incomplete[0]["missing_encoding_families"] == ["rope_like"]


def test_stage136_blocks_when_fixed_width_metadata_is_incomplete(tmp_path) -> None:
    stage99, stage100 = _write_fixture(tmp_path)
    manifest = json.loads(stage99.read_text(encoding="utf-8"))
    packet_path = next(path for path in manifest["packet_paths"] if path.endswith("phasewrap.json"))
    packet = json.loads(Path(packet_path).read_text(encoding="utf-8"))
    packet["fixed_width"]["readout"] = "x_basis"
    Path(packet_path).write_text(json.dumps(packet, indent=2, sort_keys=True), encoding="utf-8")

    result = run_stage136_preregistration(stage99_manifest_path=stage99, stage100_manifest_path=stage100)

    assert result["decision"] == "AUDITABILITY_METRIC_CONTRACT_INCOMPLETE"
    broken = [record for record in result["packet_records"] if not record["ready"]]
    assert "fixed_width.readout" in broken[0]["missing_audit_fields"]


def test_stage136_outputs_are_written(tmp_path) -> None:
    stage99, stage100 = _write_fixture(tmp_path)
    result = run_stage136_preregistration(stage99_manifest_path=stage99, stage100_manifest_path=stage100)

    paths = write_stage136_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert manifest["ready_packet_count"] == 10
    assert "phasewrap" in summary
