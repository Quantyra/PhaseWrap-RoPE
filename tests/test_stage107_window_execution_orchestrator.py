from __future__ import annotations

import json

from qrope.stage107_window_execution_orchestrator import run_stage107_orchestrator, write_stage107_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _stage102() -> dict[str, object]:
    return {
        "template_paths": [
            "logs/templates/ibm_runtime_known_state_execution.json",
            "logs/templates/amazon_braket_known_state_execution.json",
        ]
    }


def _windows() -> list[dict[str, object]]:
    return [
        {
            "window_id": "ibm_runtime__independent_window_00",
            "provider": "ibm_runtime",
            "window_index": 0,
            "minimum_separation_from_previous_window_hours": 0,
            "packet_template_count": 1,
            "packet_templates": [{"packet_id": "p0", "template_path": "p0.json"}],
        },
        {
            "window_id": "amazon_braket__independent_window_00",
            "provider": "amazon_braket",
            "window_index": 0,
            "minimum_separation_from_previous_window_hours": 0,
            "packet_template_count": 1,
            "packet_templates": [{"packet_id": "p1", "template_path": "p1.json"}],
        },
    ]


def test_stage107_blocks_when_stage106_is_not_ready(tmp_path) -> None:
    _write_json(tmp_path / "stage102.json", _stage102())
    _write_json(tmp_path / "windows.json", _windows())
    _write_json(tmp_path / "stage106.json", {"ready_for_hardware_submission": False})

    result = run_stage107_orchestrator(
        stage102_manifest_path=tmp_path / "stage102.json",
        stage105_windows_path=tmp_path / "windows.json",
        stage106_manifest_path=tmp_path / "stage106.json",
    )

    assert result["decision"] == "WINDOW_EXECUTION_PLAN_PREPARED_PREFLIGHT_BLOCKED"
    assert result["window_count"] == 2
    assert result["window_execution_plans"][0]["steps"][0]["status"] == "blocked"
    assert result["no_hardware_submission"] is True


def test_stage107_ready_when_stage106_is_ready(tmp_path) -> None:
    _write_json(tmp_path / "stage102.json", _stage102())
    _write_json(tmp_path / "windows.json", _windows())
    _write_json(tmp_path / "stage106.json", {"ready_for_hardware_submission": True})

    result = run_stage107_orchestrator(
        stage102_manifest_path=tmp_path / "stage102.json",
        stage105_windows_path=tmp_path / "windows.json",
        stage106_manifest_path=tmp_path / "stage106.json",
    )

    assert result["decision"] == "WINDOW_EXECUTION_PLAN_READY_FOR_MANUAL_HARDWARE_RUN"
    assert result["window_execution_plans"][0]["steps"][0]["status"] == "ready"
    assert result["secret_values_recorded"] is False


def test_stage107_reports_missing_sources(tmp_path) -> None:
    result = run_stage107_orchestrator(
        stage102_manifest_path=tmp_path / "missing102.json",
        stage105_windows_path=tmp_path / "missing_windows.json",
        stage106_manifest_path=tmp_path / "missing106.json",
    )

    assert result["status"] == "incomplete"
    assert len(result["missing_source_artifacts"]) == 3


def test_stage107_outputs_are_written(tmp_path) -> None:
    _write_json(tmp_path / "stage102.json", _stage102())
    _write_json(tmp_path / "windows.json", _windows())
    _write_json(tmp_path / "stage106.json", {"ready_for_hardware_submission": False})
    result = run_stage107_orchestrator(
        stage102_manifest_path=tmp_path / "stage102.json",
        stage105_windows_path=tmp_path / "windows.json",
        stage106_manifest_path=tmp_path / "stage106.json",
    )

    paths = write_stage107_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    plans = json.loads((tmp_path / "out" / "window_execution_plans.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv", "window_plans"}
    assert manifest["window_count"] == 2
    assert len(plans) == 2
    assert "ibm_runtime__independent_window_00" in summary
