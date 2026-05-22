from __future__ import annotations

import json

from qrope.stage135_post_collection_claim_gate_sequence import run_stage135_sequence_audit, write_stage135_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _paths(tmp_path):
    return {
        "stage115": tmp_path / "stage115.json",
        "stage134": tmp_path / "stage134.json",
        "stage113": tmp_path / "stage113.json",
        "stage101": tmp_path / "stage101.json",
        "stage103": tmp_path / "stage103.json",
        "stage109": tmp_path / "stage109.json",
        "stage110": tmp_path / "stage110.json",
        "stage136": tmp_path / "stage136.json",
        "stage137": tmp_path / "stage137.json",
        "stage148": tmp_path / "stage148.json",
        "stage138": tmp_path / "stage138.json",
    }


def _run(paths):
    return run_stage135_sequence_audit(
        stage115_results_path=paths["stage115"],
        stage134_results_path=paths["stage134"],
        stage113_results_path=paths["stage113"],
        stage101_results_path=paths["stage101"],
        stage103_results_path=paths["stage103"],
        stage109_results_path=paths["stage109"],
        stage110_results_path=paths["stage110"],
        stage136_results_path=paths["stage136"],
        stage137_results_path=paths["stage137"],
        stage148_results_path=paths["stage148"],
        stage138_results_path=paths["stage138"],
    )


def _write_blocked_fixture(paths) -> None:
    _write_json(paths["stage115"], {"decision": "PROVIDER_RESULTS_COLLECTION_BLOCKED_RESULTS_MISSING"})
    _write_json(paths["stage134"], {"decision": "RUNNER_RESULT_INTAKE_ALIGNED_EXECUTION_BLOCKED"})
    _write_json(paths["stage113"], {"decision": "JOB_RESULT_EVIDENCE_ASSEMBLY_BLOCKED_RESULTS_MISSING"})
    _write_json(paths["stage101"], {"decision": "KNOWN_STATE_CALIBRATION_COUNTS_REQUIRED_BEFORE_HARDWARE_INTERPRETATION"})
    _write_json(paths["stage103"], {"decision": "ROBUSTNESS_METRICS_PREREGISTERED_HARDWARE_COUNTS_REQUIRED"})
    _write_json(paths["stage109"], {"decision": "WINDOW_EVIDENCE_INTAKE_BLOCKED_EVIDENCE_MISSING"})
    _write_json(paths["stage110"], {"decision": "REPLICATED_ADVANTAGE_CLAIM_BLOCKED_EVIDENCE_INTAKE_INCOMPLETE"})
    _write_json(paths["stage136"], {"decision": "AUDITABILITY_METRIC_CONTRACT_INCOMPLETE"})
    _write_json(paths["stage137"], {"decision": "AUDITABILITY_METRICS_BLOCKED_HARDWARE_COUNTS_REQUIRED"})
    _write_json(paths["stage148"], {"decision": "FIRST_PROVIDER_STATISTICAL_INTERPRETATION_BLOCKED_EVIDENCE_REQUIRED"})
    _write_json(paths["stage138"], {"decision": "OBJECTIVE_CLAIM_GATE_BLOCKED_EVIDENCE_INCOMPLETE"})


def _write_ready_fixture(paths, *, replicated_advantage_count: int = 0) -> None:
    _write_json(paths["stage115"], {"decision": "PROVIDER_RESULTS_COLLECTED_FOR_STAGE113"})
    _write_json(paths["stage134"], {"decision": "RUNNER_RESULT_INTAKE_READY_FOR_STAGE113"})
    _write_json(paths["stage113"], {"decision": "JOB_RESULTS_ASSEMBLED_INTO_STAGE109_EVIDENCE"})
    _write_json(paths["stage101"], {"decision": "KNOWN_STATE_CALIBRATION_VERIFIED_READY_FOR_MATCHED_HARDWARE_EXECUTION"})
    _write_json(paths["stage103"], {"decision": "ROBUSTNESS_METRICS_READY_FOR_INTERPRETATION"})
    _write_json(paths["stage109"], {"decision": "WINDOW_EVIDENCE_INTAKE_READY_FOR_STAGE105_AGGREGATION"})
    _write_json(paths["stage136"], {"decision": "AUDITABILITY_METRIC_CONTRACT_READY_HARDWARE_COUNTS_REQUIRED"})
    _write_json(paths["stage137"], {"decision": "AUDITABILITY_METRICS_READY_FOR_CLAIM_GATE"})
    _write_json(paths["stage148"], {"decision": "FIRST_PROVIDER_STATISTICAL_INTERPRETATION_READY_FOR_CLAIM_GATES"})
    _write_json(paths["stage138"], {"decision": "PHASEWRAP_NOISY_HARDWARE_OBJECTIVE_NOT_SUPPORTED"})
    _write_json(
        paths["stage110"],
        {
            "decision": "PHASEWRAP_REPLICATED_ADVANTAGE_SUPPORTED_BY_STAGE105_RULE"
            if replicated_advantage_count
            else "PHASEWRAP_REPLICATED_ADVANTAGE_NOT_SUPPORTED_BY_STAGE105_RULE",
            "replicated_advantage_count": replicated_advantage_count,
        },
    )


def test_stage135_blocks_and_preserves_ordered_command_sequence(tmp_path) -> None:
    paths = _paths(tmp_path)
    _write_blocked_fixture(paths)

    result = _run(paths)

    assert result["decision"] == "POST_COLLECTION_CLAIM_GATE_SEQUENCE_PREPARED_EXECUTION_BLOCKED"
    assert result["ready_gate_count"] == 0
    assert result["blocked_gate_count"] == 11
    assert result["final_claim_gate_terminal"] is False
    assert result["ordered_command_sequence"][0] == "python scripts/run_stage115_provider_result_collector.py --write-stage113-input"
    assert "python scripts/run_stage110_replicated_advantage_claim_gate.py" in result["ordered_command_sequence"]
    assert "python scripts/run_stage136_auditability_metric_preregistration.py" in result["ordered_command_sequence"]
    assert "python scripts/run_stage137_auditability_metric_evaluator.py" in result["ordered_command_sequence"]
    assert "python scripts/run_stage148_first_provider_statistical_interpretation_gate.py" in result["ordered_command_sequence"]
    assert result["ordered_command_sequence"][-1] == "python scripts/run_stage138_objective_claim_gate.py"
    assert result["no_hardware_submission"] is True


def test_stage135_reports_complete_after_terminal_not_supported_claim_gate(tmp_path) -> None:
    paths = _paths(tmp_path)
    _write_ready_fixture(paths, replicated_advantage_count=0)

    result = _run(paths)

    assert result["decision"] == "POST_COLLECTION_CLAIM_GATE_SEQUENCE_COMPLETE_TERMINAL_CLAIM_REACHED"
    assert result["ready_gate_count"] == 11
    assert result["final_claim_gate_terminal"] is True
    assert result["replicated_advantage_count"] == 0


def test_stage135_reports_complete_after_terminal_supported_claim_gate(tmp_path) -> None:
    paths = _paths(tmp_path)
    _write_ready_fixture(paths, replicated_advantage_count=1)

    result = _run(paths)

    assert result["decision"] == "POST_COLLECTION_CLAIM_GATE_SEQUENCE_COMPLETE_TERMINAL_CLAIM_REACHED"
    assert result["ready_gate_count"] == 11
    assert result["final_claim_gate_terminal"] is True
    assert result["replicated_advantage_count"] == 1


def test_stage135_outputs_are_written(tmp_path) -> None:
    paths = _paths(tmp_path)
    _write_blocked_fixture(paths)
    result = _run(paths)

    written = write_stage135_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(written) == {"manifest", "result", "summary_csv"}
    assert manifest["gate_count"] == 11
    assert "stage110" in summary
