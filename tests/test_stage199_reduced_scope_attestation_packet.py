from __future__ import annotations

import json

from qrope.stage199_reduced_scope_attestation_packet import run_stage199_reduced_scope_attestation_packet, write_stage199_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _stage198(path) -> None:
    _write_json(
        path,
        {
            "decision": "REDUCED_SCOPE_PREREGISTERED_READY_FOR_COST_ATTESTATION_REVIEW",
            "selected_scope": {
                "scope_id": "all_lanes_half_shots_2048",
                "estimated_total_job_count": 324,
                "estimated_total_shots": 659360,
                "shots_per_row": 2048,
            },
            "interpretation_boundary": {
                "hardware_scope_label": "reduced_precision_all_lanes_2048_shots_v1",
                "pass_fail_policy": {
                    "lower_precision_caveat": "Reduced precision caveat.",
                },
            },
        },
    )


def test_stage199_builds_reduced_scope_attestation_prompt(tmp_path) -> None:
    stage198 = tmp_path / "stage198.json"
    _stage198(stage198)

    result = run_stage199_reduced_scope_attestation_packet(stage198_results_path=stage198)

    assert result["decision"] == "REDUCED_SCOPE_ATTESTATION_READY_FOR_USER_REVIEW_NOT_LIVE"
    assert result["estimated_total_shots"] == 659360
    assert result["break_even_microseconds_per_shot"] > 23.6
    assert result["break_even_microseconds_per_shot"] < 23.8
    assert "human_credit_allowance_attestation_required" in result["blockers"]
    assert result["manual_attestation_prompt_required"] is True
    assert "659360" in result["manual_attestation_prompt"]
    assert result["no_hardware_submission"] is True


def test_stage199_records_human_credit_attestation_without_exact_approval(tmp_path) -> None:
    stage198 = tmp_path / "stage198.json"
    _stage198(stage198)

    result = run_stage199_reduced_scope_attestation_packet(
        stage198_results_path=stage198,
        human_credit_allowance_verified=True,
    )

    assert result["decision"] == "REDUCED_SCOPE_CREDIT_ATTESTED_READY_FOR_EXACT_APPROVAL_REVIEW"
    assert result["human_credit_allowance_verified"] is True
    assert result["manual_attestation_prompt_required"] is False
    live_item = [item for item in result["attestation_items"] if item["item_id"] == "live_execution_boundary"][0]
    assert live_item["status"] == "live_run_disallowed"
    assert result["runnable_commands_recorded"] is False


def test_stage199_scenario_estimates_for_reduced_scope(tmp_path) -> None:
    stage198 = tmp_path / "stage198.json"
    _stage198(stage198)

    result = run_stage199_reduced_scope_attestation_packet(stage198_results_path=stage198)
    scenarios = {record["microseconds_per_shot"]: record for record in result["scenario_estimates"]}

    assert round(scenarios[10.0]["estimated_usd"], 2) == 10.55
    assert round(scenarios[25.0]["estimated_usd"], 2) == 26.37
    assert scenarios[10.0]["within_25_usd_cap"] is True
    assert scenarios[25.0]["within_25_usd_cap"] is False


def test_stage199_outputs_do_not_record_secrets_or_live_submit(tmp_path) -> None:
    stage198 = tmp_path / "stage198.json"
    _stage198(stage198)
    result = run_stage199_reduced_scope_attestation_packet(stage198_results_path=stage198)

    paths = write_stage199_outputs(result, tmp_path / "out")
    written = (tmp_path / "out" / "results.json").read_text(encoding="utf-8")
    scenarios = (tmp_path / "out" / "scenarios.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv", "scenarios_csv"}
    assert "IBM_QUANTUM_TOKEN" not in written
    assert "crn:v1" not in written
    assert "--allow-live-submit" not in written
    assert "--allow-live-submit" not in scenarios
