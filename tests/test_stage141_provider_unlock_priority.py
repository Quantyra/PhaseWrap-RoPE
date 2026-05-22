from __future__ import annotations

import json

from qrope.stage141_provider_unlock_priority import run_stage141_priority, write_stage141_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _fixture(tmp_path, *, ibm_ready: bool = False):
    _write_json(
        tmp_path / "stage139.json",
        {
            "decision": "PROVIDER_ACTION_CHECKLIST_READY_EXECUTION_BLOCKED",
            "provider_records": [
                {"provider": "amazon_braket", "first_blocker": "stage106:backend_selection_missing", "prepared_job_count": 84, "runner_command_count": 1, "authorized_runner_command_count": 0},
                {"provider": "ibm_runtime", "first_blocker": "stage106:ibm_instance_crn_missing", "prepared_job_count": 164, "runner_command_count": 1, "authorized_runner_command_count": 0},
            ],
        },
    )
    _write_json(
        tmp_path / "stage140.json",
        {
            "decision": "LOCAL_PROVIDER_CONFIGURATION_READY_FOR_PREFLIGHT_RERUN" if ibm_ready else "LOCAL_PROVIDER_CONFIGURATION_BLOCKED_ENV_OR_SDK_REQUIRED",
            "provider_records": [
                {
                    "provider": "amazon_braket",
                    "ready_for_preflight_rerun": False,
                    "missing_env_groups": ["AWS_ACCESS_KEY_ID or AWS_PROFILE", "QROPE_BRAKET_DEVICE_ARN or QROPE_BRAKET_DEVICE_ARNS"],
                    "missing_sdk_modules": ["boto3", "braket"],
                },
                {
                    "provider": "ibm_runtime",
                    "ready_for_preflight_rerun": ibm_ready,
                    "missing_env_groups": [] if ibm_ready else ["IBM_QUANTUM_INSTANCE_CRN"],
                    "missing_sdk_modules": [],
                },
            ],
        },
    )
    return tmp_path / "stage139.json", tmp_path / "stage140.json"


def test_stage141_prioritizes_lowest_friction_provider(tmp_path) -> None:
    stage139, stage140 = _fixture(tmp_path, ibm_ready=False)

    result = run_stage141_priority(stage139_results_path=stage139, stage140_results_path=stage140)

    assert result["decision"] == "PROVIDER_UNLOCK_PRIORITY_PREPARED_EXECUTION_BLOCKED"
    assert result["first_unlock_provider"] == "ibm_runtime"
    assert result["priority_records"][0]["sdk_missing_count"] == 0
    assert result["priority_records"][0]["env_missing_count"] == 1
    assert result["first_unlock_missing_env_groups"] == ["IBM_QUANTUM_INSTANCE_CRN"]
    assert result["first_unlock_missing_sdk_modules"] == []
    assert result["first_unlock_minimal_actions"] == [
        "Set local env groups without committing values: IBM_QUANTUM_INSTANCE_CRN."
    ]
    assert result["secret_values_recorded"] is False


def test_stage141_reports_ready_when_first_provider_can_rerun_preflight(tmp_path) -> None:
    stage139, stage140 = _fixture(tmp_path, ibm_ready=True)

    result = run_stage141_priority(stage139_results_path=stage139, stage140_results_path=stage140)

    assert result["decision"] == "PROVIDER_UNLOCK_PRIORITY_READY_FOR_PREFLIGHT_RERUN"
    assert result["first_unlock_provider"] == "ibm_runtime"
    assert result["first_unlock_ready_for_preflight_rerun"] is True
    assert result["first_unlock_missing_env_groups"] == []
    assert result["first_unlock_minimal_actions"] == [
        "Rerun Stage 106/111/128/129/130/139; then execute only authorized Stage 133 commands."
    ]


def test_stage141_outputs_are_written(tmp_path) -> None:
    stage139, stage140 = _fixture(tmp_path)
    result = run_stage141_priority(stage139_results_path=stage139, stage140_results_path=stage140)

    paths = write_stage141_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert manifest["first_unlock_provider"] == "ibm_runtime"
    assert manifest["first_unlock_missing_env_groups"] == ["IBM_QUANTUM_INSTANCE_CRN"]
    assert "amazon_braket" in summary
