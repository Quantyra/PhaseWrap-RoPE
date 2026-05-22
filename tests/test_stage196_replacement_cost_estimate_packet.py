from __future__ import annotations

import json

from qrope.stage196_replacement_cost_estimate_packet import run_stage196_replacement_cost_estimate_packet, write_stage196_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _stage194(path, *, shots: int = 1_314_720, budget_cap: float = 25.0) -> None:
    _write_json(
        path,
        {
            "decision": "REPLACEMENT_CREDIT_ALLOWANCE_READY_FOR_HUMAN_ATTESTATION_NOT_LIVE",
            "estimated_total_job_count": 324,
            "estimated_total_shots": shots,
            "budget_cap_usd": budget_cap,
        },
    )


def test_stage196_builds_explicit_cost_estimate_before_attestation(tmp_path) -> None:
    stage194 = tmp_path / "stage194.json"
    _stage194(stage194)

    result = run_stage196_replacement_cost_estimate_packet(stage194_results_path=stage194)

    assert result["decision"] == "REPLACEMENT_COST_ESTIMATE_READY_BUDGET_LIKELY_TIGHT_NOT_LIVE"
    assert result["budget_quantum_seconds_at_doc_rate"] == 15.625
    assert round(result["break_even_microseconds_per_shot"], 2) == 11.88
    assert "budget_likely_tight_for_full_run" in result["blockers"]
    assert result["manual_attestation_prompt_required"] is True
    assert "1,314,720" in result["manual_attestation_prompt"] or "1314720" in result["manual_attestation_prompt"]
    assert result["no_hardware_submission"] is True


def test_stage196_scenario_estimates_cross_budget_threshold(tmp_path) -> None:
    stage194 = tmp_path / "stage194.json"
    _stage194(stage194)

    result = run_stage196_replacement_cost_estimate_packet(stage194_results_path=stage194)
    scenarios = {record["microseconds_per_shot"]: record for record in result["scenario_estimates"]}

    assert scenarios[10.0]["within_budget_cap"] is True
    assert scenarios[25.0]["within_budget_cap"] is False
    assert scenarios[50.0]["estimated_usd"] > 100.0


def test_stage196_blocks_when_exposure_or_budget_missing(tmp_path) -> None:
    stage194 = tmp_path / "stage194.json"
    _stage194(stage194, shots=0, budget_cap=0.0)

    result = run_stage196_replacement_cost_estimate_packet(stage194_results_path=stage194)

    assert result["decision"] == "REPLACEMENT_COST_ESTIMATE_PACKET_BLOCKED"
    assert "replacement_exposure_missing" in result["blockers"]
    assert "local_budget_cap_missing" in result["blockers"]


def test_stage196_outputs_do_not_record_secrets_or_live_submit(tmp_path) -> None:
    stage194 = tmp_path / "stage194.json"
    _stage194(stage194)
    result = run_stage196_replacement_cost_estimate_packet(stage194_results_path=stage194)

    paths = write_stage196_outputs(result, tmp_path / "out")
    written = (tmp_path / "out" / "results.json").read_text(encoding="utf-8")
    scenarios = (tmp_path / "out" / "scenarios.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv", "scenarios_csv"}
    assert "IBM_QUANTUM_TOKEN" not in written
    assert "crn:v1" not in written
    assert "--allow-live-submit" not in written
    assert "--allow-live-submit" not in scenarios
