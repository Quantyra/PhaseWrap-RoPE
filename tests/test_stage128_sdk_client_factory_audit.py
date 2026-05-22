from __future__ import annotations

import json

import pytest

from qrope.provider_adapters.amazon_braket import build_client_config as braket_client_config
from qrope.provider_adapters.amazon_braket import create_live_client as create_braket_client
from qrope.provider_adapters.common import ProviderAdapterBlocked
from qrope.provider_adapters.ibm_runtime import build_client_config as ibm_client_config
from qrope.provider_adapters.ibm_runtime import create_live_client as create_ibm_client
from qrope.stage128_sdk_client_factory_audit import run_stage128_audit, write_stage128_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def test_client_configs_are_non_secret_and_blocked() -> None:
    ibm = ibm_client_config()
    braket = braket_client_config()

    assert ibm["provider"] == "ibm_runtime"
    assert braket["provider"] == "amazon_braket"
    assert ibm["secret_values_recorded"] is False
    assert braket["secret_values_recorded"] is False
    assert ibm["no_hardware_submission"] is True
    assert braket["no_hardware_submission"] is True
    assert "sdk_client_factory_not_enabled" in ibm["blockers"]
    assert "sdk_client_factory_not_enabled" in braket["blockers"]


def test_live_client_factories_fail_closed() -> None:
    with pytest.raises(ProviderAdapterBlocked):
        create_ibm_client()
    with pytest.raises(ProviderAdapterBlocked):
        create_ibm_client(allow_live_client=True)
    with pytest.raises(ProviderAdapterBlocked):
        create_braket_client()
    with pytest.raises(ProviderAdapterBlocked):
        create_braket_client(allow_live_client=True)


def _fixture(tmp_path):
    _write_json(
        tmp_path / "stage106.json",
        {
            "decision": "HARDWARE_EXECUTION_PREFLIGHT_BLOCKED_CONFIGURATION_REQUIRED",
            "provider_records": [
                {"provider": "amazon_braket", "status": "blocked"},
                {"provider": "ibm_runtime", "status": "blocked"},
            ],
        },
    )
    _write_json(
        tmp_path / "stage111.json",
        {
            "decision": "PROVIDER_SDK_BACKEND_DISCOVERY_BLOCKED",
            "provider_records": [
                {"provider": "amazon_braket", "status": "blocked"},
                {"provider": "ibm_runtime", "status": "blocked"},
            ],
        },
    )
    _write_json(tmp_path / "stage127.json", {"decision": "INJECTED_CLIENT_SUBMITTER_PATH_READY_EXECUTION_BLOCKED"})
    return tmp_path / "stage106.json", tmp_path / "stage111.json", tmp_path / "stage127.json"


def test_stage128_reports_client_factories_guarded(tmp_path) -> None:
    stage106, stage111, stage127 = _fixture(tmp_path)

    result = run_stage128_audit(stage106_results_path=stage106, stage111_results_path=stage111, stage127_results_path=stage127)

    assert result["decision"] == "SDK_CLIENT_FACTORIES_GUARDED_EXECUTION_BLOCKED"
    assert result["ready_provider_count"] == 2
    assert all(record["blocked_without_allow"] for record in result["provider_records"])
    assert all(record["blocked_with_allow"] for record in result["provider_records"])


def test_stage128_outputs_are_written(tmp_path) -> None:
    stage106, stage111, stage127 = _fixture(tmp_path)
    result = run_stage128_audit(stage106_results_path=stage106, stage111_results_path=stage111, stage127_results_path=stage127)

    paths = write_stage128_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert manifest["ready_provider_count"] == 2
    assert "ibm_runtime" in summary
