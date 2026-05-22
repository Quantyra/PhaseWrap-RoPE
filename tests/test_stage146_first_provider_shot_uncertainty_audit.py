from __future__ import annotations

import json

from qrope.stage146_first_provider_shot_uncertainty_audit import run_stage146_audit, write_stage146_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _packet(family: str) -> dict[str, object]:
    return {
        "packet_id": f"packet_{family}",
        "source_lane_id": "lane_a",
        "encoding_family": family,
        "circuit_template": "two_ry_product_state_z_readout_v1",
        "shot_count": 4096,
        "row_count": 16,
    }


def _write_fixture(tmp_path) -> tuple[object, object]:
    plans = tmp_path / "plans.json"
    stage145 = tmp_path / "stage145.json"
    _write_json(stage145, {"first_unlock_provider": "ibm_runtime"})
    _write_json(
        plans,
        [
            {
                "provider": "ibm_runtime",
                "window_id": "ibm_window_0",
                "steps": [
                    {
                        "step_id": "matched_packet_execution",
                        "packet_templates": [
                            _packet("phasewrap"),
                            _packet("rope_like"),
                            _packet("sinusoidal_like"),
                            _packet("alibi_like"),
                            _packet("no_position_control"),
                        ],
                    }
                ],
            },
            {
                "provider": "amazon_braket",
                "window_id": "braket_window_0",
                "steps": [
                    {
                        "step_id": "matched_packet_execution",
                        "packet_templates": [_packet("phasewrap")],
                    }
                ],
            },
        ],
    )
    return plans, stage145


def test_stage146_computes_first_provider_uncertainty_contract(tmp_path) -> None:
    plans, stage145 = _write_fixture(tmp_path)

    result = run_stage146_audit(stage107_window_plans_path=plans, stage145_results_path=stage145)

    assert result["decision"] == "FIRST_PROVIDER_SHOT_UNCERTAINTY_CONTRACT_READY_HARDWARE_COUNTS_REQUIRED"
    assert result["provider_scope"] == "ibm_runtime"
    assert result["window_count"] == 1
    assert result["packet_count"] == 5
    assert result["lane_summaries"][0]["minimum_phasewrap_mae_margin_for_95pct_shot_noise_separation"] == 0.003828125


def test_stage146_reports_incomplete_without_first_provider(tmp_path) -> None:
    plans, _ = _write_fixture(tmp_path)
    missing_stage145 = tmp_path / "missing.json"

    result = run_stage146_audit(stage107_window_plans_path=plans, stage145_results_path=missing_stage145)

    assert result["decision"] == "FIRST_PROVIDER_SHOT_UNCERTAINTY_CONTRACT_INCOMPLETE"
    assert result["missing_source_artifacts"]


def test_stage146_outputs_are_written(tmp_path) -> None:
    plans, stage145 = _write_fixture(tmp_path)
    result = run_stage146_audit(stage107_window_plans_path=plans, stage145_results_path=stage145)

    written = write_stage146_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(written) == {"manifest", "result", "summary_csv"}
    assert manifest["decision"] == "FIRST_PROVIDER_SHOT_UNCERTAINTY_CONTRACT_READY_HARDWARE_COUNTS_REQUIRED"
    assert "minimum_phasewrap_mae_margin_for_95pct_shot_noise_separation" in summary
