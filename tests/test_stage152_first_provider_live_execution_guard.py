from __future__ import annotations

import json

from qrope.stage152_first_provider_live_execution_guard import run_stage152_guard, write_stage152_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _fixture(tmp_path, *, authorized: bool = False, metadata_ready: bool = True):
    stage133 = tmp_path / "stage133.json"
    stage151 = tmp_path / "stage151.json"
    _write_json(
        stage133,
        {
            "command_records": [
                {
                    "provider": "ibm_runtime",
                    "window_id": "window_0",
                    "job_count": 164,
                    "command_authorized": authorized,
                    "blockers": [] if authorized else ["stage129:cutover_not_authorized"],
                }
            ]
        },
    )
    _write_json(
        stage151,
        {
            "decision": (
                "FIRST_PROVIDER_RESULT_METADATA_GUARD_READY_EXECUTION_BLOCKED"
                if metadata_ready
                else "FIRST_PROVIDER_RESULT_METADATA_GUARD_INCOMPLETE"
            ),
            "first_unlock_provider": "ibm_runtime",
        },
    )
    return stage133, stage151


def test_stage152_blocks_when_first_provider_command_is_not_authorized(tmp_path) -> None:
    stage133, stage151 = _fixture(tmp_path, authorized=False, metadata_ready=True)

    result = run_stage152_guard(stage133_results_path=stage133, stage151_results_path=stage151)

    assert result["decision"] == "FIRST_PROVIDER_LIVE_EXECUTION_GUARD_PREPARED_EXECUTION_BLOCKED"
    assert result["stage151_metadata_guard_ready"] is True
    assert result["first_provider_authorized_runner_count"] == 0
    assert "stage133_no_authorized_first_provider_commands" in result["blockers"]


def test_stage152_requires_metadata_guard_even_when_command_authorized(tmp_path) -> None:
    stage133, stage151 = _fixture(tmp_path, authorized=True, metadata_ready=False)

    result = run_stage152_guard(stage133_results_path=stage133, stage151_results_path=stage151)

    assert result["decision"] == "FIRST_PROVIDER_LIVE_EXECUTION_GUARD_PREPARED_EXECUTION_BLOCKED"
    assert "stage151_metadata_guard_not_ready" in result["blockers"]


def test_stage152_reports_ready_when_command_and_metadata_guard_are_ready(tmp_path) -> None:
    stage133, stage151 = _fixture(tmp_path, authorized=True, metadata_ready=True)

    result = run_stage152_guard(stage133_results_path=stage133, stage151_results_path=stage151)

    assert result["decision"] == "FIRST_PROVIDER_LIVE_EXECUTION_GUARD_READY_FOR_GUARDED_RUNNER"
    assert result["first_provider_authorized_runner_count"] == 1
    assert result["blockers"] == []


def test_stage152_outputs_are_written(tmp_path) -> None:
    stage133, stage151 = _fixture(tmp_path, authorized=False, metadata_ready=True)
    result = run_stage152_guard(stage133_results_path=stage133, stage151_results_path=stage151)

    written = write_stage152_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(written) == {"manifest", "result", "summary_csv"}
    assert manifest["decision"] == "FIRST_PROVIDER_LIVE_EXECUTION_GUARD_PREPARED_EXECUTION_BLOCKED"
    assert "stage129:cutover_not_authorized" in summary
