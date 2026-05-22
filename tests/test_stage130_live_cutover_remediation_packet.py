from __future__ import annotations

import json

from qrope.stage130_live_cutover_remediation_packet import run_stage130_packet, write_stage130_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _fixture(tmp_path, *, authorized: bool = False):
    stage106_status = "ready" if authorized else "blocked"
    stage111_status = "ready" if authorized else "blocked"
    _write_json(
        tmp_path / "stage106.json",
        {
            "required_common_env": ["QROPE_HARDWARE_BUDGET_USD_CAP", "QROPE_HARDWARE_QUEUE_DEPTH_CAP"],
            "required_provider_env": {
                "ibm_runtime": [
                    "IBM_QUANTUM_TOKEN or QISKIT_IBM_TOKEN",
                    "QROPE_IBM_BACKEND or QROPE_HARDWARE_BACKEND",
                    "IBM_QUANTUM_INSTANCE_CRN",
                ]
            },
            "provider_records": [
                {"provider": "ibm_runtime", "status": stage106_status, "blockers": [] if authorized else ["ibm_instance_crn_missing"]}
            ],
        },
    )
    _write_json(
        tmp_path / "stage111.json",
        {
            "provider_records": [
                {
                    "provider": "ibm_runtime",
                    "status": stage111_status,
                    "blockers": [] if authorized else ["stage106_provider_preflight_not_ready"],
                    "sdk_modules": {"qiskit": True, "qiskit_ibm_runtime": True},
                }
            ]
        },
    )
    _write_json(
        tmp_path / "stage128.json",
        {
            "provider_records": [
                {
                    "provider": "ibm_runtime",
                    "ready": True,
                    "client_config": {
                        "client_factory_implemented": authorized,
                        "blockers": [] if authorized else ["sdk_client_factory_not_enabled"],
                    },
                }
            ]
        },
    )
    _write_json(
        tmp_path / "stage129.json",
        {
            "provider_records": [
                {
                    "provider": "ibm_runtime",
                    "cutover_authorized": authorized,
                    "blockers": [] if authorized else ["stage106:ibm_instance_crn_missing", "stage128:client_factory_not_implemented"],
                }
            ]
        },
    )
    return tmp_path / "stage106.json", tmp_path / "stage111.json", tmp_path / "stage128.json", tmp_path / "stage129.json"


def test_stage130_builds_blocked_remediation_packet(tmp_path) -> None:
    stage106, stage111, stage128, stage129 = _fixture(tmp_path, authorized=False)

    result = run_stage130_packet(
        stage106_results_path=stage106,
        stage111_results_path=stage111,
        stage128_results_path=stage128,
        stage129_results_path=stage129,
    )

    record = result["provider_records"][0]
    assert result["decision"] == "LIVE_CUTOVER_REMEDIATION_PACKET_READY_EXECUTION_BLOCKED"
    assert result["authorized_provider_count"] == 0
    assert "IBM_QUANTUM_INSTANCE_CRN" in record["required_provider_env"]
    assert any("guarded real factory" in action for action in record["remediation_actions"])
    assert result["secret_values_recorded"] is False
    assert result["no_hardware_submission"] is True


def test_stage130_tracks_authorized_provider_state(tmp_path) -> None:
    stage106, stage111, stage128, stage129 = _fixture(tmp_path, authorized=True)

    result = run_stage130_packet(
        stage106_results_path=stage106,
        stage111_results_path=stage111,
        stage128_results_path=stage128,
        stage129_results_path=stage129,
    )

    assert result["decision"] == "LIVE_CUTOVER_REMEDIATION_PACKET_READY"
    assert result["authorized_provider_count"] == 1
    assert result["provider_records"][0]["cutover_authorized"] is True


def test_stage130_writes_json_csv_and_markdown(tmp_path) -> None:
    stage106, stage111, stage128, stage129 = _fixture(tmp_path, authorized=False)
    result = run_stage130_packet(
        stage106_results_path=stage106,
        stage111_results_path=stage111,
        stage128_results_path=stage128,
        stage129_results_path=stage129,
    )

    paths = write_stage130_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    packet = (tmp_path / "out" / "remediation_packet.md").read_text(encoding="utf-8")
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv", "remediation_packet"}
    assert manifest["decision"] == "LIVE_CUTOVER_REMEDIATION_PACKET_READY_EXECUTION_BLOCKED"
    assert "QRoPE Stage 130" in packet
    assert "ibm_runtime" in summary
