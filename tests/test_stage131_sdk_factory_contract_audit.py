from __future__ import annotations

import json

from qrope.provider_adapters.amazon_braket import build_live_client_factory_contract as braket_contract
from qrope.provider_adapters.ibm_runtime import build_live_client_factory_contract as ibm_contract
from qrope.stage131_sdk_factory_contract_audit import run_stage131_audit, write_stage131_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def test_provider_contracts_are_non_secret_and_gated() -> None:
    for contract in (ibm_contract(), braket_contract()):
        assert contract["secret_values_recorded"] is False
        assert contract["no_hardware_submission"] is True
        assert "stage106_provider_status_ready" in contract["activation_gates"]
        assert "stage111_provider_status_ready" in contract["activation_gates"]
        assert "stage129_cutover_authorized_true" in contract["activation_gates"]
        assert contract["official_doc_url"].startswith("https://")
        assert contract["required_imports"]
        assert contract["result_contract"]


def test_stage131_reports_contracts_ready_while_execution_blocked(tmp_path) -> None:
    _write_json(
        tmp_path / "stage130.json",
        {
            "decision": "LIVE_CUTOVER_REMEDIATION_PACKET_READY_EXECUTION_BLOCKED",
            "provider_records": [
                {"provider": "amazon_braket", "cutover_authorized": False},
                {"provider": "ibm_runtime", "cutover_authorized": False},
            ],
        },
    )

    result = run_stage131_audit(stage130_results_path=tmp_path / "stage130.json")

    assert result["decision"] == "SDK_FACTORY_CONTRACTS_READY_EXECUTION_BLOCKED"
    assert result["ready_provider_count"] == 2
    assert result["no_hardware_submission"] is True
    assert result["secret_values_recorded"] is False
    assert all(record["stage130_cutover_authorized"] is False for record in result["provider_records"])


def test_stage131_outputs_are_written(tmp_path) -> None:
    _write_json(
        tmp_path / "stage130.json",
        {
            "decision": "LIVE_CUTOVER_REMEDIATION_PACKET_READY_EXECUTION_BLOCKED",
            "provider_records": [
                {"provider": "amazon_braket", "cutover_authorized": False},
                {"provider": "ibm_runtime", "cutover_authorized": False},
            ],
        },
    )
    result = run_stage131_audit(stage130_results_path=tmp_path / "stage130.json")

    paths = write_stage131_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert manifest["ready_provider_count"] == 2
    assert "ibm_runtime" in summary
    assert "amazon_braket" in summary
