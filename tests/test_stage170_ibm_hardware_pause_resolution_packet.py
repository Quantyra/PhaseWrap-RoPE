from __future__ import annotations

import json

from qrope.stage170_ibm_hardware_pause_resolution_packet import run_stage170_pause_packet, write_stage170_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _sources(tmp_path):
    stage159 = tmp_path / "stage159.json"
    stage161 = tmp_path / "stage161.json"
    stage162 = tmp_path / "stage162.json"
    stage163 = tmp_path / "stage163.json"
    stage169 = tmp_path / "stage169.json"
    _write_json(
        stage159,
        {
            "decision": "FIRST_PROVIDER_BACKEND_PREFLIGHT_READY_AWAITING_APPROVAL",
            "backend_lookup_ready": True,
            "backend_metadata": {"pending_jobs": 3},
        },
    )
    _write_json(
        stage161,
        {
            "decision": "FIRST_PROVIDER_EXPOSURE_PACKET_READY_AWAITING_APPROVAL",
            "job_count": 328,
            "total_shots": 1318720,
            "missing_result_record_count": 328,
            "runnable_commands_recorded": False,
        },
    )
    _write_json(
        stage162,
        {
            "decision": "FIRST_PROVIDER_APPROVAL_DOSSIER_READY_FOR_HUMAN_GO_NO_GO",
            "first_unlock_provider": "ibm_runtime",
            "approval_phrase_required": "APPROVE IBM RUNTIME STAGE133 LIVE RUN",
            "approval_state": "awaiting_exact_phrase",
            "credit_balance_verified": False,
            "runnable_commands_recorded": False,
            "secret_values_recorded": False,
        },
    )
    _write_json(
        stage163,
        {
            "decision": "FIRST_PROVIDER_PRERUN_LOCK_READY_AWAITING_APPROVAL",
            "approved_job_count": 328,
            "locked_total_shots": 1318720,
        },
    )
    _write_json(
        stage169,
        {
            "decision": "TARGETED_IBM_PROBE_SCOPE_LOCKED_TO_STABLE_LANES",
            "stable_target_lanes": ["ibm_cx_seed314_rows16_shots4096", "ibm_product_seed314_rows16_shots4096"],
            "excluded_recommended_lanes": [
                "braket_cx_seed2718_rows8_shots1000",
                "braket_product_seed2718_rows8_shots1000",
                "ibm_cx_seed577_rows16_shots4096",
                "ibm_product_seed577_rows16_shots4096",
            ],
            "locked_lane_count": 2,
        },
    )
    return stage159, stage161, stage162, stage163, stage169


def test_stage170_pauses_for_credit_provider_resolution_without_submitting(tmp_path) -> None:
    stage159, stage161, stage162, stage163, stage169 = _sources(tmp_path)

    result = run_stage170_pause_packet(
        stage159_results_path=stage159,
        stage161_results_path=stage161,
        stage162_results_path=stage162,
        stage163_results_path=stage163,
        stage169_results_path=stage169,
    )

    assert result["decision"] == "IBM_HARDWARE_PAUSE_READY_FOR_CREDIT_PROVIDER_RESOLUTION"
    assert result["no_hardware_submission"] is True
    assert result["credit_balance_verified"] is False
    assert result["locked_job_count"] == 328
    assert result["locked_total_shots"] == 1318720
    assert result["stage169_stable_target_lanes"] == ["ibm_cx_seed314_rows16_shots4096", "ibm_product_seed314_rows16_shots4096"]
    assert "ibm_product_seed577_rows16_shots4096" in result["stage169_excluded_recommended_lanes"]
    assert result["blockers"] == []


def test_stage170_blocks_on_wrong_scope_decision(tmp_path) -> None:
    stage159, stage161, stage162, stage163, stage169 = _sources(tmp_path)
    _write_json(stage169, {"decision": "TARGETED_PROBE_SCOPE_SELECTION_BLOCKED", "stable_target_lanes": []})

    result = run_stage170_pause_packet(
        stage159_results_path=stage159,
        stage161_results_path=stage161,
        stage162_results_path=stage162,
        stage163_results_path=stage163,
        stage169_results_path=stage169,
    )

    assert result["decision"] == "IBM_HARDWARE_PAUSE_RESOLUTION_BLOCKED"
    assert "stage169_not_ready" in result["blockers"]
    assert "stage169_no_stable_target_lanes" in result["blockers"]


def test_stage170_outputs_do_not_record_secrets_or_live_commands(tmp_path) -> None:
    stage159, stage161, stage162, stage163, stage169 = _sources(tmp_path)
    result = run_stage170_pause_packet(
        stage159_results_path=stage159,
        stage161_results_path=stage161,
        stage162_results_path=stage162,
        stage163_results_path=stage163,
        stage169_results_path=stage169,
    )

    paths = write_stage170_outputs(result, tmp_path / "out")
    written = (tmp_path / "out" / "results.json").read_text(encoding="utf-8")
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert "--allow-live-submit" not in written
    assert "--allow-live-submit" not in summary
    assert "IBM_QUANTUM_TOKEN" not in written
    assert "crn:v1" not in written
