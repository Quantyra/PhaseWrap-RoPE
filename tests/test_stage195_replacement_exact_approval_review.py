from __future__ import annotations

import json

from qrope.stage189_replacement_hardware_readiness_review import APPROVAL_PHRASE
from qrope.stage195_replacement_exact_approval_review import run_stage195_replacement_exact_approval_review, write_stage195_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _stage194(path, *, credit_verified: bool = False) -> None:
    decision = (
        "REPLACEMENT_CREDIT_ALLOWANCE_VERIFIED_READY_FOR_EXACT_APPROVAL_REVIEW"
        if credit_verified
        else "REPLACEMENT_CREDIT_ALLOWANCE_READY_FOR_HUMAN_ATTESTATION_NOT_LIVE"
    )
    _write_json(
        path,
        {
            "decision": decision,
            "human_credit_allowance_verified": credit_verified,
            "estimated_total_job_count": 324,
            "estimated_total_shots": 1314720,
            "budget_cap_usd": 25.0,
        },
    )


def test_stage195_blocks_exact_phrase_until_credit_attestation_is_verified(tmp_path) -> None:
    stage194 = tmp_path / "stage194.json"
    _stage194(stage194, credit_verified=False)

    result = run_stage195_replacement_exact_approval_review(
        stage194_results_path=stage194,
        provided_approval_phrase=APPROVAL_PHRASE,
    )

    assert result["decision"] == "REPLACEMENT_EXACT_APPROVAL_REVIEW_BLOCKED_CREDIT_ATTESTATION_REQUIRED"
    assert result["approval_phrase_matches"] is False
    assert "credit_allowance_not_verified" in result["blockers"]
    assert result["no_hardware_submission"] is True
    assert result["live_submit_command_created"] is False


def test_stage195_rejects_missing_or_wrong_phrase_after_credit_attestation(tmp_path) -> None:
    stage194 = tmp_path / "stage194.json"
    _stage194(stage194, credit_verified=True)

    result = run_stage195_replacement_exact_approval_review(
        stage194_results_path=stage194,
        provided_approval_phrase="APPROVE SOMETHING ELSE",
    )

    assert result["decision"] == "REPLACEMENT_EXACT_APPROVAL_REVIEW_BLOCKED"
    assert result["approval_phrase_matches"] is False
    assert "exact_replacement_approval_phrase_missing_or_mismatched" in result["blockers"]


def test_stage195_accepts_exact_phrase_only_after_credit_attestation(tmp_path) -> None:
    stage194 = tmp_path / "stage194.json"
    _stage194(stage194, credit_verified=True)

    result = run_stage195_replacement_exact_approval_review(
        stage194_results_path=stage194,
        provided_approval_phrase=APPROVAL_PHRASE,
    )

    assert result["decision"] == "REPLACEMENT_EXACT_APPROVAL_ACCEPTED_READY_FOR_LIVE_RUNNER_PREPARATION_REVIEW"
    assert result["approval_phrase_matches"] is True
    assert result["blockers"] == []
    assert result["no_hardware_submission"] is True
    assert result["runnable_commands_recorded"] is False


def test_stage195_outputs_do_not_record_secrets_or_live_submit(tmp_path) -> None:
    stage194 = tmp_path / "stage194.json"
    _stage194(stage194, credit_verified=False)
    result = run_stage195_replacement_exact_approval_review(
        stage194_results_path=stage194,
        provided_approval_phrase=APPROVAL_PHRASE,
    )

    paths = write_stage195_outputs(result, tmp_path / "out")
    written = (tmp_path / "out" / "results.json").read_text(encoding="utf-8")
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert "IBM_QUANTUM_TOKEN" not in written
    assert "crn:v1" not in written
    assert "--allow-live-submit" not in written
    assert "--allow-live-submit" not in summary
