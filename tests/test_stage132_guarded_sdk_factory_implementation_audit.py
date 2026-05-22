from __future__ import annotations

import json

from qrope.stage132_guarded_sdk_factory_implementation_audit import run_stage132_audit, write_stage132_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _fixture(tmp_path):
    providers = ["amazon_braket", "ibm_runtime"]
    _write_json(
        tmp_path / "stage128.json",
        {
            "decision": "SDK_CLIENT_FACTORIES_IMPLEMENTED_EXECUTION_BLOCKED",
            "provider_records": [
                {
                    "provider": provider,
                    "blocked_without_allow": True,
                    "blocked_without_cutover": True,
                    "client_config": {
                        "client_factory_implemented": True,
                        "no_hardware_submission": False,
                        "secret_values_recorded": False,
                    },
                }
                for provider in providers
            ],
        },
    )
    _write_json(
        tmp_path / "stage129.json",
        {
            "decision": "LIVE_CUTOVER_BLOCKED_READINESS_REQUIRED",
            "provider_records": [
                {
                    "provider": provider,
                    "cutover_authorized": False,
                    "blockers": ["stage106:provider_not_ready"],
                }
                for provider in providers
            ],
        },
    )
    _write_json(
        tmp_path / "stage131.json",
        {
            "decision": "SDK_FACTORY_CONTRACTS_READY_EXECUTION_BLOCKED",
            "provider_records": [
                {"provider": provider, "ready": True, "contract": {"contract_version": f"{provider}_contract_v1"}}
                for provider in providers
            ],
        },
    )
    return tmp_path / "stage128.json", tmp_path / "stage129.json", tmp_path / "stage131.json"


def test_stage132_reports_factories_implemented_but_cutover_blocked(tmp_path) -> None:
    stage128, stage129, stage131 = _fixture(tmp_path)

    result = run_stage132_audit(
        stage128_results_path=stage128,
        stage129_results_path=stage129,
        stage131_results_path=stage131,
    )

    assert result["decision"] == "GUARDED_SDK_FACTORIES_IMPLEMENTED_CUTOVER_BLOCKED"
    assert result["ready_provider_count"] == 2
    assert all(record["client_factory_implemented"] is True for record in result["provider_records"])
    assert all(record["cutover_authorized"] is False for record in result["provider_records"])
    assert result["no_hardware_submission"] is True
    assert result["secret_values_recorded"] is False


def test_stage132_rejects_stale_stage129_factory_blockers(tmp_path) -> None:
    stage128, stage129, stage131 = _fixture(tmp_path)
    payload = json.loads(stage129.read_text(encoding="utf-8"))
    payload["provider_records"][0]["blockers"].append("stage128:client_factory_not_implemented")
    _write_json(stage129, payload)

    result = run_stage132_audit(
        stage128_results_path=stage128,
        stage129_results_path=stage129,
        stage131_results_path=stage131,
    )

    assert result["decision"] == "GUARDED_SDK_FACTORIES_INCOMPLETE"
    assert result["ready_provider_count"] == 1


def test_stage132_outputs_are_written(tmp_path) -> None:
    stage128, stage129, stage131 = _fixture(tmp_path)
    result = run_stage132_audit(
        stage128_results_path=stage128,
        stage129_results_path=stage129,
        stage131_results_path=stage131,
    )

    paths = write_stage132_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert manifest["ready_provider_count"] == 2
    assert "amazon_braket" in summary
    assert "ibm_runtime" in summary
