from __future__ import annotations

import json

from qrope.stage176_ibm_credit_provider_resolution_handoff import run_stage176_resolution_handoff, write_stage176_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _sources(tmp_path, *, credit_verified=False):
    stage159 = tmp_path / "stage159.json"
    stage170 = tmp_path / "stage170.json"
    stage175 = tmp_path / "stage175.json"
    _write_json(
        stage159,
        {
            "decision": "FIRST_PROVIDER_BACKEND_PREFLIGHT_READY_AWAITING_APPROVAL",
            "backend_lookup_ready": True,
            "ibm_token_present": True,
            "ibm_instance_crn_present": True,
            "ibm_backend_env_present": True,
            "backend_metadata": {"backend": "ibm_fez", "operational": True, "pending_jobs": 3},
        },
    )
    _write_json(
        stage170,
        {
            "decision": "IBM_HARDWARE_PAUSE_READY_FOR_CREDIT_PROVIDER_RESOLUTION",
            "approval_phrase_required": "APPROVE IBM RUNTIME STAGE133 LIVE RUN",
        },
    )
    _write_json(
        stage175,
        {
            "decision": (
                "FIRST_PROVIDER_PRERESULT_READY_FOR_FINAL_HUMAN_GO_NO_GO"
                if credit_verified
                else "FIRST_PROVIDER_PRERESULT_READY_FOR_CREDIT_PROVIDER_RESOLUTION"
            ),
            "first_unlock_provider": "ibm_runtime",
            "credit_balance_verified": credit_verified,
            "locked_job_count": 328,
            "locked_total_shots": 1318720,
            "stable_target_lanes": ["ibm_cx_seed314_rows16_shots4096", "ibm_product_seed314_rows16_shots4096"],
        },
    )
    return stage159, stage170, stage175


def test_stage176_prepares_human_credit_provider_handoff(tmp_path) -> None:
    stage159, stage170, stage175 = _sources(tmp_path)

    result = run_stage176_resolution_handoff(
        stage159_results_path=stage159,
        stage170_results_path=stage170,
        stage175_results_path=stage175,
    )

    assert result["decision"] == "IBM_CREDIT_PROVIDER_RESOLUTION_HANDOFF_READY_FOR_HUMAN_CHECK"
    assert result["credit_balance_verified"] is False
    assert result["locked_job_count"] == 328
    assert result["locked_total_shots"] == 1318720
    assert result["blockers"] == []
    assert any(item["item_id"] == "credit_billing_runtime_allowance" and item["status"] == "human_verification_required" for item in result["resolution_items"])


def test_stage176_reports_final_go_no_go_ready_when_credit_verified(tmp_path) -> None:
    stage159, stage170, stage175 = _sources(tmp_path, credit_verified=True)

    result = run_stage176_resolution_handoff(
        stage159_results_path=stage159,
        stage170_results_path=stage170,
        stage175_results_path=stage175,
    )

    assert result["decision"] == "IBM_CREDIT_PROVIDER_RESOLUTION_HANDOFF_READY_FOR_FINAL_GO_NO_GO"
    assert result["credit_balance_verified"] is True


def test_stage176_blocks_when_backend_preflight_not_ready(tmp_path) -> None:
    stage159, stage170, stage175 = _sources(tmp_path)
    _write_json(stage159, {"decision": "FIRST_PROVIDER_BACKEND_PREFLIGHT_BLOCKED", "backend_lookup_ready": False})

    result = run_stage176_resolution_handoff(
        stage159_results_path=stage159,
        stage170_results_path=stage170,
        stage175_results_path=stage175,
    )

    assert result["decision"] == "IBM_CREDIT_PROVIDER_RESOLUTION_HANDOFF_BLOCKED"
    assert "stage159_backend_preflight_not_ready" in result["blockers"]


def test_stage176_outputs_do_not_record_secrets_or_live_submit(tmp_path) -> None:
    stage159, stage170, stage175 = _sources(tmp_path)
    result = run_stage176_resolution_handoff(
        stage159_results_path=stage159,
        stage170_results_path=stage170,
        stage175_results_path=stage175,
    )

    paths = write_stage176_outputs(result, tmp_path / "out")
    written = (tmp_path / "out" / "results.json").read_text(encoding="utf-8")
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert "--allow-live-submit" not in written
    assert "--allow-live-submit" not in summary
    assert "IBM_QUANTUM_TOKEN" not in written
    assert "crn:v1" not in written
