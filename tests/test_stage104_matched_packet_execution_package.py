from __future__ import annotations

import json

from qrope.stage104_matched_packet_execution_package import (
    build_packet_execution_template,
    run_stage104_package,
    write_stage104_outputs,
)


def _write_json(path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _packet(
    path,
    packet_id: str,
    *,
    family: str = "phasewrap",
    lane: str = "lane_a",
    provider: str = "ibm_runtime",
    template: str = "two_ry_product_state_z_readout_v1",
) -> None:
    payload = {
        "packet_id": packet_id,
        "packet_hash": f"{packet_id}-hash",
        "source_lane_id": lane,
        "source_row_set_hash": f"{lane}-row-set",
        "provider": provider,
        "backend": "BACKEND",
        "encoding_family": family,
        "shot_count": 128,
        "fixed_width": {
            "measured_qubits": 2,
            "active_qubits": 2,
            "readout": "computational_basis",
            "circuit_template": template,
        },
        "rows": [
            {
                "row_id": "row0",
                "circuit_parameters": {"ry_q0": 0.0, "ry_q1": 1.0},
                "ideal_predictions": {"score": 0.75},
            }
        ],
    }
    _write_json(path, payload)


def _matched_surface(tmp_path) -> tuple[list[str], list[str]]:
    families = ("phasewrap", "rope_like", "sinusoidal_like", "alibi_like", "no_position_control")
    stage99_paths = []
    stage100_paths = []
    lanes = (
        ("ibm_runtime", "ibm_product_seed314_rows16_shots4096"),
        ("amazon_braket", "braket_product_seed2718_rows8_shots1000"),
    )
    for provider, lane in lanes:
        for family in families:
            packet_path = tmp_path / f"{lane}__{family}.json"
            _packet(packet_path, f"{lane}__{family}", family=family, lane=lane, provider=provider)
            stage99_paths.append(str(packet_path))
            cx_lane = lane.replace("product", "cx")
            cx_path = tmp_path / f"{cx_lane}__{family}.json"
            _packet(
                cx_path,
                f"{cx_lane}__{family}",
                family=family,
                lane=cx_lane,
                provider=provider,
                template="two_ry_cx_parity_z_readout_v1",
            )
            stage100_paths.append(str(cx_path))
    return stage99_paths, stage100_paths


def test_build_packet_execution_template_includes_rows_and_programs(tmp_path) -> None:
    packet_path = tmp_path / "packet.json"
    _packet(packet_path, "packet")
    packet = json.loads(packet_path.read_text(encoding="utf-8"))

    template = build_packet_execution_template(packet)

    assert template["packet_id"] == "packet"
    assert template["raw_counts_by_row"][0]["row_id"] == "row0"
    assert "ry(0.0) q[0];" in template["raw_counts_by_row"][0]["openqasm3"]
    assert template["raw_counts_by_row"][0]["counts"] == {}
    assert template["required_execution_fields"] == [
        "job_or_task_ids",
        "backend_metadata",
        "submitted_at_utc",
        "completed_at_utc",
        "raw_counts_by_row",
    ]


def test_stage104_prepares_template_for_each_matched_packet(tmp_path) -> None:
    packet_a = tmp_path / "packet_a.json"
    packet_b = tmp_path / "packet_b.json"
    _packet(packet_a, "packet_a")
    _packet(packet_b, "packet_b", template="two_ry_cx_parity_z_readout_v1")
    _write_json(tmp_path / "stage99.json", {"packet_paths": [str(packet_a)]})
    _write_json(tmp_path / "stage100.json", {"packet_paths": [str(packet_b)]})
    _write_json(tmp_path / "stage101.json", {"known_state_calibration_pass": False})
    _write_json(tmp_path / "stage103.json", {"decision": "ROBUSTNESS_METRICS_PREREGISTERED_HARDWARE_COUNTS_REQUIRED"})

    result = run_stage104_package(
        stage99_manifest_path=tmp_path / "stage99.json",
        stage100_manifest_path=tmp_path / "stage100.json",
        stage101_results_path=tmp_path / "stage101.json",
        stage103_manifest_path=tmp_path / "stage103.json",
    )

    assert result["status"] == "incomplete"
    assert result["template_count"] == 2
    assert result["stage101_known_state_calibration_pass"] is False
    assert "raw_counts_by_row" in result["evidence_records"][0]["missing_evidence"]
    assert result["complete_matched_group_count"] == 0


def test_stage104_marks_complete_for_twenty_packet_template_surface(tmp_path) -> None:
    stage99_paths, stage100_paths = _matched_surface(tmp_path)
    _write_json(tmp_path / "stage99.json", {"packet_paths": stage99_paths})
    _write_json(tmp_path / "stage100.json", {"packet_paths": stage100_paths})
    _write_json(tmp_path / "stage101.json", {"known_state_calibration_pass": True})
    _write_json(tmp_path / "stage103.json", {"decision": "ROBUSTNESS_METRICS_PREREGISTERED_HARDWARE_COUNTS_REQUIRED"})

    result = run_stage104_package(
        stage99_manifest_path=tmp_path / "stage99.json",
        stage100_manifest_path=tmp_path / "stage100.json",
        stage101_results_path=tmp_path / "stage101.json",
        stage103_manifest_path=tmp_path / "stage103.json",
    )

    assert result["status"] == "completed"
    assert result["decision"] == "MATCHED_PACKET_EXECUTION_TEMPLATES_PREPARED_CALIBRATION_AND_COUNTS_REQUIRED"
    assert result["template_count"] == 20
    assert result["matched_group_count"] == 4
    assert result["complete_matched_group_count"] == 4


def test_stage104_rejects_twenty_packet_surface_with_missing_comparator_family(tmp_path) -> None:
    stage99_paths, stage100_paths = _matched_surface(tmp_path)
    bad_packet = tmp_path / "duplicate_phasewrap.json"
    _packet(
        bad_packet,
        "duplicate_phasewrap",
        family="phasewrap",
        lane="ibm_product_seed314_rows16_shots4096",
        provider="ibm_runtime",
    )
    stage99_paths = [path for path in stage99_paths if "ibm_product_seed314_rows16_shots4096__rope_like" not in path]
    stage99_paths.append(str(bad_packet))
    _write_json(tmp_path / "stage99.json", {"packet_paths": stage99_paths})
    _write_json(tmp_path / "stage100.json", {"packet_paths": stage100_paths})
    _write_json(tmp_path / "stage101.json", {"known_state_calibration_pass": True})
    _write_json(tmp_path / "stage103.json", {"decision": "ROBUSTNESS_METRICS_PREREGISTERED_HARDWARE_COUNTS_REQUIRED"})

    result = run_stage104_package(
        stage99_manifest_path=tmp_path / "stage99.json",
        stage100_manifest_path=tmp_path / "stage100.json",
        stage101_results_path=tmp_path / "stage101.json",
        stage103_manifest_path=tmp_path / "stage103.json",
    )

    assert result["status"] == "incomplete"
    assert result["template_count"] == 20
    assert result["complete_matched_group_count"] == 3
    incomplete = [record for record in result["matched_group_records"] if not record["ready"]]
    assert incomplete[0]["missing_encoding_families"] == ["rope_like"]


def test_stage104_outputs_are_written(tmp_path) -> None:
    stage99_paths, stage100_paths = _matched_surface(tmp_path)
    _write_json(tmp_path / "stage99.json", {"packet_paths": stage99_paths})
    _write_json(tmp_path / "stage100.json", {"packet_paths": stage100_paths})
    _write_json(tmp_path / "stage101.json", {"known_state_calibration_pass": False})
    _write_json(tmp_path / "stage103.json", {"decision": "ROBUSTNESS_METRICS_PREREGISTERED_HARDWARE_COUNTS_REQUIRED"})
    result = run_stage104_package(
        stage99_manifest_path=tmp_path / "stage99.json",
        stage100_manifest_path=tmp_path / "stage100.json",
        stage101_results_path=tmp_path / "stage101.json",
        stage103_manifest_path=tmp_path / "stage103.json",
    )

    paths_out = write_stage104_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    templates = sorted((tmp_path / "out" / "packet_execution_templates").glob("*.json"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths_out) == {"manifest", "result", "summary_csv", "template_dir"}
    assert manifest["template_count"] == 20
    assert manifest["complete_matched_group_count"] == 4
    assert len(templates) == 20
    assert "phasewrap" in summary
