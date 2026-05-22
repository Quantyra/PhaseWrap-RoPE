from __future__ import annotations

import json

from qrope.stage187_replacement_semantics_preregistration import (
    run_stage187_replacement_semantics_preregistration,
    write_stage187_outputs,
)


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def test_stage187_preregisters_replacement_semantics_after_stage186(tmp_path) -> None:
    stage186 = tmp_path / "stage186.json"
    _write_json(stage186, {"decision": "TARGET_CONTROL_SEMANTICS_REVISION_REQUIRED_BEFORE_HARDWARE"})

    result = run_stage187_replacement_semantics_preregistration(stage186_results_path=stage186)

    assert result["decision"] == "REPLACEMENT_SEMANTICS_PREREGISTERED_READY_FOR_PACKET_SCREEN"
    assert result["semantics"]["control_definition"]["control_family"] == "matched_nonzero_null_control"
    assert "zero-zero component control" in result["semantics"]["control_definition"]["disallowed_forms"]
    assert result["semantics"]["fixed_width_constraints"]["measured_qubits"] == 2
    assert result["no_hardware_submission"] is True


def test_stage187_blocks_when_stage186_does_not_require_revision(tmp_path) -> None:
    stage186 = tmp_path / "stage186.json"
    _write_json(stage186, {"decision": "TARGET_CONTROL_SEMANTICS_AUDIT_DOES_NOT_REQUIRE_REVISION"})

    result = run_stage187_replacement_semantics_preregistration(stage186_results_path=stage186)

    assert result["decision"] == "REPLACEMENT_SEMANTICS_PREREGISTRATION_INCOMPLETE"
    assert "stage186_revision_not_required" in result["blockers"]


def test_stage187_outputs_do_not_record_secrets_or_live_submit(tmp_path) -> None:
    stage186 = tmp_path / "stage186.json"
    _write_json(stage186, {"decision": "TARGET_CONTROL_SEMANTICS_REVISION_REQUIRED_BEFORE_HARDWARE"})
    result = run_stage187_replacement_semantics_preregistration(stage186_results_path=stage186)

    paths = write_stage187_outputs(result, tmp_path / "out")
    written = (tmp_path / "out" / "results.json").read_text(encoding="utf-8")
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert "IBM_QUANTUM_TOKEN" not in written
    assert "crn:v1" not in written
    assert "--allow-live-submit" not in written
    assert "--allow-live-submit" not in summary
