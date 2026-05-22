from __future__ import annotations

import json

from qrope.automated_stage_gates import ENTANGLING_CX_CIRCUIT_FAMILY, PRODUCT_STATE_CIRCUIT_FAMILY
from scripts.preregister_stage4_replication_packets import (
    LANES,
    SCHEMA_VERSION,
    build_manifest,
    build_preregistered_packet,
    stable_hash,
    write_outputs,
)


def test_stable_hash_is_deterministic() -> None:
    payload = {"b": [2, 1], "a": "x"}
    assert stable_hash(payload) == stable_hash({"a": "x", "b": [2, 1]})


def test_preregistered_packets_are_deterministic() -> None:
    first = build_preregistered_packet(LANES[0])
    second = build_preregistered_packet(LANES[0])
    assert first == second
    assert first["preregistration"]["execution_status"] == "not_submitted"
    assert first["preregistration"]["row_set_hash"]
    assert first["row_count"] == LANES[0]["rows"]
    assert first["shot_count"] == LANES[0]["shots"]


def test_manifest_contains_expected_lanes() -> None:
    manifest = build_manifest()
    assert manifest["schema_version"] == SCHEMA_VERSION
    assert manifest["no_hardware_submission"] is True
    assert len(manifest["records"]) == len(LANES)
    assert any(record["lane_id"] == "ibm_product_seed577_rows16_shots4096" for record in manifest["records"])
    assert any(record["lane_id"] == "ibm_cx_seed577_rows16_shots4096" for record in manifest["records"])
    families = {record["family"] for record in manifest["records"]}
    assert families == {PRODUCT_STATE_CIRCUIT_FAMILY, ENTANGLING_CX_CIRCUIT_FAMILY}
    assert all(record["execution_status"] == "not_submitted" for record in manifest["records"])


def test_write_outputs(tmp_path) -> None:
    paths = write_outputs(tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    assert set(paths) == {"manifest", *(lane["lane_id"] for lane in LANES)}
    assert manifest["records"][0]["packet_path"].endswith(".json")
    for lane in LANES:
        packet = json.loads((tmp_path / f"{lane['lane_id']}.json").read_text(encoding="utf-8"))
        assert packet["preregistration"]["lane_id"] == lane["lane_id"]
        assert packet["preregistration"]["execution_status"] == "not_submitted"
