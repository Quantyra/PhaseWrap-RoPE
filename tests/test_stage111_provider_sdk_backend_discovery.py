from __future__ import annotations

import json

from qrope.stage111_provider_sdk_backend_discovery import run_stage111_discovery, write_stage111_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _stage106(*, ready: bool = False) -> dict[str, object]:
    return {
        "decision": "HARDWARE_EXECUTION_PREFLIGHT_READY_NO_SUBMISSION" if ready else "HARDWARE_EXECUTION_PREFLIGHT_BLOCKED_CONFIGURATION_REQUIRED",
        "ready_for_hardware_submission": ready,
        "provider_records": [
            {"provider": "ibm_runtime", "status": "ready" if ready else "blocked", "blockers": [] if ready else ["ibm_instance_crn_missing"]},
            {"provider": "amazon_braket", "status": "blocked", "blockers": ["provider_credentials_missing"]},
        ],
    }


def test_stage111_reports_missing_stage106_source(tmp_path) -> None:
    result = run_stage111_discovery(stage106_results_path=tmp_path / "missing.json")

    assert result["status"] == "incomplete"
    assert result["decision"] == "PROVIDER_SDK_BACKEND_DISCOVERY_BLOCKED"
    assert result["missing_source_artifacts"]


def test_stage111_separates_sdk_status_from_stage106_readiness(tmp_path) -> None:
    _write_json(tmp_path / "stage106.json", _stage106())

    result = run_stage111_discovery(stage106_results_path=tmp_path / "stage106.json")

    assert result["status"] == "completed"
    assert result["stage106_ready_for_hardware_submission"] is False
    assert result["provider_records"][0]["provider"] == "ibm_runtime"
    assert "stage106_provider_preflight_not_ready" in result["provider_records"][0]["blockers"]


def test_stage111_ready_when_all_providers_are_ready_and_sdks_are_present(monkeypatch, tmp_path) -> None:
    _write_json(
        tmp_path / "stage106.json",
        {
            "decision": "HARDWARE_EXECUTION_PREFLIGHT_READY_NO_SUBMISSION",
            "ready_for_hardware_submission": True,
            "provider_records": [
                {"provider": "ibm_runtime", "status": "ready", "blockers": []},
            ],
        },
    )
    monkeypatch.setattr("qrope.stage111_provider_sdk_backend_discovery._module_present", lambda name: True)

    result = run_stage111_discovery(stage106_results_path=tmp_path / "stage106.json")

    assert result["decision"] == "PROVIDER_SDK_BACKEND_DISCOVERY_READY_NO_SUBMISSION"
    assert result["ready_provider_count"] == 1


def test_stage111_live_discovery_blocks_without_token_or_backend(monkeypatch, tmp_path) -> None:
    _write_json(
        tmp_path / "stage106.json",
        {
            "decision": "HARDWARE_EXECUTION_PREFLIGHT_READY_NO_SUBMISSION",
            "ready_for_hardware_submission": True,
            "provider_records": [
                {"provider": "ibm_runtime", "status": "ready", "blockers": []},
            ],
        },
    )
    monkeypatch.setattr("qrope.stage111_provider_sdk_backend_discovery._module_present", lambda name: True)

    result = run_stage111_discovery(stage106_results_path=tmp_path / "stage106.json", env={}, allow_live_discovery=True)

    assert result["decision"] == "PROVIDER_SDK_BACKEND_DISCOVERY_BLOCKED"
    assert result["provider_records"][0]["backend_discovery"]["status"] == "blocked"
    assert "backend_discovery_failed" in result["provider_records"][0]["blockers"]


def test_stage111_outputs_are_written(tmp_path) -> None:
    _write_json(tmp_path / "stage106.json", _stage106())
    result = run_stage111_discovery(stage106_results_path=tmp_path / "stage106.json")

    paths = write_stage111_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert manifest["provider_count"] == 2
    assert "ibm_runtime" in summary
