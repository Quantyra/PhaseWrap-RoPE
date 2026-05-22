from __future__ import annotations

import json

from qrope.stage129_live_cutover_authorization_audit import run_stage129_audit, write_stage129_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _fixture(tmp_path, *, authorized: bool = False):
    stage106_status = "ready" if authorized else "blocked"
    stage111_status = "ready" if authorized else "blocked"
    _write_json(
        tmp_path / "stage106.json",
        {
            "decision": "READY" if authorized else "HARDWARE_EXECUTION_PREFLIGHT_BLOCKED_CONFIGURATION_REQUIRED",
            "providers": ["ibm_runtime"],
            "provider_records": [
                {"provider": "ibm_runtime", "status": stage106_status, "blockers": [] if authorized else ["ibm_instance_crn_missing"]}
            ],
        },
    )
    _write_json(
        tmp_path / "stage111.json",
        {
            "decision": "READY" if authorized else "PROVIDER_SDK_BACKEND_DISCOVERY_BLOCKED",
            "provider_records": [
                {"provider": "ibm_runtime", "status": stage111_status, "blockers": [] if authorized else ["stage106_provider_preflight_not_ready"]}
            ],
        },
    )
    _write_json(
        tmp_path / "stage128.json",
        {
            "decision": "SDK_CLIENT_FACTORIES_GUARDED_EXECUTION_BLOCKED",
            "provider_records": [
                {
                    "provider": "ibm_runtime",
                    "ready": True,
                    "blocked_with_allow": not authorized,
                    "client_config": {
                        "client_factory_implemented": authorized,
                        "no_hardware_submission": not authorized,
                    },
                }
            ],
        },
    )
    return tmp_path / "stage106.json", tmp_path / "stage111.json", tmp_path / "stage128.json"


def test_stage129_blocks_current_unready_cutover(tmp_path) -> None:
    stage106, stage111, stage128 = _fixture(tmp_path, authorized=False)

    result = run_stage129_audit(stage106_results_path=stage106, stage111_results_path=stage111, stage128_results_path=stage128)

    assert result["decision"] == "LIVE_CUTOVER_BLOCKED_READINESS_REQUIRED"
    assert result["authorized_provider_count"] == 0
    assert result["provider_records"][0]["cutover_authorized"] is False
    assert any("stage106:" in blocker for blocker in result["provider_records"][0]["blockers"])


def test_stage129_authorizes_only_when_all_evidence_ready(tmp_path) -> None:
    stage106, stage111, stage128 = _fixture(tmp_path, authorized=True)

    result = run_stage129_audit(stage106_results_path=stage106, stage111_results_path=stage111, stage128_results_path=stage128)

    assert result["decision"] == "LIVE_CUTOVER_AUTHORIZED"
    assert result["authorized_provider_count"] == 1
    assert result["provider_records"][0]["cutover_authorized"] is True


def test_stage129_outputs_are_written(tmp_path) -> None:
    stage106, stage111, stage128 = _fixture(tmp_path, authorized=False)
    result = run_stage129_audit(stage106_results_path=stage106, stage111_results_path=stage111, stage128_results_path=stage128)

    paths = write_stage129_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert manifest["authorized_provider_count"] == 0
    assert "ibm_runtime" in summary
