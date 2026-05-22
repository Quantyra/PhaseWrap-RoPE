from __future__ import annotations

import json

from qrope.stage138_objective_claim_gate import run_stage138_claim_gate, write_stage138_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _stage110(decision: str, replicated: int = 0) -> dict:
    return {
        "decision": decision,
        "stage105_preregistered": decision in {
            "PHASEWRAP_REPLICATED_ADVANTAGE_SUPPORTED_BY_STAGE105_RULE",
            "PHASEWRAP_REPLICATED_ADVANTAGE_NOT_SUPPORTED_BY_STAGE105_RULE",
        },
        "stage109_ready_for_aggregation": decision in {
            "PHASEWRAP_REPLICATED_ADVANTAGE_SUPPORTED_BY_STAGE105_RULE",
            "PHASEWRAP_REPLICATED_ADVANTAGE_NOT_SUPPORTED_BY_STAGE105_RULE",
        },
        "ready_for_stage105_aggregation": decision in {
            "PHASEWRAP_REPLICATED_ADVANTAGE_SUPPORTED_BY_STAGE105_RULE",
            "PHASEWRAP_REPLICATED_ADVANTAGE_NOT_SUPPORTED_BY_STAGE105_RULE",
        },
        "replicated_advantage_count": replicated,
        "replication_records": [{"provider": "ibm_runtime", "replicated_phasewrap_advantage": bool(replicated)}] if replicated else [],
    }


def _stage137(*, ready: bool, passing_windows: tuple[str, ...] = ()) -> dict:
    return {
        "decision": "AUDITABILITY_METRICS_READY_FOR_CLAIM_GATE" if ready else "AUDITABILITY_METRICS_BLOCKED_HARDWARE_COUNTS_REQUIRED",
        "stage136_ready": ready,
        "window_count": 2,
        "ready_window_count": 2 if ready else 0,
        "window_records": [
            {"provider": "ibm_runtime", "window_id": "w0", "ready": ready},
            {"provider": "ibm_runtime", "window_id": "w1", "ready": ready},
        ],
        "comparison_summary": [
            {
                "window_id": window_id,
                "provider": "ibm_runtime",
                "source_lane_id": "lane_0",
                "circuit_template": "two_ry_product_state_z_readout_v1",
                "passes_auditability_advantage_rule": window_id in passing_windows,
            }
            for window_id in ("w0", "w1")
        ]
        if ready
        else [],
    }


def _stage148(*, ready: bool) -> dict:
    return {
        "decision": "FIRST_PROVIDER_STATISTICAL_INTERPRETATION_READY_FOR_CLAIM_GATES"
        if ready
        else "FIRST_PROVIDER_STATISTICAL_INTERPRETATION_BLOCKED_EVIDENCE_REQUIRED",
        "calibration_record_count": 2,
        "ready_calibration_record_count": 2 if ready else 0,
        "lane_record_count": 2,
        "stage103_lower_mae_lane_count": 2 if ready else 0,
        "shot_noise_separated_lane_count": 2 if ready else 0,
    }


def test_stage138_blocks_until_both_robustness_and_auditability_gates_are_terminal(tmp_path) -> None:
    stage110 = tmp_path / "stage110.json"
    stage137 = tmp_path / "stage137.json"
    stage148 = tmp_path / "stage148.json"
    _write_json(stage110, _stage110("REPLICATED_ADVANTAGE_CLAIM_BLOCKED_EVIDENCE_INTAKE_INCOMPLETE"))
    _write_json(stage137, _stage137(ready=False))
    _write_json(stage148, _stage148(ready=False))

    result = run_stage138_claim_gate(stage110_results_path=stage110, stage137_results_path=stage137, stage148_results_path=stage148)

    assert result["decision"] == "OBJECTIVE_CLAIM_GATE_BLOCKED_EVIDENCE_INCOMPLETE"
    assert result["objective_terminal"] is False
    assert result["objective_supported"] is False


def test_stage138_supports_objective_when_robustness_is_supported(tmp_path) -> None:
    stage110 = tmp_path / "stage110.json"
    stage137 = tmp_path / "stage137.json"
    stage148 = tmp_path / "stage148.json"
    _write_json(stage110, _stage110("PHASEWRAP_REPLICATED_ADVANTAGE_SUPPORTED_BY_STAGE105_RULE", replicated=1))
    _write_json(stage137, _stage137(ready=True))
    _write_json(stage148, _stage148(ready=True))

    result = run_stage138_claim_gate(stage110_results_path=stage110, stage137_results_path=stage137, stage148_results_path=stage148)

    assert result["decision"] == "PHASEWRAP_NOISY_HARDWARE_OBJECTIVE_SUPPORTED"
    assert result["objective_terminal"] is True
    assert result["objective_supported"] is True
    assert result["robustness_supported"] is True
    assert result["statistical_interpretation_required"] is True
    assert result["statistical_interpretation_ready"] is True


def test_stage138_blocks_supported_objective_when_stage148_is_not_ready(tmp_path) -> None:
    stage110 = tmp_path / "stage110.json"
    stage137 = tmp_path / "stage137.json"
    stage148 = tmp_path / "stage148.json"
    _write_json(stage110, _stage110("PHASEWRAP_REPLICATED_ADVANTAGE_SUPPORTED_BY_STAGE105_RULE", replicated=1))
    _write_json(stage137, _stage137(ready=True))
    _write_json(stage148, _stage148(ready=False))

    result = run_stage138_claim_gate(stage110_results_path=stage110, stage137_results_path=stage137, stage148_results_path=stage148)

    assert result["decision"] == "OBJECTIVE_CLAIM_GATE_BLOCKED_EVIDENCE_INCOMPLETE"
    assert result["objective_terminal"] is False
    assert result["statistical_interpretation_required"] is True
    assert result["statistical_interpretation_ready"] is False


def test_stage138_rejects_supported_stage110_decision_without_readiness_flags(tmp_path) -> None:
    stage110 = tmp_path / "stage110.json"
    stage137 = tmp_path / "stage137.json"
    stage148 = tmp_path / "stage148.json"
    payload = _stage110("PHASEWRAP_REPLICATED_ADVANTAGE_SUPPORTED_BY_STAGE105_RULE", replicated=1)
    payload.pop("ready_for_stage105_aggregation")
    _write_json(stage110, payload)
    _write_json(stage137, _stage137(ready=True))
    _write_json(stage148, _stage148(ready=True))

    result = run_stage138_claim_gate(stage110_results_path=stage110, stage137_results_path=stage137, stage148_results_path=stage148)

    assert result["decision"] == "OBJECTIVE_CLAIM_GATE_BLOCKED_EVIDENCE_INCOMPLETE"
    assert result["robustness_terminal"] is False
    assert result["objective_supported"] is False


def test_stage138_rejects_stage137_ready_decision_without_ready_windows(tmp_path) -> None:
    stage110 = tmp_path / "stage110.json"
    stage137 = tmp_path / "stage137.json"
    stage148 = tmp_path / "stage148.json"
    payload = _stage137(ready=True, passing_windows=("w0", "w1"))
    payload["ready_window_count"] = 1
    _write_json(stage110, _stage110("PHASEWRAP_REPLICATED_ADVANTAGE_NOT_SUPPORTED_BY_STAGE105_RULE"))
    _write_json(stage137, payload)
    _write_json(stage148, _stage148(ready=True))

    result = run_stage138_claim_gate(stage110_results_path=stage110, stage137_results_path=stage137, stage148_results_path=stage148)

    assert result["decision"] == "OBJECTIVE_CLAIM_GATE_BLOCKED_EVIDENCE_INCOMPLETE"
    assert result["auditability_ready"] is False
    assert result["replicated_auditability_advantage_count"] == 0


def test_stage138_rejects_stage148_ready_decision_without_ready_counters(tmp_path) -> None:
    stage110 = tmp_path / "stage110.json"
    stage137 = tmp_path / "stage137.json"
    stage148 = tmp_path / "stage148.json"
    payload = _stage148(ready=True)
    payload["shot_noise_separated_lane_count"] = 1
    _write_json(stage110, _stage110("PHASEWRAP_REPLICATED_ADVANTAGE_SUPPORTED_BY_STAGE105_RULE", replicated=1))
    _write_json(stage137, _stage137(ready=True))
    _write_json(stage148, payload)

    result = run_stage138_claim_gate(stage110_results_path=stage110, stage137_results_path=stage137, stage148_results_path=stage148)

    assert result["decision"] == "OBJECTIVE_CLAIM_GATE_BLOCKED_EVIDENCE_INCOMPLETE"
    assert result["statistical_interpretation_ready"] is False
    assert result["objective_supported"] is False


def test_stage138_supports_objective_when_auditability_replicates(tmp_path) -> None:
    stage110 = tmp_path / "stage110.json"
    stage137 = tmp_path / "stage137.json"
    stage148 = tmp_path / "stage148.json"
    _write_json(stage110, _stage110("PHASEWRAP_REPLICATED_ADVANTAGE_NOT_SUPPORTED_BY_STAGE105_RULE"))
    _write_json(stage137, _stage137(ready=True, passing_windows=("w0", "w1")))
    _write_json(stage148, _stage148(ready=True))

    result = run_stage138_claim_gate(stage110_results_path=stage110, stage137_results_path=stage137, stage148_results_path=stage148)

    assert result["decision"] == "PHASEWRAP_NOISY_HARDWARE_OBJECTIVE_SUPPORTED"
    assert result["objective_supported"] is True
    assert result["replicated_auditability_advantage_count"] == 1


def test_stage138_reports_not_supported_when_terminal_without_either_advantage(tmp_path) -> None:
    stage110 = tmp_path / "stage110.json"
    stage137 = tmp_path / "stage137.json"
    stage148 = tmp_path / "stage148.json"
    _write_json(stage110, _stage110("PHASEWRAP_REPLICATED_ADVANTAGE_NOT_SUPPORTED_BY_STAGE105_RULE"))
    _write_json(stage137, _stage137(ready=True, passing_windows=("w0",)))
    _write_json(stage148, _stage148(ready=False))

    result = run_stage138_claim_gate(stage110_results_path=stage110, stage137_results_path=stage137, stage148_results_path=stage148)

    assert result["decision"] == "PHASEWRAP_NOISY_HARDWARE_OBJECTIVE_NOT_SUPPORTED"
    assert result["objective_terminal"] is True
    assert result["objective_supported"] is False
    assert result["replicated_auditability_advantage_count"] == 0
    assert result["statistical_interpretation_required"] is False


def test_stage138_outputs_are_written(tmp_path) -> None:
    stage110 = tmp_path / "stage110.json"
    stage137 = tmp_path / "stage137.json"
    stage148 = tmp_path / "stage148.json"
    _write_json(stage110, _stage110("PHASEWRAP_REPLICATED_ADVANTAGE_NOT_SUPPORTED_BY_STAGE105_RULE"))
    _write_json(stage137, _stage137(ready=True, passing_windows=("w0", "w1")))
    _write_json(stage148, _stage148(ready=True))
    result = run_stage138_claim_gate(stage110_results_path=stage110, stage137_results_path=stage137, stage148_results_path=stage148)

    paths = write_stage138_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert manifest["objective_supported"] is True
    assert "ibm_runtime" in summary
