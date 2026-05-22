from __future__ import annotations

import json

from qrope.stage99_matched_fixed_width_encoding_packet_freezer import (
    ENCODING_FAMILIES,
    run_stage99_freezer,
    write_stage99_outputs,
)


def _source_packet(lane_id: str, provider: str = "ibm_runtime") -> dict[str, object]:
    return {
        "backend": "TEST_BACKEND",
        "config": {"shot_count": 128},
        "preregistration": {
            "lane_id": lane_id,
            "row_set_hash": f"{lane_id}-rows",
        },
        "provider": provider,
        "rows": [
            {
                "row_id": "hwrow-000",
                "row_hash": "source-row-0",
                "source": {
                    "reference_delta": -2,
                    "candidate_delta": -6,
                    "seed": 1,
                    "slot": 0,
                },
            },
            {
                "row_id": "hwrow-001",
                "row_hash": "source-row-1",
                "source": {
                    "reference_delta": 3,
                    "candidate_delta": -1,
                    "seed": 1,
                    "slot": 1,
                },
            },
        ],
    }


def _write_packet(root, file_name: str, payload: dict[str, object]) -> None:
    path = root / file_name
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def test_stage99_freezes_five_matched_families_for_each_source_lane(tmp_path) -> None:
    _write_packet(tmp_path, "lane_a.json", _source_packet("lane_a"))
    _write_packet(tmp_path, "lane_b.json", _source_packet("lane_b", provider="amazon_braket"))

    result = run_stage99_freezer(source_packet_dir=tmp_path, source_packet_files=("lane_a.json", "lane_b.json"))

    assert result["stage"] == "stage99_matched_fixed_width_encoding_packet_freezer"
    assert result["status"] == "completed"
    assert result["decision"] == "MATCHED_FIXED_WIDTH_ENCODING_PACKETS_FROZEN_NO_HARDWARE"
    assert result["packet_count"] == 2 * len(ENCODING_FAMILIES)
    assert result["matched_encoding_families"] == list(ENCODING_FAMILIES)
    assert result["no_hardware_submission"] is True
    assert result["provider_credentials_required"] is False
    for packet in result["packets"]:
        assert packet["fixed_width"]["measured_qubits"] == 2
        assert packet["fixed_width"]["active_qubits"] == 2
        assert packet["fixed_width"]["circuit_template"] == "two_ry_product_state_z_readout_v1"
        assert packet["row_count"] == 2
        assert packet["execution_status"] == "not_submitted"


def test_stage99_no_position_control_is_centered_and_uses_same_rows(tmp_path) -> None:
    _write_packet(tmp_path, "lane_a.json", _source_packet("lane_a"))

    result = run_stage99_freezer(source_packet_dir=tmp_path, source_packet_files=("lane_a.json",))
    control = next(packet for packet in result["packets"] if packet["encoding_family"] == "no_position_control")

    assert [row["row_id"] for row in control["rows"]] == ["hwrow-000", "hwrow-001"]
    for row in control["rows"]:
        assert row["components"] == {"component_a": 0.0, "component_b": 0.0}
        assert row["ideal_predictions"]["score"] == 0.5


def test_stage99_outputs_are_written(tmp_path) -> None:
    _write_packet(tmp_path, "lane_a.json", _source_packet("lane_a"))
    result = run_stage99_freezer(source_packet_dir=tmp_path, source_packet_files=("lane_a.json",))

    paths = write_stage99_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((tmp_path / "out" / "results.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")
    packet_files = sorted((tmp_path / "out" / "packets").glob("*.json"))

    assert set(paths) == {"manifest", "result", "summary_csv", "packet_dir"}
    assert manifest["packet_count"] == len(ENCODING_FAMILIES)
    assert saved["decision"] == result["decision"]
    assert len(packet_files) == len(ENCODING_FAMILIES)
    assert "phasewrap" in summary
