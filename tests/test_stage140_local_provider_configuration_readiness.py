from __future__ import annotations

import json

from qrope.stage140_local_provider_configuration_readiness import run_stage140_readiness, write_stage140_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _stage139(path) -> None:
    _write_json(
        path,
        {
            "decision": "PROVIDER_ACTION_CHECKLIST_READY_EXECUTION_BLOCKED",
            "provider_records": [
                {
                    "provider": "ibm_runtime",
                    "first_blocker": "stage106:ibm_instance_crn_missing",
                    "cutover_authorized": False,
                    "required_provider_env": [
                        "IBM_QUANTUM_TOKEN or QISKIT_IBM_TOKEN",
                        "QROPE_IBM_BACKEND or QROPE_HARDWARE_BACKEND",
                        "IBM_QUANTUM_INSTANCE_CRN",
                    ],
                    "required_common_env": [
                        "QROPE_HARDWARE_BUDGET_USD_CAP",
                        "QROPE_HARDWARE_QUEUE_DEPTH_CAP",
                    ],
                    "sdk_modules": {"json": True},
                }
            ],
        },
    )


def test_stage140_blocks_without_required_local_env(tmp_path) -> None:
    stage139 = tmp_path / "stage139.json"
    _stage139(stage139)

    result = run_stage140_readiness(stage139_results_path=stage139, env={})

    record = result["provider_records"][0]
    assert result["decision"] == "LOCAL_PROVIDER_CONFIGURATION_BLOCKED_ENV_OR_SDK_REQUIRED"
    assert result["rerun_ready_provider_count"] == 0
    assert record["env_ready_for_stage106"] is False
    assert "IBM_QUANTUM_INSTANCE_CRN" in record["missing_env_groups"]
    assert result["secret_values_recorded"] is False


def test_stage140_reports_provider_ready_when_env_groups_and_sdk_are_present(tmp_path) -> None:
    stage139 = tmp_path / "stage139.json"
    _stage139(stage139)
    env = {
        "QISKIT_IBM_TOKEN": "redacted-by-design",
        "QROPE_IBM_BACKEND": "ibm_backend",
        "IBM_QUANTUM_INSTANCE_CRN": "crn",
        "QROPE_HARDWARE_BUDGET_USD_CAP": "50",
        "QROPE_HARDWARE_QUEUE_DEPTH_CAP": "1",
    }

    result = run_stage140_readiness(stage139_results_path=stage139, env=env)

    record = result["provider_records"][0]
    assert result["decision"] == "LOCAL_PROVIDER_CONFIGURATION_READY_FOR_PREFLIGHT_RERUN"
    assert result["rerun_ready_provider_count"] == 1
    assert record["ready_for_preflight_rerun"] is True
    assert "QISKIT_IBM_TOKEN" in record["present_env_keys"]
    assert "redacted-by-design" not in json.dumps(result)


def test_stage140_outputs_are_written(tmp_path) -> None:
    stage139 = tmp_path / "stage139.json"
    _stage139(stage139)
    result = run_stage140_readiness(stage139_results_path=stage139, env={})

    paths = write_stage140_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert manifest["provider_count"] == 1
    assert "ibm_runtime" in summary
