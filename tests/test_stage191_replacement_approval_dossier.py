from __future__ import annotations

import json

from qrope.stage191_replacement_approval_dossier import run_stage191_replacement_approval_dossier, write_stage191_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _sources(tmp_path):
    stage176 = tmp_path / "stage176.json"
    stage188 = tmp_path / "stage188.json"
    stage189 = tmp_path / "stage189.json"
    stage190 = tmp_path / "stage190.json"
    _write_json(stage176, {"credit_balance_verified": False})
    _write_json(stage188, {"decision": "REPLACEMENT_SEMANTICS_SIM_SUPPORTS_HARDWARE_REOPEN", "semantics_id": "matched_nonzero_null_noise_sensitivity_v1", "reopen_candidate_count": 5})
    _write_json(stage189, {"decision": "REPLACEMENT_HARDWARE_REVIEW_REOPENED_BUT_NOT_READY_FOR_LIVE_RUN"})
    _write_json(
        stage190,
        {
            "decision": "REPLACEMENT_EXECUTION_PACKAGE_PREPARED_COUNTS_AND_CALIBRATION_REQUIRED",
            "selected_lanes": ["ibm_product_seed314_rows16_shots4096"],
            "selected_lane_count": 1,
            "packet_template_count": 5,
            "estimated_packet_row_job_count": 80,
            "estimated_calibration_job_count": 4,
            "estimated_total_job_count": 84,
            "execution_templates": [{"shot_count": 1000, "raw_counts_by_row": [{}, {}]}],
            "calibration_template": {"shots_per_state": 100, "raw_counts_by_state": [{}, {}, {}, {}]},
        },
    )
    return stage176, stage188, stage189, stage190


def test_stage191_builds_human_review_dossier_not_live(tmp_path) -> None:
    stage176, stage188, stage189, stage190 = _sources(tmp_path)

    result = run_stage191_replacement_approval_dossier(
        stage176_results_path=stage176,
        stage188_results_path=stage188,
        stage189_results_path=stage189,
        stage190_results_path=stage190,
    )

    assert result["decision"] == "REPLACEMENT_APPROVAL_DOSSIER_READY_FOR_HUMAN_REVIEW_NOT_LIVE"
    assert result["estimated_total_shots"] == 2400
    assert result["no_hardware_submission"] is True
    assert result["runnable_commands_recorded"] is False
    assert "replacement_approval_requirements_open" in result["blockers"]


def test_stage191_blocks_when_stage190_not_prepared(tmp_path) -> None:
    stage176, stage188, stage189, stage190 = _sources(tmp_path)
    _write_json(stage190, {"decision": "NOPE", "execution_templates": [], "calibration_template": {}})

    result = run_stage191_replacement_approval_dossier(
        stage176_results_path=stage176,
        stage188_results_path=stage188,
        stage189_results_path=stage189,
        stage190_results_path=stage190,
    )

    assert result["decision"] == "REPLACEMENT_APPROVAL_DOSSIER_BLOCKED"
    assert "stage190_execution_package_not_prepared" in result["blockers"]


def test_stage191_outputs_do_not_record_secrets_or_live_submit(tmp_path) -> None:
    stage176, stage188, stage189, stage190 = _sources(tmp_path)
    result = run_stage191_replacement_approval_dossier(
        stage176_results_path=stage176,
        stage188_results_path=stage188,
        stage189_results_path=stage189,
        stage190_results_path=stage190,
    )

    paths = write_stage191_outputs(result, tmp_path / "out")
    written = (tmp_path / "out" / "results.json").read_text(encoding="utf-8")
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert "IBM_QUANTUM_TOKEN" not in written
    assert "crn:v1" not in written
    assert "--allow-live-submit" not in written
    assert "--allow-live-submit" not in summary
