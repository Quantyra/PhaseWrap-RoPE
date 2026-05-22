from __future__ import annotations

import json

from qrope.stage179_current_ibm_hardware_path_disposition import (
    run_stage179_current_ibm_hardware_path_disposition,
    write_stage179_outputs,
)


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _sources(tmp_path):
    stage169 = tmp_path / "stage169.json"
    stage176 = tmp_path / "stage176.json"
    stage177 = tmp_path / "stage177.json"
    stage178 = tmp_path / "stage178.json"
    _write_json(
        stage169,
        {
            "decision": "TARGETED_IBM_PROBE_SCOPE_LOCKED_TO_STABLE_LANES",
            "stable_target_lanes": ["ibm_cx_seed314_rows16_shots4096", "ibm_product_seed314_rows16_shots4096"],
            "locked_lane_ids": ["ibm_cx_seed314_rows16_shots4096", "ibm_product_seed314_rows16_shots4096"],
            "approved_job_count": 328,
            "locked_total_shots": 1318720,
        },
    )
    _write_json(
        stage176,
        {
            "decision": "IBM_CREDIT_PROVIDER_RESOLUTION_HANDOFF_READY_FOR_HUMAN_CHECK",
            "credit_balance_verified": False,
        },
    )
    _write_json(
        stage177,
        {
            "decision": "IBM_BACKEND_INFORMED_SIM_DOES_NOT_SUPPORT_TARGETED_HARDWARE_RUN_YET",
            "primary_stable_target_count": 0,
            "proxy_stable_target_count": 0,
            "backend_snapshot_summary": {"backend": "ibm_fez"},
        },
    )
    _write_json(
        stage178,
        {
            "decision": "IBM_COHERENT_OFFSET_SENSITIVITY_DOES_NOT_RECOVER_TARGETED_SIGNAL",
            "stable_offset_count": 0,
            "locked_offset_record_count": 18,
            "signed_offsets_radians": [-0.04, 0.0, 0.04],
        },
    )
    return stage169, stage176, stage177, stage178


def test_stage179_archives_current_ibm_hardware_path_when_backend_informed_evidence_is_negative(tmp_path) -> None:
    stage169, stage176, stage177, stage178 = _sources(tmp_path)

    result = run_stage179_current_ibm_hardware_path_disposition(
        stage169_results_path=stage169,
        stage176_results_path=stage176,
        stage177_results_path=stage177,
        stage178_results_path=stage178,
    )

    assert result["decision"] == "CURRENT_IBM_HARDWARE_PATH_ARCHIVE_RECOMMENDED"
    assert result["disposition"] == "archive_current_328_job_ibm_run"
    assert result["locked_scope"]["approved_job_count"] == 328
    assert result["evidence_summary"]["stage178_stable_offset_count"] == 0
    assert result["no_hardware_submission"] is True


def test_stage179_blocks_when_required_stage_is_missing(tmp_path) -> None:
    stage169, stage176, stage177, stage178 = _sources(tmp_path)
    stage178.unlink()

    result = run_stage179_current_ibm_hardware_path_disposition(
        stage169_results_path=stage169,
        stage176_results_path=stage176,
        stage177_results_path=stage177,
        stage178_results_path=stage178,
    )

    assert result["decision"] == "CURRENT_IBM_HARDWARE_PATH_DISPOSITION_INCOMPLETE"
    assert "missing_source_artifacts" in result["blockers"]


def test_stage179_outputs_do_not_record_secrets_or_live_submit(tmp_path) -> None:
    stage169, stage176, stage177, stage178 = _sources(tmp_path)
    result = run_stage179_current_ibm_hardware_path_disposition(
        stage169_results_path=stage169,
        stage176_results_path=stage176,
        stage177_results_path=stage177,
        stage178_results_path=stage178,
    )

    paths = write_stage179_outputs(result, tmp_path / "out")
    written = (tmp_path / "out" / "results.json").read_text(encoding="utf-8")
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert "IBM_QUANTUM_TOKEN" not in written
    assert "crn:v1" not in written
    assert "--allow-live-submit" not in written
    assert "--allow-live-submit" not in summary
