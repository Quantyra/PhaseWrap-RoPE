from __future__ import annotations

import json

from qrope.stage103_robustness_metric_preregistration import (
    expectation_from_counts,
    packet_metrics,
    run_stage103_preregistration,
    score_from_counts,
    write_stage103_outputs,
)


def _write_json(path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _packet(root, packet_id: str, family: str = "phasewrap", template: str = "two_ry_product_state_z_readout_v1") -> dict[str, object]:
    path = root / f"{packet_id}.json"
    payload = {
        "packet_id": packet_id,
        "provider": "ibm_runtime",
        "source_lane_id": "lane_a",
        "encoding_family": family,
        "fixed_width": {"circuit_template": template},
        "rows": [
            {"row_id": "row0", "ideal_predictions": {"score": 1.0}},
            {"row_id": "row1", "ideal_predictions": {"score": 0.0}},
        ],
    }
    _write_json(path, payload)
    return {"path": path, "payload": payload}


def _execution(packet_id: str, row0_counts: dict[str, int], row1_counts: dict[str, int]) -> dict[str, object]:
    return {
        "status": "assembled_from_stage113_results",
        "no_hardware_submission": False,
        "job_or_task_ids": [f"job-{packet_id}"],
        "backend_metadata": {"provider": "ibm_runtime", "backend": "backend_a"},
        "submitted_at_utc": "2026-05-21T00:00:00Z",
        "completed_at_utc": "2026-05-21T00:01:00Z",
        "raw_counts_by_row": [{"row_id": "row0", "counts": row0_counts}, {"row_id": "row1", "counts": row1_counts}],
    }


def _stage113_ready(path) -> None:
    _write_json(
        path,
        {
            "decision": "JOB_RESULTS_ASSEMBLED_INTO_STAGE109_EVIDENCE",
            "stage115_write_ready": True,
            "stage115_write_blockers": [],
            "stage115_stage152_first_provider_runner_command_count": 1,
            "stage115_stage152_first_provider_authorized_runner_count": 1,
            "stage115_stage152_first_provider_live_submit_ready_count": 1,
            "stage115_stage152_all_first_provider_commands_authorized": True,
            "stage115_stage152_all_first_provider_commands_live_submit_ready": True,
        },
    )


def _stage104_ready(path, *, complete_groups: int = 1) -> None:
    _write_json(
        path,
        {
            "decision": "MATCHED_PACKET_EXECUTION_TEMPLATES_PREPARED_CALIBRATION_AND_COUNTS_REQUIRED",
            "expected_packet_count": 5,
            "template_count": 5,
            "expected_matched_group_count": 1,
            "matched_group_count": 1,
            "complete_matched_group_count": complete_groups,
        },
    )


def test_score_reconstruction_for_product_and_cx_counts() -> None:
    assert expectation_from_counts({"00": 10}, "z0") == 1.0
    assert expectation_from_counts({"11": 10}, "z0z1") == 1.0
    assert score_from_counts({"00": 10}, "two_ry_product_state_z_readout_v1") == 1.0
    assert score_from_counts({"01": 10}, "two_ry_cx_parity_z_readout_v1") == 0.5


def test_packet_metrics_compute_error_and_rank() -> None:
    packet = _packet_payload("phasewrap")
    execution = {
        "raw_counts_by_row": [
            {"row_id": "row0", "counts": {"00": 10}},
            {"row_id": "row1", "counts": {"11": 10}},
        ]
    }

    metrics = packet_metrics(packet, execution)

    assert metrics["coverage_fraction"] == 1.0
    assert metrics["mean_absolute_score_error"] == 0.0
    assert metrics["spearman_rank_correlation"] == 1.0
    assert metrics["top1_match"] is True


def test_stage103_preregisters_metrics_and_blocks_without_counts(tmp_path) -> None:
    packet = _packet(tmp_path, "lane_a__phasewrap")
    _write_json(tmp_path / "stage99.json", {"packet_paths": [str(packet["path"])]})
    _write_json(tmp_path / "stage100.json", {"packet_paths": []})
    _write_json(tmp_path / "stage101.json", {"known_state_calibration_pass": False})
    _write_json(tmp_path / "stage102.json", {"decision": "CALIBRATION_EXECUTION_TEMPLATES_PREPARED_COUNTS_STILL_REQUIRED"})

    result = run_stage103_preregistration(
        stage99_manifest_path=tmp_path / "stage99.json",
        stage100_manifest_path=tmp_path / "stage100.json",
        stage101_results_path=tmp_path / "stage101.json",
        stage102_manifest_path=tmp_path / "stage102.json",
    )

    assert result["decision"] == "ROBUSTNESS_METRICS_PREREGISTERED_HARDWARE_COUNTS_REQUIRED"
    assert result["packet_count"] == 1
    assert result["metric_record_count"] == 0
    assert result["missing_execution_count"] == 1


def test_stage103_computes_metrics_with_complete_family_counts_after_calibration(tmp_path) -> None:
    packet_specs = [
        ("phasewrap", {"00": 10}, {"11": 10}),
        ("rope_like", {"11": 10}, {"00": 10}),
        ("sinusoidal_like", {"11": 10}, {"00": 10}),
        ("alibi_like", {"11": 10}, {"00": 10}),
        ("no_position_control", {"11": 10}, {"00": 10}),
    ]
    packets = [
        _packet(tmp_path, f"lane_a__{family}", family)
        for family, _, _ in packet_specs
    ]
    _write_json(tmp_path / "stage99.json", {"packet_paths": [str(packet["path"]) for packet in packets]})
    _write_json(tmp_path / "stage100.json", {"packet_paths": []})
    _write_json(
        tmp_path / "stage101.json",
        {
            "known_state_calibration_pass": True,
            "decision": "KNOWN_STATE_CALIBRATION_VERIFIED_READY_FOR_MATCHED_HARDWARE_EXECUTION",
        },
    )
    _write_json(tmp_path / "stage102.json", {"decision": "ok"})
    _stage113_ready(tmp_path / "stage113.json")
    _stage104_ready(tmp_path / "stage104.json")
    for family, row0_counts, row1_counts in packet_specs:
        packet_id = f"lane_a__{family}"
        _write_json(tmp_path / f"exec/{packet_id}.json", _execution(packet_id, row0_counts, row1_counts))

    result = run_stage103_preregistration(
        stage99_manifest_path=tmp_path / "stage99.json",
        stage100_manifest_path=tmp_path / "stage100.json",
        stage101_results_path=tmp_path / "stage101.json",
        stage102_manifest_path=tmp_path / "stage102.json",
        stage113_results_path=tmp_path / "stage113.json",
        stage104_results_path=tmp_path / "stage104.json",
        execution_dir=tmp_path / "exec",
    )

    assert result["decision"] == "ROBUSTNESS_METRICS_READY_FOR_INTERPRETATION"
    assert result["metric_record_count"] == 5
    assert result["comparison_groups_complete"] is True
    assert result["stage104_matched_surface_ready"] is True
    phasewrap_record = next(record for record in result["metric_records"] if record["encoding_family"] == "phasewrap")
    assert phasewrap_record["mean_absolute_score_error"] == 0.0


def test_stage103_requires_stage113_live_submit_provenance_for_interpretation(tmp_path) -> None:
    packet_specs = [
        ("phasewrap", {"00": 10}, {"11": 10}),
        ("rope_like", {"11": 10}, {"00": 10}),
        ("sinusoidal_like", {"11": 10}, {"00": 10}),
        ("alibi_like", {"11": 10}, {"00": 10}),
        ("no_position_control", {"11": 10}, {"00": 10}),
    ]
    packets = [_packet(tmp_path, f"lane_a__{family}", family) for family, _, _ in packet_specs]
    _write_json(tmp_path / "stage99.json", {"packet_paths": [str(packet["path"]) for packet in packets]})
    _write_json(tmp_path / "stage100.json", {"packet_paths": []})
    _write_json(
        tmp_path / "stage101.json",
        {
            "known_state_calibration_pass": True,
            "decision": "KNOWN_STATE_CALIBRATION_VERIFIED_READY_FOR_MATCHED_HARDWARE_EXECUTION",
        },
    )
    _write_json(tmp_path / "stage102.json", {"decision": "ok"})
    _write_json(
        tmp_path / "stage113.json",
        {
            "decision": "JOB_RESULTS_ASSEMBLED_INTO_STAGE109_EVIDENCE",
            "stage115_write_ready": True,
            "stage115_write_blockers": [],
            "stage115_stage152_first_provider_runner_command_count": 2,
            "stage115_stage152_first_provider_authorized_runner_count": 1,
            "stage115_stage152_first_provider_live_submit_ready_count": 1,
            "stage115_stage152_all_first_provider_commands_authorized": False,
            "stage115_stage152_all_first_provider_commands_live_submit_ready": False,
        },
    )
    _stage104_ready(tmp_path / "stage104.json")
    for family, row0_counts, row1_counts in packet_specs:
        packet_id = f"lane_a__{family}"
        _write_json(tmp_path / f"exec/{packet_id}.json", _execution(packet_id, row0_counts, row1_counts))

    result = run_stage103_preregistration(
        stage99_manifest_path=tmp_path / "stage99.json",
        stage100_manifest_path=tmp_path / "stage100.json",
        stage101_results_path=tmp_path / "stage101.json",
        stage102_manifest_path=tmp_path / "stage102.json",
        stage113_results_path=tmp_path / "stage113.json",
        stage104_results_path=tmp_path / "stage104.json",
        execution_dir=tmp_path / "exec",
    )

    assert result["decision"] == "ROBUSTNESS_METRICS_PREREGISTERED_HARDWARE_COUNTS_REQUIRED"
    assert result["metric_record_count"] == 5
    assert result["comparison_groups_complete"] is True
    assert result["stage113_live_submit_provenance_ready"] is False
    assert result["stage113_stage115_stage152_all_first_provider_commands_authorized"] is False
    assert result["stage113_stage115_stage152_all_first_provider_commands_live_submit_ready"] is False


def test_stage103_requires_stage104_matched_surface_for_interpretation(tmp_path) -> None:
    packet_specs = [
        ("phasewrap", {"00": 10}, {"11": 10}),
        ("rope_like", {"11": 10}, {"00": 10}),
        ("sinusoidal_like", {"11": 10}, {"00": 10}),
        ("alibi_like", {"11": 10}, {"00": 10}),
        ("no_position_control", {"11": 10}, {"00": 10}),
    ]
    packets = [_packet(tmp_path, f"lane_a__{family}", family) for family, _, _ in packet_specs]
    _write_json(tmp_path / "stage99.json", {"packet_paths": [str(packet["path"]) for packet in packets]})
    _write_json(tmp_path / "stage100.json", {"packet_paths": []})
    _write_json(
        tmp_path / "stage101.json",
        {
            "known_state_calibration_pass": True,
            "decision": "KNOWN_STATE_CALIBRATION_VERIFIED_READY_FOR_MATCHED_HARDWARE_EXECUTION",
        },
    )
    _write_json(tmp_path / "stage102.json", {"decision": "ok"})
    _stage113_ready(tmp_path / "stage113.json")
    _stage104_ready(tmp_path / "stage104.json", complete_groups=0)
    for family, row0_counts, row1_counts in packet_specs:
        packet_id = f"lane_a__{family}"
        _write_json(tmp_path / f"exec/{packet_id}.json", _execution(packet_id, row0_counts, row1_counts))

    result = run_stage103_preregistration(
        stage99_manifest_path=tmp_path / "stage99.json",
        stage100_manifest_path=tmp_path / "stage100.json",
        stage101_results_path=tmp_path / "stage101.json",
        stage102_manifest_path=tmp_path / "stage102.json",
        stage113_results_path=tmp_path / "stage113.json",
        stage104_results_path=tmp_path / "stage104.json",
        execution_dir=tmp_path / "exec",
    )

    assert result["decision"] == "ROBUSTNESS_METRICS_PREREGISTERED_HARDWARE_COUNTS_REQUIRED"
    assert result["metric_record_count"] == 5
    assert result["comparison_groups_complete"] is True
    assert result["stage104_matched_surface_ready"] is False
    assert result["stage104_complete_matched_group_count"] == 0


def test_stage103_blocks_incomplete_family_group_after_calibration(tmp_path) -> None:
    phasewrap = _packet(tmp_path, "lane_a__phasewrap", "phasewrap")
    rope = _packet(tmp_path, "lane_a__rope_like", "rope_like")
    _write_json(tmp_path / "stage99.json", {"packet_paths": [str(phasewrap["path"]), str(rope["path"])]})
    _write_json(tmp_path / "stage100.json", {"packet_paths": []})
    _write_json(
        tmp_path / "stage101.json",
        {
            "known_state_calibration_pass": True,
            "decision": "KNOWN_STATE_CALIBRATION_VERIFIED_READY_FOR_MATCHED_HARDWARE_EXECUTION",
        },
    )
    _write_json(tmp_path / "stage102.json", {"decision": "ok"})
    _write_json(tmp_path / "exec/lane_a__phasewrap.json", _execution("lane_a__phasewrap", {"00": 10}, {"11": 10}))
    _write_json(tmp_path / "exec/lane_a__rope_like.json", _execution("lane_a__rope_like", {"11": 10}, {"00": 10}))

    result = run_stage103_preregistration(
        stage99_manifest_path=tmp_path / "stage99.json",
        stage100_manifest_path=tmp_path / "stage100.json",
        stage101_results_path=tmp_path / "stage101.json",
        stage102_manifest_path=tmp_path / "stage102.json",
        execution_dir=tmp_path / "exec",
    )

    assert result["decision"] == "ROBUSTNESS_METRICS_PREREGISTERED_HARDWARE_COUNTS_REQUIRED"
    assert result["metric_record_count"] == 2
    assert result["comparison_groups_complete"] is False


def test_stage103_blocks_counts_without_result_lineage_metadata(tmp_path) -> None:
    phasewrap = _packet(tmp_path, "lane_a__phasewrap", "phasewrap")
    _write_json(tmp_path / "stage99.json", {"packet_paths": [str(phasewrap["path"])]})
    _write_json(tmp_path / "stage100.json", {"packet_paths": []})
    _write_json(
        tmp_path / "stage101.json",
        {
            "known_state_calibration_pass": True,
            "decision": "KNOWN_STATE_CALIBRATION_VERIFIED_READY_FOR_MATCHED_HARDWARE_EXECUTION",
        },
    )
    _write_json(tmp_path / "stage102.json", {"decision": "ok"})
    execution = _execution("lane_a__phasewrap", {"00": 10}, {"11": 10})
    execution.pop("backend_metadata")
    _write_json(tmp_path / "exec/lane_a__phasewrap.json", execution)

    result = run_stage103_preregistration(
        stage99_manifest_path=tmp_path / "stage99.json",
        stage100_manifest_path=tmp_path / "stage100.json",
        stage101_results_path=tmp_path / "stage101.json",
        stage102_manifest_path=tmp_path / "stage102.json",
        execution_dir=tmp_path / "exec",
    )

    assert result["decision"] == "ROBUSTNESS_METRICS_PREREGISTERED_HARDWARE_COUNTS_REQUIRED"
    assert result["metric_record_count"] == 0
    assert result["missing_execution"][0]["reason"] == "result_lineage_metadata_missing"
    assert result["missing_execution"][0]["missing_fields"] == ["backend_metadata"]


def test_stage103_blocks_partial_row_coverage(tmp_path) -> None:
    phasewrap = _packet(tmp_path, "lane_a__phasewrap", "phasewrap")
    _write_json(tmp_path / "stage99.json", {"packet_paths": [str(phasewrap["path"])]})
    _write_json(tmp_path / "stage100.json", {"packet_paths": []})
    _write_json(
        tmp_path / "stage101.json",
        {
            "known_state_calibration_pass": True,
            "decision": "KNOWN_STATE_CALIBRATION_VERIFIED_READY_FOR_MATCHED_HARDWARE_EXECUTION",
        },
    )
    _write_json(tmp_path / "stage102.json", {"decision": "ok"})
    execution = _execution("lane_a__phasewrap", {"00": 10}, {"11": 10})
    execution["raw_counts_by_row"] = [{"row_id": "row0", "counts": {"00": 10}}]
    _write_json(tmp_path / "exec/lane_a__phasewrap.json", execution)

    result = run_stage103_preregistration(
        stage99_manifest_path=tmp_path / "stage99.json",
        stage100_manifest_path=tmp_path / "stage100.json",
        stage101_results_path=tmp_path / "stage101.json",
        stage102_manifest_path=tmp_path / "stage102.json",
        execution_dir=tmp_path / "exec",
    )

    assert result["decision"] == "ROBUSTNESS_METRICS_PREREGISTERED_HARDWARE_COUNTS_REQUIRED"
    assert result["metric_record_count"] == 0
    assert result["missing_execution"][0]["reason"] == "packet_row_counts_incomplete"
    assert result["missing_execution"][0]["missing_rows"] == ["row1"]


def test_stage103_rejects_complete_counts_without_stage113_status(tmp_path) -> None:
    phasewrap = _packet(tmp_path, "lane_a__phasewrap", "phasewrap")
    _write_json(tmp_path / "stage99.json", {"packet_paths": [str(phasewrap["path"])]})
    _write_json(tmp_path / "stage100.json", {"packet_paths": []})
    _write_json(
        tmp_path / "stage101.json",
        {
            "known_state_calibration_pass": True,
            "decision": "KNOWN_STATE_CALIBRATION_VERIFIED_READY_FOR_MATCHED_HARDWARE_EXECUTION",
        },
    )
    _write_json(tmp_path / "stage102.json", {"decision": "ok"})
    _write_json(
        tmp_path / "exec/lane_a__phasewrap.json",
        {"raw_counts_by_row": [{"row_id": "row0", "counts": {"00": 10}}, {"row_id": "row1", "counts": {"11": 10}}]},
    )

    result = run_stage103_preregistration(
        stage99_manifest_path=tmp_path / "stage99.json",
        stage100_manifest_path=tmp_path / "stage100.json",
        stage101_results_path=tmp_path / "stage101.json",
        stage102_manifest_path=tmp_path / "stage102.json",
        execution_dir=tmp_path / "exec",
    )

    assert result["decision"] == "ROBUSTNESS_METRICS_PREREGISTERED_HARDWARE_COUNTS_REQUIRED"
    assert result["metric_record_count"] == 0
    assert result["missing_execution"][0]["reason"] == "stage113_assembled_status_missing"


def test_stage103_outputs_are_written(tmp_path) -> None:
    _write_json(tmp_path / "stage99.json", {"packet_paths": []})
    _write_json(tmp_path / "stage100.json", {"packet_paths": []})
    _write_json(tmp_path / "stage101.json", {"known_state_calibration_pass": False})
    _write_json(tmp_path / "stage102.json", {"decision": "ok"})
    result = run_stage103_preregistration(
        stage99_manifest_path=tmp_path / "stage99.json",
        stage100_manifest_path=tmp_path / "stage100.json",
        stage101_results_path=tmp_path / "stage101.json",
        stage102_manifest_path=tmp_path / "stage102.json",
    )

    paths = write_stage103_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert manifest["stage"] == "stage103_robustness_metric_preregistration"
    assert "mean_absolute_score_error" in summary


def _packet_payload(family: str) -> dict[str, object]:
    return {
        "packet_id": f"lane_a__{family}",
        "provider": "ibm_runtime",
        "source_lane_id": "lane_a",
        "encoding_family": family,
        "fixed_width": {"circuit_template": "two_ry_product_state_z_readout_v1"},
        "rows": [
            {"row_id": "row0", "ideal_predictions": {"score": 1.0}},
            {"row_id": "row1", "ideal_predictions": {"score": 0.0}},
        ],
    }
