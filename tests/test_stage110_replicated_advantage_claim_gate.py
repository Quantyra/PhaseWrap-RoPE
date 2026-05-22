from __future__ import annotations

import json

from qrope.stage110_replicated_advantage_claim_gate import run_stage110_claim_gate, write_stage110_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _summary(pass_rule: bool) -> dict[str, object]:
    return {
        "provider": "ibm_runtime",
        "source_lane_id": "lane_a",
        "circuit_template": "two_ry_product_state_z_readout_v1",
        "phasewrap_mean_absolute_score_error": 0.01 if pass_rule else 0.20,
        "best_comparator_mean_absolute_score_error": 0.05,
        "phasewrap_lower_error_than": ["rope_like", "sinusoidal_like", "alibi_like", "no_position_control"] if pass_rule else ["rope_like"],
        "all_families_present": True,
    }


def _ready_stage109(tmp_path, *, second_window_passes: bool = True) -> dict[str, object]:
    records = []
    for index, pass_rule in enumerate((True, second_window_passes)):
        window_id = f"ibm_runtime__independent_window_{index:02d}"
        stage103_path = tmp_path / "windows" / window_id / "stage103" / "results.json"
        _write_json(
            stage103_path,
            {
                "decision": "ROBUSTNESS_METRICS_READY_FOR_INTERPRETATION",
                "ready_to_interpret_hardware_metrics": True,
                "comparison_groups_complete": True,
                "stage104_matched_surface_ready": True,
                "stage104_complete_matched_group_count": 1,
                "stage113_live_submit_provenance_ready": True,
                "missing_execution_count": 0,
                "metric_record_count": 5,
                "comparison_summary": [_summary(pass_rule)],
            },
        )
        records.append(
            {
                "window_id": window_id,
                "provider": "ibm_runtime",
                "window_index": index,
                "ready": True,
                "stage103_results_path": str(stage103_path.as_posix()),
            }
        )
    return {
        "decision": "WINDOW_EVIDENCE_INTAKE_READY_FOR_STAGE105_AGGREGATION",
        "window_records": records,
    }


def test_stage110_reports_missing_sources(tmp_path) -> None:
    result = run_stage110_claim_gate(stage105_manifest_path=tmp_path / "missing105.json", stage109_results_path=tmp_path / "missing109.json")

    assert result["status"] == "incomplete"
    assert result["decision"] == "REPLICATED_ADVANTAGE_CLAIM_GATE_INCOMPLETE"
    assert len(result["missing_source_artifacts"]) == 2


def test_stage110_blocks_when_stage109_intake_is_incomplete(tmp_path) -> None:
    _write_json(tmp_path / "stage105.json", {"decision": "INDEPENDENT_RERUN_PROTOCOL_PREREGISTERED_EXECUTION_REQUIRED"})
    _write_json(tmp_path / "stage109.json", {"decision": "WINDOW_EVIDENCE_INTAKE_BLOCKED_EVIDENCE_MISSING", "window_records": []})

    result = run_stage110_claim_gate(stage105_manifest_path=tmp_path / "stage105.json", stage109_results_path=tmp_path / "stage109.json")

    assert result["decision"] == "REPLICATED_ADVANTAGE_CLAIM_BLOCKED_EVIDENCE_INTAKE_INCOMPLETE"
    assert result["stage109_ready_for_aggregation"] is False


def test_stage110_blocks_when_stage105_preregistration_is_missing(tmp_path) -> None:
    _write_json(tmp_path / "stage105.json", {"decision": "unexpected"})
    _write_json(tmp_path / "stage109.json", _ready_stage109(tmp_path))

    result = run_stage110_claim_gate(stage105_manifest_path=tmp_path / "stage105.json", stage109_results_path=tmp_path / "stage109.json")

    assert result["decision"] == "REPLICATED_ADVANTAGE_CLAIM_BLOCKED_EVIDENCE_INTAKE_INCOMPLETE"
    assert result["stage105_preregistered"] is False
    assert result["ready_for_stage105_aggregation"] is False
    assert result["window_metric_record_count"] == 0


def test_stage110_supports_replicated_advantage_when_every_window_passes(tmp_path) -> None:
    _write_json(tmp_path / "stage105.json", {"decision": "INDEPENDENT_RERUN_PROTOCOL_PREREGISTERED_EXECUTION_REQUIRED"})
    _write_json(tmp_path / "stage109.json", _ready_stage109(tmp_path))

    result = run_stage110_claim_gate(stage105_manifest_path=tmp_path / "stage105.json", stage109_results_path=tmp_path / "stage109.json")

    assert result["decision"] == "PHASEWRAP_REPLICATED_ADVANTAGE_SUPPORTED_BY_STAGE105_RULE"
    assert result["replicated_advantage_count"] == 1
    assert result["replication_records"][0]["passing_window_count"] == 2


def test_stage110_rejects_summary_shaped_stage103_without_ready_decision(tmp_path) -> None:
    _write_json(tmp_path / "stage105.json", {"decision": "INDEPENDENT_RERUN_PROTOCOL_PREREGISTERED_EXECUTION_REQUIRED"})
    stage109 = _ready_stage109(tmp_path)
    _write_json(tmp_path / "stage109.json", stage109)
    stage103_path = tmp_path / "windows" / "ibm_runtime__independent_window_00" / "stage103" / "results.json"
    stage103 = json.loads(stage103_path.read_text(encoding="utf-8"))
    stage103.pop("decision")
    _write_json(stage103_path, stage103)

    result = run_stage110_claim_gate(stage105_manifest_path=tmp_path / "stage105.json", stage109_results_path=tmp_path / "stage109.json")

    assert result["decision"] == "PHASEWRAP_REPLICATED_ADVANTAGE_NOT_SUPPORTED_BY_STAGE105_RULE"
    assert result["replicated_advantage_count"] == 0
    assert result["window_metric_records"][0]["stage103_ready_for_interpretation"] is False
    assert result["window_metric_records"][0]["passes_stage103_advantage_rule"] is False


def test_stage110_rejects_stage103_without_readiness_counters(tmp_path) -> None:
    _write_json(tmp_path / "stage105.json", {"decision": "INDEPENDENT_RERUN_PROTOCOL_PREREGISTERED_EXECUTION_REQUIRED"})
    stage109 = _ready_stage109(tmp_path)
    _write_json(tmp_path / "stage109.json", stage109)
    stage103_path = tmp_path / "windows" / "ibm_runtime__independent_window_00" / "stage103" / "results.json"
    stage103 = json.loads(stage103_path.read_text(encoding="utf-8"))
    stage103["comparison_groups_complete"] = False
    _write_json(stage103_path, stage103)

    result = run_stage110_claim_gate(stage105_manifest_path=tmp_path / "stage105.json", stage109_results_path=tmp_path / "stage109.json")

    assert result["decision"] == "PHASEWRAP_REPLICATED_ADVANTAGE_NOT_SUPPORTED_BY_STAGE105_RULE"
    assert result["replicated_advantage_count"] == 0
    first_window = result["window_metric_records"][0]
    assert first_window["stage103_ready_for_interpretation"] is False
    assert first_window["stage103_comparison_groups_complete"] is False
    assert first_window["passes_stage103_advantage_rule"] is False


def test_stage110_rejects_stage103_without_stage104_matched_surface_readiness(tmp_path) -> None:
    _write_json(tmp_path / "stage105.json", {"decision": "INDEPENDENT_RERUN_PROTOCOL_PREREGISTERED_EXECUTION_REQUIRED"})
    stage109 = _ready_stage109(tmp_path)
    _write_json(tmp_path / "stage109.json", stage109)
    stage103_path = tmp_path / "windows" / "ibm_runtime__independent_window_00" / "stage103" / "results.json"
    stage103 = json.loads(stage103_path.read_text(encoding="utf-8"))
    stage103["stage104_matched_surface_ready"] = False
    _write_json(stage103_path, stage103)

    result = run_stage110_claim_gate(stage105_manifest_path=tmp_path / "stage105.json", stage109_results_path=tmp_path / "stage109.json")

    assert result["decision"] == "PHASEWRAP_REPLICATED_ADVANTAGE_NOT_SUPPORTED_BY_STAGE105_RULE"
    assert result["replicated_advantage_count"] == 0
    first_window = result["window_metric_records"][0]
    assert first_window["stage103_ready_for_interpretation"] is False
    assert first_window["stage103_stage104_matched_surface_ready"] is False
    assert first_window["passes_stage103_advantage_rule"] is False


def test_stage110_rejects_stage103_without_live_submit_provenance(tmp_path) -> None:
    _write_json(tmp_path / "stage105.json", {"decision": "INDEPENDENT_RERUN_PROTOCOL_PREREGISTERED_EXECUTION_REQUIRED"})
    stage109 = _ready_stage109(tmp_path)
    _write_json(tmp_path / "stage109.json", stage109)
    stage103_path = tmp_path / "windows" / "ibm_runtime__independent_window_00" / "stage103" / "results.json"
    stage103 = json.loads(stage103_path.read_text(encoding="utf-8"))
    stage103["stage113_live_submit_provenance_ready"] = False
    _write_json(stage103_path, stage103)

    result = run_stage110_claim_gate(stage105_manifest_path=tmp_path / "stage105.json", stage109_results_path=tmp_path / "stage109.json")

    assert result["decision"] == "PHASEWRAP_REPLICATED_ADVANTAGE_NOT_SUPPORTED_BY_STAGE105_RULE"
    assert result["replicated_advantage_count"] == 0
    first_window = result["window_metric_records"][0]
    assert first_window["stage103_ready_for_interpretation"] is False
    assert first_window["stage103_stage113_live_submit_provenance_ready"] is False
    assert first_window["passes_stage103_advantage_rule"] is False


def test_stage110_rejects_stage103_summary_provider_mismatch(tmp_path) -> None:
    _write_json(tmp_path / "stage105.json", {"decision": "INDEPENDENT_RERUN_PROTOCOL_PREREGISTERED_EXECUTION_REQUIRED"})
    stage109 = _ready_stage109(tmp_path)
    _write_json(tmp_path / "stage109.json", stage109)
    stage103_path = tmp_path / "windows" / "ibm_runtime__independent_window_00" / "stage103" / "results.json"
    stage103 = json.loads(stage103_path.read_text(encoding="utf-8"))
    stage103["comparison_summary"][0]["provider"] = "amazon_braket"
    _write_json(stage103_path, stage103)

    result = run_stage110_claim_gate(stage105_manifest_path=tmp_path / "stage105.json", stage109_results_path=tmp_path / "stage109.json")

    assert result["decision"] == "PHASEWRAP_REPLICATED_ADVANTAGE_NOT_SUPPORTED_BY_STAGE105_RULE"
    assert result["replicated_advantage_count"] == 0
    first_window = result["window_metric_records"][0]
    assert first_window["provider"] == "amazon_braket"
    assert first_window["window_provider"] == "ibm_runtime"
    assert first_window["passes_stage103_advantage_rule"] is False


def test_stage110_rejects_replicated_advantage_when_any_window_fails(tmp_path) -> None:
    _write_json(tmp_path / "stage105.json", {"decision": "INDEPENDENT_RERUN_PROTOCOL_PREREGISTERED_EXECUTION_REQUIRED"})
    _write_json(tmp_path / "stage109.json", _ready_stage109(tmp_path, second_window_passes=False))

    result = run_stage110_claim_gate(stage105_manifest_path=tmp_path / "stage105.json", stage109_results_path=tmp_path / "stage109.json")

    assert result["decision"] == "PHASEWRAP_REPLICATED_ADVANTAGE_NOT_SUPPORTED_BY_STAGE105_RULE"
    assert result["replicated_advantage_count"] == 0
    assert result["replication_records"][0]["passing_window_count"] == 1


def test_stage110_outputs_are_written(tmp_path) -> None:
    _write_json(tmp_path / "stage105.json", {"decision": "INDEPENDENT_RERUN_PROTOCOL_PREREGISTERED_EXECUTION_REQUIRED"})
    _write_json(tmp_path / "stage109.json", _ready_stage109(tmp_path))
    result = run_stage110_claim_gate(stage105_manifest_path=tmp_path / "stage105.json", stage109_results_path=tmp_path / "stage109.json")

    paths = write_stage110_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert manifest["replicated_advantage_count"] == 1
    assert "lane_a" in summary
