from __future__ import annotations

import json

from qrope.stage181_fixed_width_target_redesign_plan import run_stage181_fixed_width_target_redesign_plan, write_stage181_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _sources(tmp_path):
    stage177 = tmp_path / "stage177.json"
    stage179 = tmp_path / "stage179.json"
    stage180 = tmp_path / "stage180.json"
    _write_json(
        stage177,
        {
            "noise_models": [
                {"noise_model_id": "ibm_backend_median_stochastic"},
                {"noise_model_id": "ibm_backend_p75_stochastic"},
                {"noise_model_id": "coherent_proxy"},
            ]
        },
    )
    _write_json(stage179, {"decision": "CURRENT_IBM_HARDWARE_PATH_ARCHIVE_RECOMMENDED"})
    _write_json(stage180, {"decision": "EXISTING_SURFACE_HAS_NO_IBM_INFORMED_REOPEN_CANDIDATE"})
    return stage177, stage179, stage180


def test_stage181_redesign_plan_ready_after_archive_and_existing_surface_exhaustion(tmp_path) -> None:
    stage177, stage179, stage180 = _sources(tmp_path)

    result = run_stage181_fixed_width_target_redesign_plan(
        stage177_results_path=stage177,
        stage179_results_path=stage179,
        stage180_results_path=stage180,
    )

    assert result["decision"] == "FIXED_WIDTH_TARGET_REDESIGN_PLAN_READY"
    assert result["design_family_count"] == 3
    assert result["current_path_status"]["current_ibm_328_job_run_archived"] is True
    assert result["hardware_reopen_thresholds"]["min_independent_seed_pairs"] == 2
    assert result["no_hardware_submission"] is True


def test_stage181_blocks_when_current_path_not_archived(tmp_path) -> None:
    stage177, stage179, stage180 = _sources(tmp_path)
    _write_json(stage179, {"decision": "CURRENT_IBM_HARDWARE_PATH_REQUIRES_HUMAN_REVIEW"})

    result = run_stage181_fixed_width_target_redesign_plan(
        stage177_results_path=stage177,
        stage179_results_path=stage179,
        stage180_results_path=stage180,
    )

    assert result["decision"] == "FIXED_WIDTH_TARGET_REDESIGN_PLAN_INCOMPLETE"
    assert "stage179_current_ibm_path_not_archived" in result["blockers"]


def test_stage181_outputs_do_not_record_secrets_or_live_submit(tmp_path) -> None:
    stage177, stage179, stage180 = _sources(tmp_path)
    result = run_stage181_fixed_width_target_redesign_plan(
        stage177_results_path=stage177,
        stage179_results_path=stage179,
        stage180_results_path=stage180,
    )

    paths = write_stage181_outputs(result, tmp_path / "out")
    written = (tmp_path / "out" / "results.json").read_text(encoding="utf-8")
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert "IBM_QUANTUM_TOKEN" not in written
    assert "crn:v1" not in written
    assert "--allow-live-submit" not in written
    assert "--allow-live-submit" not in summary
