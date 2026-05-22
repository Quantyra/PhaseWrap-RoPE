from __future__ import annotations

import json

from qrope.stage151_first_provider_result_metadata_guard_audit import run_stage151_audit, write_stage151_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _stage150(path) -> None:
    _write_json(
        path,
        {
            "decision": "FIRST_PROVIDER_RESULT_LINEAGE_CONTRACT_READY_EXECUTION_BLOCKED",
            "first_unlock_provider": "ibm_runtime",
            "required_backend_metadata_fields": ["provider", "backend", "window_id", "job_kind"],
            "stage148_stage146_ready": True,
            "stage148_stage147_ready": True,
            "stage148_statistical_source_contract_ready": True,
        },
    )


def test_stage151_readies_metadata_guard_contract(tmp_path) -> None:
    stage150 = tmp_path / "stage150.json"
    _stage150(stage150)

    result = run_stage151_audit(stage150_results_path=stage150)

    assert result["decision"] == "FIRST_PROVIDER_RESULT_METADATA_GUARD_READY_EXECUTION_BLOCKED"
    assert result["stage150_lineage_contract_ready"] is True
    assert result["stage150_statistical_source_contract_ready"] is True
    assert result["stage150_stage146_ready"] is True
    assert result["stage150_stage147_ready"] is True
    assert result["synthetic_guard_ready_count"] == 4
    assert result["required_backend_metadata_fields"] == ["provider", "backend", "window_id", "job_kind"]
    assert result["no_hardware_submission"] is True


def test_stage151_reports_incomplete_when_stage150_metadata_contract_missing(tmp_path) -> None:
    stage150 = tmp_path / "stage150.json"
    _write_json(
        stage150,
        {
            "decision": "FIRST_PROVIDER_RESULT_LINEAGE_CONTRACT_READY_EXECUTION_BLOCKED",
            "first_unlock_provider": "ibm_runtime",
            "required_backend_metadata_fields": ["provider", "backend"],
            "stage148_statistical_source_contract_ready": True,
        },
    )

    result = run_stage151_audit(stage150_results_path=stage150)

    assert result["decision"] == "FIRST_PROVIDER_RESULT_METADATA_GUARD_INCOMPLETE"
    assert result["stage150_lineage_contract_ready"] is False
    assert result["synthetic_guard_ready_count"] == 4


def test_stage151_requires_stage150_statistical_source_contract_readiness(tmp_path) -> None:
    stage150 = tmp_path / "stage150.json"
    _write_json(
        stage150,
        {
            "decision": "FIRST_PROVIDER_RESULT_LINEAGE_CONTRACT_READY_EXECUTION_BLOCKED",
            "first_unlock_provider": "ibm_runtime",
            "required_backend_metadata_fields": ["provider", "backend", "window_id", "job_kind"],
            "stage148_stage146_ready": True,
            "stage148_stage147_ready": False,
            "stage148_statistical_source_contract_ready": False,
        },
    )

    result = run_stage151_audit(stage150_results_path=stage150)

    assert result["decision"] == "FIRST_PROVIDER_RESULT_METADATA_GUARD_INCOMPLETE"
    assert result["stage150_lineage_contract_ready"] is False
    assert result["stage150_statistical_source_contract_ready"] is False
    assert result["stage150_stage146_ready"] is True
    assert result["stage150_stage147_ready"] is False


def test_stage151_outputs_are_written(tmp_path) -> None:
    stage150 = tmp_path / "stage150.json"
    _stage150(stage150)
    result = run_stage151_audit(stage150_results_path=stage150)

    written = write_stage151_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(written) == {"manifest", "result", "summary_csv"}
    assert manifest["decision"] == "FIRST_PROVIDER_RESULT_METADATA_GUARD_READY_EXECUTION_BLOCKED"
    assert "missing_backend_field_rejected" in summary
