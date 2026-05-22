from __future__ import annotations

import json

from qrope.stage149_first_provider_guarded_runner_contract_audit import run_stage149_audit, write_stage149_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _paths(tmp_path) -> dict[str, object]:
    return {
        "stage111_results_path": tmp_path / "stage111.json",
        "stage118_results_path": tmp_path / "stage118.json",
        "stage129_results_path": tmp_path / "stage129.json",
        "stage133_results_path": tmp_path / "stage133.json",
        "stage145_results_path": tmp_path / "stage145.json",
    }


def _fixture(paths, *, provider="ibm_runtime") -> None:
    _write_json(paths["stage145_results_path"], {"first_unlock_provider": provider})
    _write_json(paths["stage111_results_path"], {"provider_records": [{"provider": provider, "status": "blocked"}]})
    _write_json(paths["stage118_results_path"], {"payload_records": []})
    _write_json(paths["stage129_results_path"], {"provider_records": [{"provider": provider, "cutover_authorized": False}]})
    _write_json(
        paths["stage133_results_path"],
        {"command_records": [{"provider": provider, "command_authorized": False}]},
    )


def test_stage149_validates_synthetic_runner_contract_and_current_cutover_block(tmp_path) -> None:
    paths = _paths(tmp_path)
    _fixture(paths)

    result = run_stage149_audit(**paths)

    assert result["decision"] == "FIRST_PROVIDER_GUARDED_RUNNER_CONTRACT_READY_CUTOVER_BLOCKED"
    assert result["first_unlock_provider"] == "ibm_runtime"
    assert result["current_stage129_cutover_authorized"] is False
    assert result["synthetic_contract_ready_count"] == 3
    assert result["no_hardware_submission"] is True


def test_stage149_validates_synthetic_runner_contract_for_actual_first_provider(tmp_path) -> None:
    paths = _paths(tmp_path)
    _fixture(paths, provider="amazon_braket")

    result = run_stage149_audit(**paths)

    assert result["decision"] == "FIRST_PROVIDER_GUARDED_RUNNER_CONTRACT_READY_CUTOVER_BLOCKED"
    assert result["first_unlock_provider"] == "amazon_braket"
    assert result["synthetic_contract_ready_count"] == 3


def test_stage149_blocks_without_first_provider_scope(tmp_path) -> None:
    paths = _paths(tmp_path)
    _fixture(paths)
    _write_json(paths["stage145_results_path"], {"first_unlock_provider": ""})

    result = run_stage149_audit(**paths)

    assert result["decision"] == "FIRST_PROVIDER_GUARDED_RUNNER_CONTRACT_INCOMPLETE"
    assert result["synthetic_contract_ready_count"] == 0
    assert result["synthetic_contract_records"][0]["check"] == "first_provider_scope_required"


def test_stage149_reports_missing_sources(tmp_path) -> None:
    paths = _paths(tmp_path)
    _fixture(paths)
    paths["stage129_results_path"].unlink()

    result = run_stage149_audit(**paths)

    assert result["decision"] == "FIRST_PROVIDER_GUARDED_RUNNER_CONTRACT_INCOMPLETE"
    assert result["missing_source_artifacts"]


def test_stage149_outputs_are_written(tmp_path) -> None:
    paths = _paths(tmp_path)
    _fixture(paths)
    result = run_stage149_audit(**paths)

    written = write_stage149_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(written) == {"manifest", "result", "summary_csv"}
    assert manifest["decision"] == "FIRST_PROVIDER_GUARDED_RUNNER_CONTRACT_READY_CUTOVER_BLOCKED"
    assert "valid_injected_submitter_writes_stage114_result" in summary
