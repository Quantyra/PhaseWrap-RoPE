from __future__ import annotations

import json

from qrope.stage197_replacement_cost_constrained_scope_review import (
    run_stage197_replacement_cost_constrained_scope_review,
    write_stage197_outputs,
)


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _sources(tmp_path):
    stage188 = tmp_path / "stage188.json"
    stage196 = tmp_path / "stage196.json"
    _write_json(
        stage188,
        {
            "decision": "REPLACEMENT_SEMANTICS_SIM_SUPPORTS_HARDWARE_REOPEN",
            "candidate_records": [
                {
                    "provider_family": "ibm",
                    "reopen_candidate": True,
                    "min_positional_margin_shot_quanta": 5.238051,
                    "min_matched_null_margin_shot_quanta": 8.870596,
                },
                {
                    "provider_family": "ibm",
                    "reopen_candidate": True,
                    "min_positional_margin_shot_quanta": 22.502149,
                    "min_matched_null_margin_shot_quanta": 5.006154,
                },
            ],
        },
    )
    _write_json(
        stage196,
        {
            "decision": "REPLACEMENT_COST_ESTIMATE_READY_BUDGET_LIKELY_TIGHT_NOT_LIVE",
            "budget_cap_usd": 25.0,
        },
    )
    return stage188, stage196


def test_stage197_recommends_half_shot_scope_before_attestation(tmp_path) -> None:
    stage188, stage196 = _sources(tmp_path)

    result = run_stage197_replacement_cost_constrained_scope_review(
        stage188_results_path=stage188,
        stage196_results_path=stage196,
    )

    assert result["decision"] == "REPLACEMENT_REDUCED_SCOPE_RECOMMENDED_BEFORE_CREDIT_ATTESTATION"
    assert result["recommended_scope_id"] == "all_lanes_half_shots_2048"
    assert "full_scope_exceeds_budget_at_50us_scenario" in result["blockers"]
    half = [scope for scope in result["scope_options"] if scope["scope_id"] == "all_lanes_half_shots_2048"][0]
    assert half["estimated_total_shots"] == 659360
    assert round(half["estimated_usd_at_10us_per_shot"], 2) == 10.55
    assert round(half["scaled_min_positional_margin_shot_quanta"], 3) == 2.619
    assert result["no_hardware_submission"] is True


def test_stage197_marks_scout_scope_not_claim_capable(tmp_path) -> None:
    stage188, stage196 = _sources(tmp_path)

    result = run_stage197_replacement_cost_constrained_scope_review(
        stage188_results_path=stage188,
        stage196_results_path=stage196,
    )
    scout = [scope for scope in result["scope_options"] if scope["scope_id"] == "all_lanes_scout_512"][0]

    assert scout["evidentiary_status"] == "scouting_only_not_claim_capable"
    assert scout["estimated_total_shots"] == 167840
    assert scout["scaled_min_positional_margin_shot_quanta"] < 1.0


def test_stage197_blocks_when_positive_sim_or_cost_packet_missing(tmp_path) -> None:
    stage188, stage196 = _sources(tmp_path)
    _write_json(stage188, {"decision": "NOPE", "candidate_records": []})

    result = run_stage197_replacement_cost_constrained_scope_review(
        stage188_results_path=stage188,
        stage196_results_path=stage196,
    )

    assert result["decision"] == "REPLACEMENT_COST_CONSTRAINED_SCOPE_REVIEW_BLOCKED"
    assert "stage188_replacement_sim_not_positive" in result["blockers"]


def test_stage197_outputs_do_not_record_secrets_or_live_submit(tmp_path) -> None:
    stage188, stage196 = _sources(tmp_path)
    result = run_stage197_replacement_cost_constrained_scope_review(
        stage188_results_path=stage188,
        stage196_results_path=stage196,
    )

    paths = write_stage197_outputs(result, tmp_path / "out")
    written = (tmp_path / "out" / "results.json").read_text(encoding="utf-8")
    scope_csv = (tmp_path / "out" / "scope_options.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv", "scope_csv"}
    assert "IBM_QUANTUM_TOKEN" not in written
    assert "crn:v1" not in written
    assert "--allow-live-submit" not in written
    assert "--allow-live-submit" not in scope_csv
