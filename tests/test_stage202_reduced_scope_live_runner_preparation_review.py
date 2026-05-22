from __future__ import annotations

import json

from qrope.stage202_reduced_scope_live_runner_preparation_review import (
    run_stage202_reduced_scope_live_runner_preparation_review,
    write_stage202_outputs,
)


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _stage201(path, *, accepted: bool = False) -> None:
    _write_json(
        path,
        {
            "decision": (
                "REDUCED_SCOPE_EXACT_APPROVAL_ACCEPTED_READY_FOR_LIVE_RUNNER_PREPARATION_REVIEW"
                if accepted
                else "REDUCED_SCOPE_EXACT_APPROVAL_REVIEW_BLOCKED_CREDIT_ATTESTATION_REQUIRED"
            ),
            "human_credit_allowance_verified": accepted,
            "approval_phrase_matches": accepted,
            "budget_cap_usd": 25.0,
        },
    )


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
                "packet_row_job_count": 320,
                "calibration_job_count": 4,
            },
            "interpretation_boundary": {
                "hardware_scope_label": "reduced_precision_all_lanes_2048_shots_v1",
                "shots_per_row": 2048,
                "calibration_states": ["00", "01", "10", "11"],
                "calibration_shots_per_state": 1000,
            },
        },
    )


def _stage193(path, *, ready: bool = True) -> None:
    _write_json(
        path,
        {
            "decision": (
                "REPLACEMENT_READ_ONLY_BACKEND_REFRESH_READY_CREDIT_AND_APPROVAL_STILL_REQUIRED"
                if ready
                else "REPLACEMENT_READ_ONLY_BACKEND_REFRESH_BLOCKED"
            ),
            "backend_lookup_ready": ready,
            "backend_metadata": {
                "backend": "ibm_fez",
                "operational": ready,
                "pending_jobs": 16,
            },
        },
    )


def test_stage202_blocks_when_stage201_exact_approval_not_accepted(tmp_path) -> None:
    stage201 = tmp_path / "stage201.json"
    stage198 = tmp_path / "stage198.json"
    stage193 = tmp_path / "stage193.json"
    _stage201(stage201, accepted=False)
    _stage198(stage198)
    _stage193(stage193)

    result = run_stage202_reduced_scope_live_runner_preparation_review(
        stage201_results_path=stage201,
        stage198_results_path=stage198,
        stage193_results_path=stage193,
    )

    assert result["decision"] == "REDUCED_SCOPE_LIVE_RUNNER_PREPARATION_REVIEW_BLOCKED_APPROVAL_OR_PACKAGE_REQUIRED"
    assert "stage201_exact_reduced_scope_approval_not_accepted" in result["blockers"]
    assert result["reduced_scope_execution_package_created"] is False
    assert result["live_submit_command_created"] is False
    assert result["no_hardware_submission"] is True


def test_stage202_after_approval_still_requires_package_and_result_contract(tmp_path) -> None:
    stage201 = tmp_path / "stage201.json"
    stage198 = tmp_path / "stage198.json"
    stage193 = tmp_path / "stage193.json"
    _stage201(stage201, accepted=True)
    _stage198(stage198)
    _stage193(stage193)

    result = run_stage202_reduced_scope_live_runner_preparation_review(
        stage201_results_path=stage201,
        stage198_results_path=stage198,
        stage193_results_path=stage193,
    )

    assert result["decision"] == "REDUCED_SCOPE_LIVE_RUNNER_PREPARATION_REVIEW_READY_TO_BUILD_PACKAGE_NOT_LIVE"
    assert result["exact_approval_ready"] is True
    assert result["reduced_scope_frozen"] is True
    assert result["read_only_backend_ready"] is True
    assert "reduced_scope_execution_package_required" in result["blockers"]
    assert "result_ingestion_contract_required" in result["blockers"]
    assert result["runnable_commands_recorded"] is False


def test_stage202_outputs_do_not_record_secrets_or_live_submit(tmp_path) -> None:
    stage201 = tmp_path / "stage201.json"
    stage198 = tmp_path / "stage198.json"
    stage193 = tmp_path / "stage193.json"
    _stage201(stage201, accepted=False)
    _stage198(stage198)
    _stage193(stage193)

    result = run_stage202_reduced_scope_live_runner_preparation_review(
        stage201_results_path=stage201,
        stage198_results_path=stage198,
        stage193_results_path=stage193,
    )
    paths = write_stage202_outputs(result, tmp_path / "out")
    written = (tmp_path / "out" / "results.json").read_text(encoding="utf-8")
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert "IBM_QUANTUM_TOKEN" not in written
    assert "QISKIT_IBM_TOKEN" not in written
    assert "crn:v1" not in written
    assert "--allow-live-submit" not in written
    assert "--allow-live-submit" not in summary
