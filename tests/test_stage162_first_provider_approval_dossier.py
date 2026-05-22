from __future__ import annotations

import json

from qrope.stage162_first_provider_approval_dossier import run_stage162_approval_dossier, write_stage162_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _sources(tmp_path):
    stage154 = tmp_path / "stage154.json"
    stage157 = tmp_path / "stage157.json"
    stage159 = tmp_path / "stage159.json"
    stage160 = tmp_path / "stage160.json"
    stage161 = tmp_path / "stage161.json"
    stage165 = tmp_path / "stage165.json"
    stage166 = tmp_path / "stage166.json"
    stage167 = tmp_path / "stage167.json"
    stage168 = tmp_path / "stage168.json"
    stage169 = tmp_path / "stage169.json"
    _write_json(
        stage154,
        {
            "decision": "SIMULATED_NOISE_TARGETED_HARDWARE_FOLLOWUP_RECOMMENDED",
            "recommended_targets": [
                {"provider": "ibm_runtime", "source_lane_id": "ibm_product"},
                {"provider": "amazon_braket", "source_lane_id": "braket_product"},
            ],
        },
    )
    _write_json(
        stage157,
        {
            "decision": "FIRST_PROVIDER_LIVE_RUN_APPROVAL_PACKET_READY",
            "first_unlock_provider": "ibm_runtime",
            "approval_phrase_required": "APPROVE IBM RUNTIME STAGE133 LIVE RUN",
            "authorized_first_provider_runner_count": 2,
            "authorized_first_provider_job_count": 328,
            "runnable_commands_recorded": False,
        },
    )
    _write_json(
        stage159,
        {
            "decision": "FIRST_PROVIDER_BACKEND_PREFLIGHT_READY_AWAITING_APPROVAL",
            "backend_lookup_ready": True,
            "backend_metadata": {"pending_jobs": 3},
        },
    )
    _write_json(stage160, {"decision": "FIRST_PROVIDER_POST_RUN_ANALYSIS_PACKET_READY_AWAITING_PROVIDER_RESULTS"})
    _write_json(
        stage161,
        {
            "decision": "FIRST_PROVIDER_EXPOSURE_PACKET_READY_AWAITING_APPROVAL",
            "job_count": 328,
            "window_count": 2,
            "total_shots": 1318720,
            "missing_result_record_count": 328,
            "runnable_commands_recorded": False,
            "credit_balance_verified": False,
        },
    )
    _write_json(
        stage165,
        {
            "decision": "SIMULATED_NOISE_STABLE_TARGETED_HARDWARE_PROBE_RECOMMENDED",
            "recommended_hardware_probe_providers": ["ibm_runtime"],
            "target_records": [
                {"provider": "ibm_runtime", "stable_target": True, "source_lane_id": "ibm_product"},
                {"provider": "ibm_runtime", "stable_target": True, "source_lane_id": "ibm_cx"},
            ],
        },
    )
    _write_json(
        stage166,
        {
            "decision": "SIMULATED_EVIDENCE_TARGETED_PROBE_READY_BROAD_CLAIM_INSUFFICIENT",
            "targeted_probe_ready_providers": ["ibm_runtime"],
            "stable_provider_records": [
                {
                    "provider": "ibm_runtime",
                    "targeted_probe_ready": True,
                    "broad_simulated_claim_ready": False,
                    "broad_claim_blockers": ["stable_seed_count_below_broad_claim_threshold"],
                }
            ],
        },
    )
    _write_json(
        stage167,
        {
            "decision": "EXPANDED_SIMULATED_SEED_STRESS_DOES_NOT_SUPPORT_BROADENED_HARDWARE_PROBE",
            "stable_seed_count": 1,
            "stable_noise_model_count": 1,
            "stable_template_count": 2,
        },
    )
    _write_json(
        stage168,
        {
            "decision": "REAL_SOURCE_SEED_EXPANSION_REQUIRED_BEFORE_BROADENED_SCOPE",
            "current_real_ibm_seed_pair_count": 1,
            "missing_real_ibm_seed_pair_count": 1,
            "blockers": ["real_ibm_seed_pair_count_below_broadened_scope_threshold"],
        },
    )
    _write_json(
        stage169,
        {
            "decision": "TARGETED_IBM_PROBE_SCOPE_LOCKED_TO_STABLE_LANES",
            "stable_target_lanes": ["ibm_cx", "ibm_product"],
            "excluded_recommended_lanes": ["ibm_product_seed577_rows16_shots4096"],
            "locked_lane_count": 2,
        },
    )
    return stage154, stage157, stage159, stage160, stage161, stage165, stage166, stage167, stage168, stage169


def test_stage162_dossier_ready_for_human_go_no_go(tmp_path) -> None:
    stage154, stage157, stage159, stage160, stage161, stage165, stage166, stage167, stage168, stage169 = _sources(tmp_path)

    result = run_stage162_approval_dossier(
        stage154_results_path=stage154,
        stage157_results_path=stage157,
        stage159_results_path=stage159,
        stage160_results_path=stage160,
        stage161_results_path=stage161,
        stage165_results_path=stage165,
        stage166_results_path=stage166,
        stage167_results_path=stage167,
        stage168_results_path=stage168,
        stage169_results_path=stage169,
    )

    assert result["decision"] == "FIRST_PROVIDER_APPROVAL_DOSSIER_READY_FOR_HUMAN_GO_NO_GO"
    assert result["approval_state"] == "awaiting_exact_phrase"
    assert result["strict_simulated_target_count_for_provider"] == 1
    assert result["stable_simulated_target_count_for_provider"] == 2
    assert result["stage166_targeted_probe_ready_for_provider"] is True
    assert result["stage166_broad_simulated_claim_ready_for_provider"] is False
    assert result["stage167_stable_seed_count"] == 1
    assert result["stage168_missing_real_ibm_seed_pair_count"] == 1
    assert result["stage169_locked_lane_count"] == 2
    assert result["stage169_stable_target_lanes"] == ["ibm_cx", "ibm_product"]
    assert result["exposure_total_shots"] == 1318720
    assert result["runnable_commands_recorded"] is False
    assert result["credit_balance_verified"] is False


def test_stage162_go_consideration_updates_when_real_seed_pair_count_is_cleared(tmp_path) -> None:
    stage154, stage157, stage159, stage160, stage161, stage165, stage166, stage167, stage168, stage169 = _sources(tmp_path)
    _write_json(
        stage168,
        {
            "decision": "REAL_SOURCE_SEED_EXPANSION_REQUIRED_BEFORE_BROADENED_SCOPE",
            "current_real_ibm_seed_pair_count": 2,
            "missing_real_ibm_seed_pair_count": 0,
            "blockers": ["stage167_synthetic_stress_did_not_support_broadened_scope"],
        },
    )

    result = run_stage162_approval_dossier(
        stage154_results_path=stage154,
        stage157_results_path=stage157,
        stage159_results_path=stage159,
        stage160_results_path=stage160,
        stage161_results_path=stage161,
        stage165_results_path=stage165,
        stage166_results_path=stage166,
        stage167_results_path=stage167,
        stage168_results_path=stage168,
        stage169_results_path=stage169,
    )

    assert result["stage168_missing_real_ibm_seed_pair_count"] == 0
    assert any("clears the real IBM seed-pair count" in item for item in result["go_considerations"])
    assert all("requires another real IBM product/CX source seed pair" not in item for item in result["go_considerations"])


def test_stage162_blocks_on_exposure_mismatch(tmp_path) -> None:
    stage154, stage157, stage159, stage160, stage161, stage165, stage166, stage167, stage168, stage169 = _sources(tmp_path)
    _write_json(
        stage161,
        {
            "decision": "FIRST_PROVIDER_EXPOSURE_PACKET_READY_AWAITING_APPROVAL",
            "job_count": 327,
            "missing_result_record_count": 327,
            "runnable_commands_recorded": False,
            "credit_balance_verified": False,
        },
    )

    result = run_stage162_approval_dossier(
        stage154_results_path=stage154,
        stage157_results_path=stage157,
        stage159_results_path=stage159,
        stage160_results_path=stage160,
        stage161_results_path=stage161,
        stage165_results_path=stage165,
        stage166_results_path=stage166,
        stage167_results_path=stage167,
        stage168_results_path=stage168,
        stage169_results_path=stage169,
    )

    assert result["decision"] == "FIRST_PROVIDER_APPROVAL_DOSSIER_BLOCKED"
    assert "approved_job_count_exposure_mismatch" in result["blockers"]


def test_stage162_outputs_do_not_record_secrets_or_live_commands(tmp_path) -> None:
    stage154, stage157, stage159, stage160, stage161, stage165, stage166, stage167, stage168, stage169 = _sources(tmp_path)
    result = run_stage162_approval_dossier(
        stage154_results_path=stage154,
        stage157_results_path=stage157,
        stage159_results_path=stage159,
        stage160_results_path=stage160,
        stage161_results_path=stage161,
        stage165_results_path=stage165,
        stage166_results_path=stage166,
        stage167_results_path=stage167,
        stage168_results_path=stage168,
        stage169_results_path=stage169,
    )

    paths = write_stage162_outputs(result, tmp_path / "out")
    written = (tmp_path / "out" / "results.json").read_text(encoding="utf-8")
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert "--allow-live-submit" not in written
    assert "--allow-live-submit" not in summary
    assert "IBM_QUANTUM_TOKEN" not in written
    assert "crn:v1" not in written
