from __future__ import annotations

import json

from qrope.stage147_first_provider_calibration_confidence_audit import run_stage147_audit, write_stage147_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _fixture(tmp_path) -> tuple[object, object]:
    template_dir = tmp_path / "templates"
    stage145 = tmp_path / "stage145.json"
    _write_json(stage145, {"first_unlock_provider": "ibm_runtime"})
    _write_json(
        template_dir / "ibm_runtime_known_state_execution.json",
        {
            "provider": "ibm_runtime",
            "expected_bitstring_order": "q1q0",
            "shots_per_state": 1000,
            "raw_counts_by_state": [
                {"state": "00", "expected_dominant_key": "00"},
                {"state": "01", "expected_dominant_key": "10"},
                {"state": "10", "expected_dominant_key": "01"},
                {"state": "11", "expected_dominant_key": "11"},
            ],
        },
    )
    return template_dir, stage145


def test_stage147_computes_wilson_calibration_thresholds(tmp_path) -> None:
    template_dir, stage145 = _fixture(tmp_path)

    result = run_stage147_audit(stage102_template_dir=template_dir, stage145_results_path=stage145)

    assert result["decision"] == "FIRST_PROVIDER_CALIBRATION_CONFIDENCE_CONTRACT_READY_COUNTS_REQUIRED"
    assert result["provider_scope"] == "ibm_runtime"
    assert result["expected_bitstring_order"] == "q1q0"
    assert result["state_count"] == 4
    assert result["state_records"][0]["minimum_stage101_dominant_count"] == 800
    assert result["state_records"][0]["minimum_wilson95_dominant_count"] == 825


def test_stage147_reports_incomplete_without_template(tmp_path) -> None:
    stage145 = tmp_path / "stage145.json"
    _write_json(stage145, {"first_unlock_provider": "ibm_runtime"})

    result = run_stage147_audit(stage102_template_dir=tmp_path / "missing_templates", stage145_results_path=stage145)

    assert result["decision"] == "FIRST_PROVIDER_CALIBRATION_CONFIDENCE_CONTRACT_INCOMPLETE"
    assert result["missing_source_artifacts"]


def test_stage147_outputs_are_written(tmp_path) -> None:
    template_dir, stage145 = _fixture(tmp_path)
    result = run_stage147_audit(stage102_template_dir=template_dir, stage145_results_path=stage145)

    written = write_stage147_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(written) == {"manifest", "result", "summary_csv"}
    assert manifest["decision"] == "FIRST_PROVIDER_CALIBRATION_CONFIDENCE_CONTRACT_READY_COUNTS_REQUIRED"
    assert "minimum_wilson95_dominant_count" in summary
