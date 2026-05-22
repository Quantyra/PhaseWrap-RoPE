from __future__ import annotations

import json

from qrope.stage171_post_result_analysis_dry_run_audit import EXPECTED_STAGE_SEQUENCE, run_stage171_dry_run_audit, write_stage171_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _sources(tmp_path, *, missing_job_count=328):
    script_root = tmp_path / "scripts"
    script_root.mkdir()
    command_records = []
    for order, stage_id in enumerate(EXPECTED_STAGE_SEQUENCE, start=1):
        script = script_root / f"run_{stage_id}_example.py"
        script.write_text("print('no submit')\n", encoding="utf-8")
        command_records.append(
            {
                "order": order,
                "stage_id": stage_id,
                "command": f"python scripts/{script.name}",
                "hardware_submission_command": False,
                "purpose": f"run {stage_id}",
            }
        )
    stage160 = tmp_path / "stage160.json"
    stage170 = tmp_path / "stage170.json"
    _write_json(
        stage160,
        {
            "decision": "FIRST_PROVIDER_POST_RUN_ANALYSIS_PACKET_READY_AWAITING_PROVIDER_RESULTS",
            "command_records": command_records,
            "missing_job_count": missing_job_count,
            "runnable_hardware_commands_recorded": False,
        },
    )
    _write_json(
        stage170,
        {
            "decision": "IBM_HARDWARE_PAUSE_READY_FOR_CREDIT_PROVIDER_RESOLUTION",
            "first_unlock_provider": "ibm_runtime",
            "runnable_commands_recorded": False,
        },
    )
    return stage160, stage170, script_root


def test_stage171_validates_post_result_scripts_without_submitting(tmp_path, monkeypatch) -> None:
    stage160, stage170, script_root = _sources(tmp_path)
    monkeypatch.chdir(tmp_path)

    result = run_stage171_dry_run_audit(stage160_results_path=stage160, stage170_results_path=stage170, script_root=script_root)

    assert result["decision"] == "POST_RESULT_ANALYSIS_DRY_RUN_READY_AWAITING_PROVIDER_RESULTS"
    assert result["no_hardware_submission"] is True
    assert result["command_count"] == 12
    assert result["script_ready_count"] == 12
    assert result["observed_stage_sequence"] == EXPECTED_STAGE_SEQUENCE
    assert result["provider_results_missing"] is True
    assert result["blockers"] == []


def test_stage171_blocks_missing_script_and_wrong_order(tmp_path, monkeypatch) -> None:
    stage160, stage170, script_root = _sources(tmp_path)
    payload = json.loads(stage160.read_text(encoding="utf-8"))
    payload["command_records"][0], payload["command_records"][1] = payload["command_records"][1], payload["command_records"][0]
    payload["command_records"][2]["command"] = "python scripts/missing.py"
    _write_json(stage160, payload)
    monkeypatch.chdir(tmp_path)

    result = run_stage171_dry_run_audit(stage160_results_path=stage160, stage170_results_path=stage170, script_root=script_root)

    assert result["decision"] == "POST_RESULT_ANALYSIS_DRY_RUN_AUDIT_BLOCKED"
    assert "post_result_stage_sequence_mismatch" in result["blockers"]
    assert "post_result_command_records_not_ready" in result["blockers"]


def test_stage171_outputs_do_not_record_secrets_or_live_submit(tmp_path, monkeypatch) -> None:
    stage160, stage170, script_root = _sources(tmp_path)
    monkeypatch.chdir(tmp_path)
    result = run_stage171_dry_run_audit(stage160_results_path=stage160, stage170_results_path=stage170, script_root=script_root)

    paths = write_stage171_outputs(result, tmp_path / "out")
    written = (tmp_path / "out" / "results.json").read_text(encoding="utf-8")
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert "--allow-live-submit" not in written
    assert "--allow-live-submit" not in summary
    assert "IBM_QUANTUM_TOKEN" not in written
    assert "crn:v1" not in written
