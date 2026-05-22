from __future__ import annotations

import json

from qrope.stage200_reduced_scope_attestation_intake import (
    REQUIRED_ATTESTATION_PHRASE,
    required_attestation_phrase_for_budget,
    run_stage200_reduced_scope_attestation_intake,
    write_stage200_outputs,
)


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _stage199(path, *, budget_cap_usd: float = 25.0) -> None:
    _write_json(
        path,
        {
            "decision": "REDUCED_SCOPE_ATTESTATION_READY_FOR_USER_REVIEW_NOT_LIVE",
            "scope_id": "all_lanes_half_shots_2048",
            "hardware_scope_label": "reduced_precision_all_lanes_2048_shots_v1",
            "estimated_total_job_count": 324,
            "estimated_total_shots": 659360,
            "budget_cap_usd": budget_cap_usd,
            "break_even_microseconds_per_shot": 23.69722154816792,
        },
    )


def test_stage200_requires_exact_reduced_scope_attestation_phrase(tmp_path) -> None:
    stage199 = tmp_path / "stage199.json"
    _stage199(stage199)

    result = run_stage200_reduced_scope_attestation_intake(stage199_results_path=stage199)

    assert result["decision"] == "REDUCED_SCOPE_ATTESTATION_INTAKE_AWAITING_EXACT_PHRASE"
    assert result["required_attestation_phrase"] == REQUIRED_ATTESTATION_PHRASE
    assert result["human_credit_allowance_verified"] is False
    assert "exact_reduced_scope_attestation_phrase_required" in result["blockers"]
    assert result["no_hardware_submission"] is True


def test_stage200_rejects_ambiguous_or_wrong_phrase(tmp_path) -> None:
    stage199 = tmp_path / "stage199.json"
    _stage199(stage199)

    result = run_stage200_reduced_scope_attestation_intake(
        stage199_results_path=stage199,
        provided_attestation_phrase="yes",
    )

    assert result["decision"] == "REDUCED_SCOPE_ATTESTATION_INTAKE_AWAITING_EXACT_PHRASE"
    assert result["attestation_phrase_matches"] is False
    exact_item = [item for item in result["intake_items"] if item["item_id"] == "exact_attestation_phrase"][0]
    assert exact_item["status"] == "mismatched"


def test_stage200_accepts_exact_phrase_without_live_submission(tmp_path) -> None:
    stage199 = tmp_path / "stage199.json"
    _stage199(stage199)

    result = run_stage200_reduced_scope_attestation_intake(
        stage199_results_path=stage199,
        provided_attestation_phrase=REQUIRED_ATTESTATION_PHRASE,
    )

    assert result["decision"] == "REDUCED_SCOPE_CREDIT_ATTESTATION_ACCEPTED_READY_FOR_EXACT_APPROVAL_REVIEW"
    assert result["human_credit_allowance_verified"] is True
    assert result["attestation_phrase_matches"] is True
    assert result["live_submit_command_created"] is False
    assert result["runnable_commands_recorded"] is False


def test_stage200_phrase_tracks_recorded_budget_cap(tmp_path) -> None:
    stage199 = tmp_path / "stage199.json"
    _stage199(stage199, budget_cap_usd=100.0)

    result = run_stage200_reduced_scope_attestation_intake(
        stage199_results_path=stage199,
        provided_attestation_phrase=required_attestation_phrase_for_budget(100.0),
    )

    assert result["required_attestation_phrase"] == "ATTEST IBM CREDIT FOR REDUCED SCOPE STAGE199 WITH 100 USD CAP"
    assert result["attestation_phrase_matches"] is True
    assert result["human_credit_allowance_verified"] is True


def test_stage200_outputs_do_not_record_secrets_or_live_submit(tmp_path) -> None:
    stage199 = tmp_path / "stage199.json"
    _stage199(stage199)
    result = run_stage200_reduced_scope_attestation_intake(stage199_results_path=stage199)

    paths = write_stage200_outputs(result, tmp_path / "out")
    written = (tmp_path / "out" / "results.json").read_text(encoding="utf-8")
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert "IBM_QUANTUM_TOKEN" not in written
    assert "crn:v1" not in written
    assert "--allow-live-submit" not in written
    assert "--allow-live-submit" not in summary
