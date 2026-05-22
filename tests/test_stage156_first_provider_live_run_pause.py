from __future__ import annotations

import json

from qrope.stage156_first_provider_live_run_pause import run_stage156_live_run_pause, write_stage156_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def test_stage156_pauses_when_stage152_ready_and_commands_authorized(tmp_path) -> None:
    stage133 = tmp_path / "stage133.json"
    stage152 = tmp_path / "stage152.json"
    _write_json(
        stage133,
        {
            "decision": "AUTHORIZED_RUNNER_COMMANDS_PREPARED_EXECUTION_BLOCKED",
            "command_records": [
                {
                    "provider": "ibm_runtime",
                    "window_id": "window_0",
                    "job_count": 2,
                    "command_authorized": True,
                    "live_submit_command_available": True,
                    "live_submit_command": "python runner.py --allow-live-submit",
                }
            ],
        },
    )
    _write_json(
        stage152,
        {
            "decision": "FIRST_PROVIDER_LIVE_EXECUTION_GUARD_READY_FOR_GUARDED_RUNNER",
            "first_unlock_provider": "ibm_runtime",
        },
    )

    result = run_stage156_live_run_pause(stage133_results_path=stage133, stage152_results_path=stage152)

    assert result["decision"] == "FIRST_PROVIDER_LIVE_RUN_READY_AWAITING_EXPLICIT_APPROVAL"
    assert result["authorized_first_provider_runner_count"] == 1
    assert result["authorized_first_provider_job_count"] == 2
    assert result["explicit_user_approval_required"] is True
    assert result["no_hardware_submission"] is True
    assert "live_submit_command" not in result["authorized_command_records"][0]


def test_stage156_blocks_without_stage152_ready(tmp_path) -> None:
    stage133 = tmp_path / "stage133.json"
    stage152 = tmp_path / "stage152.json"
    _write_json(stage133, {"command_records": []})
    _write_json(stage152, {"decision": "FIRST_PROVIDER_LIVE_EXECUTION_GUARD_PREPARED_EXECUTION_BLOCKED"})

    result = run_stage156_live_run_pause(stage133_results_path=stage133, stage152_results_path=stage152)

    assert result["decision"] == "FIRST_PROVIDER_LIVE_RUN_PAUSE_BLOCKED_GUARD_NOT_READY"


def test_stage156_outputs_are_written_without_live_submit_command(tmp_path) -> None:
    stage133 = tmp_path / "stage133.json"
    stage152 = tmp_path / "stage152.json"
    _write_json(
        stage133,
        {
            "command_records": [
                {
                    "provider": "ibm_runtime",
                    "window_id": "window_0",
                    "job_count": 2,
                    "command_authorized": True,
                    "live_submit_command_available": True,
                    "live_submit_command": "python runner.py --allow-live-submit",
                }
            ]
        },
    )
    _write_json(
        stage152,
        {
            "decision": "FIRST_PROVIDER_LIVE_EXECUTION_GUARD_READY_FOR_GUARDED_RUNNER",
            "first_unlock_provider": "ibm_runtime",
        },
    )
    result = run_stage156_live_run_pause(stage133_results_path=stage133, stage152_results_path=stage152)

    paths = write_stage156_outputs(result, tmp_path / "out")
    written = (tmp_path / "out" / "results.json").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert "--allow-live-submit" not in written
