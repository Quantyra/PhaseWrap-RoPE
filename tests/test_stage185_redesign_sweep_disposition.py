from __future__ import annotations

import json

from qrope.stage185_redesign_sweep_disposition import run_stage185_redesign_sweep_disposition, write_stage185_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _sources(tmp_path):
    stage181 = tmp_path / "stage181.json"
    stage182 = tmp_path / "stage182.json"
    stage183 = tmp_path / "stage183.json"
    stage184 = tmp_path / "stage184.json"
    _write_json(
        stage181,
        {
            "decision": "FIXED_WIDTH_TARGET_REDESIGN_PLAN_READY",
            "design_families": [
                {"family_id": "pw_balanced_phase_window_v1"},
                {"family_id": "pw_contrast_amplified_delta_v1"},
                {"family_id": "pw_error_orthogonalized_components_v1"},
            ],
        },
    )
    for path, family, decision in (
        (stage182, "pw_balanced_phase_window_v1", "BALANCED_PHASE_WINDOW_CANDIDATE_DOES_NOT_SUPPORT_HARDWARE_REOPEN"),
        (stage183, "pw_contrast_amplified_delta_v1", "CONTRAST_AMPLIFIED_DELTA_CANDIDATE_DOES_NOT_SUPPORT_HARDWARE_REOPEN"),
        (stage184, "pw_error_orthogonalized_components_v1", "ERROR_ORTHOGONALIZED_COMPONENTS_CANDIDATE_DOES_NOT_SUPPORT_HARDWARE_REOPEN"),
    ):
        _write_json(
            path,
            {
                "design_family_id": family,
                "decision": decision,
                "status": "completed",
                "packet_count": 30,
                "comparison_group_count": 12,
                "reopen_candidate_count": 0,
            },
        )
    return stage181, stage182, stage183, stage184


def test_stage185_disposes_exhausted_redesign_sweep(tmp_path) -> None:
    stage181, stage182, stage183, stage184 = _sources(tmp_path)

    result = run_stage185_redesign_sweep_disposition(
        stage181_results_path=stage181,
        stage182_results_path=stage182,
        stage183_results_path=stage183,
        stage184_results_path=stage184,
    )

    assert result["decision"] == "REDESIGN_SWEEP_EXHAUSTED_NO_HARDWARE_REOPEN"
    assert result["hardware_reopen_candidate_count"] == 0
    assert result["total_packet_count"] == 90
    assert result["total_comparison_group_count"] == 36
    assert result["no_hardware_submission"] is True


def test_stage185_blocks_when_candidate_missing(tmp_path) -> None:
    stage181, stage182, stage183, stage184 = _sources(tmp_path)
    stage184.unlink()

    result = run_stage185_redesign_sweep_disposition(
        stage181_results_path=stage181,
        stage182_results_path=stage182,
        stage183_results_path=stage183,
        stage184_results_path=stage184,
    )

    assert result["decision"] == "REDESIGN_SWEEP_DISPOSITION_INCOMPLETE"
    assert "missing_source_artifacts" in result["blockers"]


def test_stage185_outputs_do_not_record_secrets_or_live_submit(tmp_path) -> None:
    stage181, stage182, stage183, stage184 = _sources(tmp_path)
    result = run_stage185_redesign_sweep_disposition(
        stage181_results_path=stage181,
        stage182_results_path=stage182,
        stage183_results_path=stage183,
        stage184_results_path=stage184,
    )

    paths = write_stage185_outputs(result, tmp_path / "out")
    written = (tmp_path / "out" / "results.json").read_text(encoding="utf-8")
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert "IBM_QUANTUM_TOKEN" not in written
    assert "crn:v1" not in written
    assert "--allow-live-submit" not in written
    assert "--allow-live-submit" not in summary
