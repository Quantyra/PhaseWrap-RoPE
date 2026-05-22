from __future__ import annotations

import json

from qrope.provider_adapters.common import env_present
from qrope.stage124_adapter_readiness_alignment_audit import run_stage124_audit, write_stage124_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _write_jsonl(path, records) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(record, sort_keys=True) + "\n" for record in records), encoding="utf-8")


def test_env_present_accepts_alternative_variables(monkeypatch) -> None:
    monkeypatch.setenv("QROPE_HARDWARE_BACKEND", "backend")

    result = env_present(("QROPE_IBM_BACKEND or QROPE_HARDWARE_BACKEND",))

    assert result["QROPE_IBM_BACKEND or QROPE_HARDWARE_BACKEND"] is True


def _fixture(tmp_path):
    _write_json(
        tmp_path / "stage106.json",
        {
            "decision": "HARDWARE_EXECUTION_PREFLIGHT_BLOCKED_CONFIGURATION_REQUIRED",
            "required_provider_env": {
                "amazon_braket": [
                    "AWS_ACCESS_KEY_ID or AWS_PROFILE",
                    "QROPE_BRAKET_DEVICE_ARN or QROPE_BRAKET_DEVICE_ARNS",
                    "QROPE_BRAKET_OUTPUT_S3_BUCKET",
                    "QROPE_BRAKET_AWS_REGION or AWS_REGION",
                ],
                "ibm_runtime": [
                    "IBM_QUANTUM_TOKEN or QISKIT_IBM_TOKEN",
                    "QROPE_IBM_BACKEND or QROPE_HARDWARE_BACKEND",
                    "IBM_QUANTUM_INSTANCE_CRN",
                ],
            },
            "provider_records": [
                {"provider": "amazon_braket", "status": "blocked", "blockers": ["provider_credentials_missing"]},
                {"provider": "ibm_runtime", "status": "blocked", "blockers": ["ibm_instance_crn_missing"]},
            ],
        },
    )
    _write_json(
        tmp_path / "stage111.json",
        {
            "decision": "PROVIDER_SDK_BACKEND_DISCOVERY_BLOCKED",
            "provider_records": [
                {"provider": "amazon_braket", "status": "blocked", "blockers": ["provider_sdk_missing"]},
                {"provider": "ibm_runtime", "status": "blocked", "blockers": ["stage106_provider_preflight_not_ready"]},
            ],
        },
    )
    _write_json(tmp_path / "stage123" / "results.json", {"decision": "PROVIDER_SUBMISSION_PLANS_READY_EXECUTION_BLOCKED"})
    _write_jsonl(
        tmp_path / "stage123" / "submission_plans" / "ibm_runtime" / "window_0" / "submission_plans.jsonl",
        [
            {
                "credential_env": "IBM_QUANTUM_TOKEN or QISKIT_IBM_TOKEN",
                "backend_env": "QROPE_IBM_BACKEND or QROPE_HARDWARE_BACKEND",
                "instance_env": "IBM_QUANTUM_INSTANCE_CRN",
            }
        ],
    )
    _write_jsonl(
        tmp_path / "stage123" / "submission_plans" / "amazon_braket" / "window_0" / "submission_plans.jsonl",
        [
            {
                "credential_env": "AWS_ACCESS_KEY_ID or AWS_PROFILE",
                "device_arn_env": "QROPE_BRAKET_DEVICE_ARN or QROPE_BRAKET_DEVICE_ARNS",
                "output_s3_bucket_env": "QROPE_BRAKET_OUTPUT_S3_BUCKET",
                "region_env": "QROPE_BRAKET_AWS_REGION or AWS_REGION",
            }
        ],
    )
    return tmp_path / "stage106.json", tmp_path / "stage111.json", tmp_path / "stage123" / "results.json"


def test_stage124_reports_alignment_ready(tmp_path) -> None:
    stage106, stage111, stage123 = _fixture(tmp_path)

    result = run_stage124_audit(stage106_results_path=stage106, stage111_results_path=stage111, stage123_results_path=stage123)

    assert result["decision"] == "ADAPTER_READINESS_ALIGNED_EXECUTION_BLOCKED"
    assert result["aligned_provider_count"] == 2
    assert all(record["ready"] for record in result["provider_records"])


def test_stage124_outputs_are_written(tmp_path) -> None:
    stage106, stage111, stage123 = _fixture(tmp_path)
    result = run_stage124_audit(stage106_results_path=stage106, stage111_results_path=stage111, stage123_results_path=stage123)

    paths = write_stage124_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert manifest["aligned_provider_count"] == 2
    assert "ibm_runtime" in summary
