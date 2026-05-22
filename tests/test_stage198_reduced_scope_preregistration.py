from __future__ import annotations

import json

from qrope.stage198_reduced_scope_preregistration import run_stage198_reduced_scope_preregistration, write_stage198_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _stage197(path, *, recommended_scope_id: str = "all_lanes_half_shots_2048") -> None:
    _write_json(
        path,
        {
            "decision": "REPLACEMENT_REDUCED_SCOPE_RECOMMENDED_BEFORE_CREDIT_ATTESTATION",
            "recommended_scope_id": recommended_scope_id,
            "scope_options": [
                {
                    "scope_id": "all_lanes_half_shots_2048",
                    "estimated_total_job_count": 324,
                    "estimated_total_shots": 659360,
                    "estimated_usd_at_10us_per_shot": 10.54976,
                    "estimated_usd_at_50us_per_shot": 52.7488,
                    "estimated_usd_at_100us_per_shot": 105.4976,
                    "row_count_per_packet": 16,
                    "shots_per_row": 2048,
                    "scaled_min_positional_margin_shot_quanta": 2.6190255,
                    "scaled_min_matched_null_margin_shot_quanta": 2.503077,
                }
            ],
        },
    )


def test_stage198_preregisters_reduced_scope_boundary(tmp_path) -> None:
    stage197 = tmp_path / "stage197.json"
    _stage197(stage197)

    result = run_stage198_reduced_scope_preregistration(stage197_results_path=stage197)

    assert result["decision"] == "REDUCED_SCOPE_PREREGISTERED_READY_FOR_COST_ATTESTATION_REVIEW"
    assert result["selected_scope_id"] == "all_lanes_half_shots_2048"
    assert result["selected_scope"]["shots_per_row"] == 2048
    boundary = result["interpretation_boundary"]
    assert boundary["pass_fail_policy"]["minimum_scaled_best_positional_margin_shot_quanta"] == 2.0
    assert boundary["pass_fail_policy"]["minimum_scaled_matched_null_margin_shot_quanta"] == 2.0
    assert "claiming equivalence to the full 4096-shot Stage190 package" in boundary["disallowed_interpretations"]
    assert result["no_hardware_submission"] is True


def test_stage198_blocks_scope_mismatch(tmp_path) -> None:
    stage197 = tmp_path / "stage197.json"
    _stage197(stage197, recommended_scope_id="all_lanes_scout_512")

    result = run_stage198_reduced_scope_preregistration(stage197_results_path=stage197)

    assert result["decision"] == "REDUCED_SCOPE_PREREGISTRATION_BLOCKED"
    assert "recommended_scope_mismatch" in result["blockers"]


def test_stage198_outputs_do_not_record_secrets_or_live_submit(tmp_path) -> None:
    stage197 = tmp_path / "stage197.json"
    _stage197(stage197)
    result = run_stage198_reduced_scope_preregistration(stage197_results_path=stage197)

    paths = write_stage198_outputs(result, tmp_path / "out")
    written = (tmp_path / "out" / "results.json").read_text(encoding="utf-8")
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert "IBM_QUANTUM_TOKEN" not in written
    assert "crn:v1" not in written
    assert "--allow-live-submit" not in written
    assert "--allow-live-submit" not in summary
