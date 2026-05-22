from __future__ import annotations

import json

from qrope.stage137_auditability_metric_evaluator import run_stage137_evaluator, write_stage137_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _packet(path, packet_id, family, component_a, component_b) -> None:
    _write_json(
        path,
        {
            "packet_id": packet_id,
            "source_lane_id": "lane_0",
            "encoding_family": family,
            "fixed_width": {"circuit_template": "two_ry_product_state_z_readout_v1"},
            "row_count": 1,
            "rows": [
                {
                    "row_id": "row_0",
                    "components": {"component_a": component_a, "component_b": component_b},
                }
            ],
        },
    )


def _execution(path, packet_id, counts) -> None:
    _write_json(
        path,
        {
            "status": "assembled_from_stage113_results",
            "no_hardware_submission": False,
            "packet_id": packet_id,
            "job_or_task_ids": [f"job-{packet_id}"],
            "backend_metadata": {"provider": "ibm_runtime", "backend": "backend_a"},
            "submitted_at_utc": "2026-05-21T00:00:00Z",
            "completed_at_utc": "2026-05-21T00:01:00Z",
            "raw_counts_by_row": [{"row_id": "row_0", "counts": counts}],
        },
    )


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


def _ready_fixture(tmp_path):
    packet_dir = tmp_path / "packets"
    execution_dir = tmp_path / "executions"
    calibration_dir = tmp_path / "calibration"
    families = {
        "phasewrap": {"target": (1.0, 1.0), "counts": {"00": 100}},
        "rope_like": {"target": (1.0, 1.0), "counts": {"00": 80, "11": 20}},
        "sinusoidal_like": {"target": (1.0, 1.0), "counts": {"00": 70, "11": 30}},
        "alibi_like": {"target": (1.0, 1.0), "counts": {"00": 60, "11": 40}},
        "no_position_control": {"target": (1.0, 1.0), "counts": {"00": 50, "11": 50}},
    }
    packet_templates = []
    for family, spec in families.items():
        packet_id = f"lane_0__{family}"
        packet_path = packet_dir / f"{packet_id}.json"
        _packet(packet_path, packet_id, family, *spec["target"])
        _execution(execution_dir / f"{packet_id}.json", packet_id, spec["counts"])
        packet_templates.append(
            {
                "packet_id": packet_id,
                "encoding_family": family,
                "source_lane_id": "lane_0",
                "circuit_template": "two_ry_product_state_z_readout_v1",
                "row_count": 1,
                "template_path": str(packet_path.as_posix()),
            }
        )
    _write_json(
        calibration_dir / "stage101" / "results.json",
        {
            "decision": "KNOWN_STATE_CALIBRATION_VERIFIED_READY_FOR_MATCHED_HARDWARE_EXECUTION",
            "known_state_calibration_pass": True,
        },
    )
    plans = [
        {
            "window_id": "window_0",
            "provider": "ibm_runtime",
            "steps": [
                {"step_id": "known_state_calibration_execution", "output_path": str((calibration_dir / "ibm_runtime_known_state_execution.json").as_posix())},
                {"step_id": "matched_packet_execution", "output_dir": str(execution_dir.as_posix()), "packet_templates": packet_templates},
            ],
        }
    ]
    _write_json(tmp_path / "plans.json", plans)
    _write_json(
        tmp_path / "stage136.json",
        {
            "decision": "AUDITABILITY_METRIC_CONTRACT_READY_HARDWARE_COUNTS_REQUIRED",
            "packet_count": 5,
            "ready_packet_count": 5,
            "lane_family_record_count": 1,
            "lane_family_records": [{"all_packet_audit_traces_ready": True}],
        },
    )
    _stage113_ready(tmp_path / "stage113.json")
    return tmp_path / "plans.json", tmp_path / "stage136.json", tmp_path / "stage113.json"


def test_stage137_blocks_when_hardware_counts_are_missing(tmp_path) -> None:
    plans, stage136, stage113 = _ready_fixture(tmp_path)
    execution_to_remove = tmp_path / "executions" / "lane_0__phasewrap.json"
    execution_to_remove.unlink()

    result = run_stage137_evaluator(stage107_window_plans_path=plans, stage136_results_path=stage136, stage113_results_path=stage113)

    assert result["decision"] == "AUDITABILITY_METRICS_BLOCKED_HARDWARE_COUNTS_REQUIRED"
    assert result["ready_window_count"] == 0
    assert "packet_execution_counts_missing" in result["window_records"][0]["missing_evidence"]


def test_stage137_computes_component_reconstruction_advantage_when_counts_are_ready(tmp_path) -> None:
    plans, stage136, stage113 = _ready_fixture(tmp_path)

    result = run_stage137_evaluator(stage107_window_plans_path=plans, stage136_results_path=stage136, stage113_results_path=stage113)

    assert result["decision"] == "AUDITABILITY_METRICS_READY_FOR_CLAIM_GATE"
    assert result["stage113_live_submit_provenance_ready"] is True
    assert result["ready_window_count"] == 1
    assert result["comparison_summary_count"] == 1
    assert result["auditability_advantage_count"] == 1
    summary = result["comparison_summary"][0]
    assert summary["passes_auditability_advantage_rule"] is True
    assert summary["all_required_families_present"] is True
    assert summary["no_position_control_present"] is True
    assert summary["phasewrap_lower_error_than"] == ["rope_like", "sinusoidal_like", "alibi_like"]


def test_stage137_requires_stage113_live_submit_provenance_for_claim_gate(tmp_path) -> None:
    plans, stage136, stage113 = _ready_fixture(tmp_path)
    _write_json(
        stage113,
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

    result = run_stage137_evaluator(stage107_window_plans_path=plans, stage136_results_path=stage136, stage113_results_path=stage113)

    assert result["decision"] == "AUDITABILITY_METRICS_BLOCKED_HARDWARE_COUNTS_REQUIRED"
    assert result["ready_window_count"] == 0
    assert result["stage113_live_submit_provenance_ready"] is False
    assert "stage113_live_submit_provenance_not_ready" in result["window_records"][0]["missing_evidence"]


def test_stage137_requires_stage136_fixed_width_group_counters(tmp_path) -> None:
    plans, stage136, stage113 = _ready_fixture(tmp_path)
    _write_json(
        stage136,
        {
            "decision": "AUDITABILITY_METRIC_CONTRACT_READY_HARDWARE_COUNTS_REQUIRED",
            "packet_count": 5,
            "ready_packet_count": 4,
            "lane_family_record_count": 1,
            "lane_family_records": [{"all_packet_audit_traces_ready": False}],
        },
    )

    result = run_stage137_evaluator(stage107_window_plans_path=plans, stage136_results_path=stage136, stage113_results_path=stage113)

    assert result["decision"] == "AUDITABILITY_METRICS_BLOCKED_HARDWARE_COUNTS_REQUIRED"
    assert result["stage136_ready"] is False
    assert result["stage136_ready_packet_count"] == 4
    assert "stage136_auditability_contract_not_ready" in result["window_records"][0]["missing_evidence"]


def test_stage137_rejects_complete_counts_without_stage113_status(tmp_path) -> None:
    plans, stage136, stage113 = _ready_fixture(tmp_path)
    execution_path = tmp_path / "executions" / "lane_0__phasewrap.json"
    execution = json.loads(execution_path.read_text(encoding="utf-8"))
    execution.pop("status")
    _write_json(execution_path, execution)

    result = run_stage137_evaluator(stage107_window_plans_path=plans, stage136_results_path=stage136, stage113_results_path=stage113)

    assert result["decision"] == "AUDITABILITY_METRICS_BLOCKED_HARDWARE_COUNTS_REQUIRED"
    assert result["ready_window_count"] == 0
    phasewrap_packet = result["window_records"][0]["packet_records"][0]
    assert phasewrap_packet["ready"] is False
    assert "stage113_assembled_status" in phasewrap_packet["missing_evidence"]


def test_stage137_rejects_counts_without_result_lineage_metadata(tmp_path) -> None:
    plans, stage136, stage113 = _ready_fixture(tmp_path)
    execution_path = tmp_path / "executions" / "lane_0__phasewrap.json"
    execution = json.loads(execution_path.read_text(encoding="utf-8"))
    execution.pop("backend_metadata")
    _write_json(execution_path, execution)

    result = run_stage137_evaluator(stage107_window_plans_path=plans, stage136_results_path=stage136, stage113_results_path=stage113)

    assert result["decision"] == "AUDITABILITY_METRICS_BLOCKED_HARDWARE_COUNTS_REQUIRED"
    assert result["ready_window_count"] == 0
    phasewrap_packet = result["window_records"][0]["packet_records"][0]
    assert phasewrap_packet["ready"] is False
    assert "backend_metadata" in phasewrap_packet["missing_evidence"]


def test_stage137_rejects_incomplete_positional_comparator_group(tmp_path) -> None:
    plans, stage136, stage113 = _ready_fixture(tmp_path)
    payload = json.loads(plans.read_text(encoding="utf-8"))
    packet_templates = payload[0]["steps"][1]["packet_templates"]
    payload[0]["steps"][1]["packet_templates"] = [
        record for record in packet_templates if record["encoding_family"] != "alibi_like"
    ]
    _write_json(plans, payload)

    result = run_stage137_evaluator(stage107_window_plans_path=plans, stage136_results_path=stage136, stage113_results_path=stage113)

    assert result["decision"] == "AUDITABILITY_METRICS_BLOCKED_HARDWARE_COUNTS_REQUIRED"
    assert result["ready_window_count"] == 0
    assert "auditability_comparison_groups_incomplete" in result["window_records"][0]["missing_evidence"]


def test_stage137_rejects_missing_no_position_control_group(tmp_path) -> None:
    plans, stage136, stage113 = _ready_fixture(tmp_path)
    payload = json.loads(plans.read_text(encoding="utf-8"))
    packet_templates = payload[0]["steps"][1]["packet_templates"]
    payload[0]["steps"][1]["packet_templates"] = [
        record for record in packet_templates if record["encoding_family"] != "no_position_control"
    ]
    _write_json(plans, payload)

    result = run_stage137_evaluator(stage107_window_plans_path=plans, stage136_results_path=stage136, stage113_results_path=stage113)

    assert result["decision"] == "AUDITABILITY_METRICS_BLOCKED_HARDWARE_COUNTS_REQUIRED"
    assert result["ready_window_count"] == 0
    summary = result["window_records"][0]["comparison_summary"][0]
    assert summary["all_required_families_present"] is False
    assert summary["no_position_control_present"] is False
    assert "auditability_comparison_groups_incomplete" in result["window_records"][0]["missing_evidence"]


def test_stage137_outputs_are_written(tmp_path) -> None:
    plans, stage136, stage113 = _ready_fixture(tmp_path)
    result = run_stage137_evaluator(stage107_window_plans_path=plans, stage136_results_path=stage136, stage113_results_path=stage113)

    paths = write_stage137_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert manifest["auditability_advantage_count"] == 1
    assert "window_0" in summary
