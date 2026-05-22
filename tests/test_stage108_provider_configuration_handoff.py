from __future__ import annotations

import json

from qrope.stage108_provider_configuration_handoff import run_stage108_handoff, write_stage108_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _stage106() -> dict[str, object]:
    return {
        "decision": "HARDWARE_EXECUTION_PREFLIGHT_BLOCKED_CONFIGURATION_REQUIRED",
        "ready_for_hardware_submission": False,
        "provider_records": [
            {
                "provider": "amazon_braket",
                "status": "blocked",
                "credential_env_present": [],
                "backend_env_present": [],
                "blockers": ["provider_credentials_missing", "backend_selection_missing"],
            },
            {
                "provider": "ibm_runtime",
                "status": "blocked",
                "credential_env_present": ["IBM_QUANTUM_TOKEN"],
                "backend_env_present": ["QROPE_HARDWARE_BACKEND"],
                "blockers": ["ibm_instance_crn_missing"],
            },
        ],
    }


def test_stage108_generates_non_secret_templates_for_stage106_blockers(tmp_path) -> None:
    _write_json(tmp_path / "stage106.json", _stage106())
    _write_json(tmp_path / "stage107.json", {"decision": "WINDOW_EXECUTION_PLAN_PREPARED_PREFLIGHT_BLOCKED"})

    result = run_stage108_handoff(stage106_results_path=tmp_path / "stage106.json", stage107_manifest_path=tmp_path / "stage107.json")

    assert result["decision"] == "PROVIDER_CONFIGURATION_HANDOFF_PREPARED_STAGE106_STILL_BLOCKED"
    assert result["provider_count"] == 2
    assert result["secret_values_recorded"] is False
    assert "amazon_braket_stage106_env.template" in result["templates"]
    assert "QROPE_BRAKET_OUTPUT_S3_BUCKET=" in result["templates"]["amazon_braket_stage106_env.template"]
    assert "IBM_QUANTUM_INSTANCE_CRN=" in result["templates"]["ibm_runtime_stage106_env.template"]


def test_stage108_reports_missing_sources(tmp_path) -> None:
    result = run_stage108_handoff(stage106_results_path=tmp_path / "missing106.json", stage107_manifest_path=tmp_path / "missing107.json")

    assert result["status"] == "incomplete"
    assert len(result["missing_source_artifacts"]) == 2


def test_stage108_outputs_are_written(tmp_path) -> None:
    _write_json(tmp_path / "stage106.json", _stage106())
    _write_json(tmp_path / "stage107.json", {"decision": "WINDOW_EXECUTION_PLAN_PREPARED_PREFLIGHT_BLOCKED"})
    result = run_stage108_handoff(stage106_results_path=tmp_path / "stage106.json", stage107_manifest_path=tmp_path / "stage107.json")

    paths = write_stage108_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    templates = sorted((tmp_path / "out" / "env_templates").glob("*.template"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv", "template_dir"}
    assert manifest["provider_count"] == 2
    assert len(templates) == 2
    assert "ibm_instance_crn_missing" in summary
