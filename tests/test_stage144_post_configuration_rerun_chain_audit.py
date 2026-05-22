from __future__ import annotations

import json

from qrope.stage144_post_configuration_rerun_chain_audit import run_stage144_audit, write_stage144_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _stage_paths(tmp_path) -> dict[str, object]:
    return {
        "stage106_results_path": tmp_path / "stage106.json",
        "stage111_results_path": tmp_path / "stage111.json",
        "stage128_results_path": tmp_path / "stage128.json",
        "stage129_results_path": tmp_path / "stage129.json",
        "stage130_results_path": tmp_path / "stage130.json",
        "stage133_results_path": tmp_path / "stage133.json",
        "stage138_results_path": tmp_path / "stage138.json",
        "stage139_results_path": tmp_path / "stage139.json",
        "stage140_results_path": tmp_path / "stage140.json",
        "stage141_results_path": tmp_path / "stage141.json",
        "stage142_results_path": tmp_path / "stage142.json",
        "stage143_results_path": tmp_path / "stage143.json",
    }


def _write_fixture(paths, *, ready: bool) -> None:
    provider = "ibm_runtime"
    _write_json(
        paths["stage143_results_path"],
        {
            "decision": "FIRST_PROVIDER_HANDOFF_SAFETY_VERIFIED_NO_SUBMISSION",
            "first_unlock_provider": provider,
            "template_assignment_count": 1,
            "template_placeholders_only": True,
            "template_key_scope_ready": True,
            "unexpected_template_keys": [],
            "missing_template_keys": [],
            "rerun_commands_non_live": True,
            "stage139_context_ready": True,
            "boundary_ready": True,
        },
    )
    _write_json(paths["stage142_results_path"], {"first_unlock_provider": provider})
    _write_json(paths["stage141_results_path"], {"first_unlock_provider": provider})
    _write_json(
        paths["stage140_results_path"],
        {
            "provider_records": [
                {
                    "provider": provider,
                    "ready_for_preflight_rerun": ready,
                    "missing_env_groups": [] if ready else ["IBM_QUANTUM_INSTANCE_CRN"],
                    "missing_sdk_modules": [],
                    "stage139_context_blockers": [],
                }
            ]
        },
    )
    _write_json(
        paths["stage106_results_path"],
        {"provider_records": [{"provider": provider, "status": "ready" if ready else "blocked", "blockers": [] if ready else ["ibm_instance_crn_missing"]}]},
    )
    _write_json(
        paths["stage111_results_path"],
        {"provider_records": [{"provider": provider, "status": "ready" if ready else "blocked", "blockers": [] if ready else ["stage106_provider_preflight_not_ready"]}]},
    )
    _write_json(paths["stage128_results_path"], {"provider_records": [{"provider": provider, "ready": True, "missing_evidence": []}]})
    _write_json(
        paths["stage129_results_path"],
        {"provider_records": [{"provider": provider, "cutover_authorized": ready, "blockers": [] if ready else ["cutover_not_authorized"]}]},
    )
    _write_json(
        paths["stage130_results_path"],
        {
            "provider_records": [
                {
                    "provider": provider,
                    "cutover_authorized": ready,
                    "stage129_blockers": [] if ready else ["stage106:ibm_instance_crn_missing"],
                }
            ]
        },
    )
    _write_json(
        paths["stage139_results_path"],
        {
            "provider_records": [
                {
                    "provider": provider,
                    "ready_for_live_runner_execution": ready,
                    "first_blocker": "" if ready else "stage106:ibm_instance_crn_missing",
                }
            ]
        },
    )
    _write_json(
        paths["stage133_results_path"],
        {
            "command_records": [
                {
                    "provider": provider,
                    "command_authorized": ready,
                    "job_count": 164,
                }
            ]
        },
    )
    _write_json(paths["stage138_results_path"], {"decision": "OBJECTIVE_CLAIM_GATE_BLOCKED_EVIDENCE_INCOMPLETE"})


def test_stage144_blocks_at_stage140_when_first_provider_local_config_not_ready(tmp_path) -> None:
    paths = _stage_paths(tmp_path)
    _write_fixture(paths, ready=False)

    result = run_stage144_audit(**paths)

    assert result["decision"] == "POST_CONFIGURATION_RERUN_CHAIN_PREPARED_EXECUTION_BLOCKED"
    assert result["first_unlock_provider"] == "ibm_runtime"
    assert result["first_blocked_transition"]["stage"] == "stage140_local_provider_configuration_readiness"
    assert result["next_command"] == "python scripts/run_stage140_local_provider_configuration_readiness.py --load-dotenv"
    assert result["no_hardware_submission"] is True
    assert result["secret_values_recorded"] is False


def test_stage144_blocks_when_stage143_did_not_verify_scoped_template(tmp_path) -> None:
    paths = _stage_paths(tmp_path)
    _write_fixture(paths, ready=True)
    stage143 = json.loads(paths["stage143_results_path"].read_text(encoding="utf-8"))
    stage143["template_key_scope_ready"] = False
    stage143["unexpected_template_keys"] = ["IBM_QUANTUM_TOKEN"]
    _write_json(paths["stage143_results_path"], stage143)

    result = run_stage144_audit(**paths)

    assert result["decision"] == "POST_CONFIGURATION_RERUN_CHAIN_PREPARED_EXECUTION_BLOCKED"
    assert result["first_blocked_transition"]["stage"] == "stage143_first_provider_handoff_safety_audit"
    assert "template_key_scope_not_ready" in result["first_blocked_transition"]["blockers"]
    assert result["next_command"] == "python scripts/run_stage143_first_provider_handoff_safety_audit.py"


def test_stage144_blocks_when_stage143_reports_stage139_context_not_ready(tmp_path) -> None:
    paths = _stage_paths(tmp_path)
    _write_fixture(paths, ready=True)
    stage143 = json.loads(paths["stage143_results_path"].read_text(encoding="utf-8"))
    stage143["stage139_context_ready"] = False
    stage143["stage139_context_blockers"] = ["stage139_action_checklist_not_ready"]
    _write_json(paths["stage143_results_path"], stage143)

    result = run_stage144_audit(**paths)

    assert result["decision"] == "POST_CONFIGURATION_RERUN_CHAIN_PREPARED_EXECUTION_BLOCKED"
    assert result["first_blocked_transition"]["stage"] == "stage143_first_provider_handoff_safety_audit"
    assert "stage139_context_not_ready" in result["first_blocked_transition"]["blockers"]


def test_stage144_preserves_stage140_context_blockers(tmp_path) -> None:
    paths = _stage_paths(tmp_path)
    _write_fixture(paths, ready=True)
    stage140 = json.loads(paths["stage140_results_path"].read_text(encoding="utf-8"))
    stage140["provider_records"][0]["ready_for_preflight_rerun"] = False
    stage140["provider_records"][0]["stage139_context_blockers"] = ["stage139_runner_commands_missing"]
    _write_json(paths["stage140_results_path"], stage140)

    result = run_stage144_audit(**paths)

    assert result["decision"] == "POST_CONFIGURATION_RERUN_CHAIN_PREPARED_EXECUTION_BLOCKED"
    assert result["first_blocked_transition"]["stage"] == "stage140_local_provider_configuration_readiness"
    assert "stage139_runner_commands_missing" in result["first_blocked_transition"]["blockers"]


def test_stage144_accepts_stage140_after_first_provider_cutover_authorized(tmp_path) -> None:
    paths = _stage_paths(tmp_path)
    _write_fixture(paths, ready=True)
    stage140 = json.loads(paths["stage140_results_path"].read_text(encoding="utf-8"))
    stage140["provider_records"][0]["ready_for_preflight_rerun"] = False
    stage140["provider_records"][0]["env_ready_for_stage106"] = True
    stage140["provider_records"][0]["sdk_ready_for_stage111"] = True
    stage140["provider_records"][0]["stage139_context_blockers"] = ["stage139_provider_already_cutover_authorized"]
    _write_json(paths["stage140_results_path"], stage140)

    result = run_stage144_audit(**paths)
    stage140_transition = next(
        record for record in result["transition_records"] if record["stage"] == "stage140_local_provider_configuration_readiness"
    )

    assert stage140_transition["ready"] is True
    assert stage140_transition["blockers"] == []
    assert result["decision"] == "POST_CONFIGURATION_RERUN_CHAIN_READY_FOR_AUTHORIZED_RUNNER"


def test_stage144_reports_ready_when_first_provider_chain_and_runner_commands_authorized(tmp_path) -> None:
    paths = _stage_paths(tmp_path)
    _write_fixture(paths, ready=True)

    result = run_stage144_audit(**paths)

    assert result["decision"] == "POST_CONFIGURATION_RERUN_CHAIN_READY_FOR_AUTHORIZED_RUNNER"
    assert result["first_blocked_transition"] is None
    assert result["first_provider_authorized_runner_count"] == 1
    assert result["first_provider_prepared_job_count"] == 164


def test_stage144_outputs_are_written(tmp_path) -> None:
    paths = _stage_paths(tmp_path)
    _write_fixture(paths, ready=False)
    result = run_stage144_audit(**paths)

    written = write_stage144_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(written) == {"manifest", "result", "summary_csv"}
    assert manifest["decision"] == "POST_CONFIGURATION_RERUN_CHAIN_PREPARED_EXECUTION_BLOCKED"
    assert "stage140_local_provider_configuration_readiness" in summary
