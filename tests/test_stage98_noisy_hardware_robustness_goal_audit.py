from __future__ import annotations

import json

from qrope.stage98_noisy_hardware_robustness_goal_audit import run_stage98_audit, write_stage98_outputs


def _write_json(root, relative: str, payload: dict[str, object]) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def test_stage98_frames_noisy_hardware_goal_with_matched_encoding_gap(tmp_path) -> None:
    _write_json(
        tmp_path,
        "stage4_hardware_sweep/manifest.json",
        {
            "records": [
                {
                    "provider": "ibm_runtime",
                    "family": "two_qubit_zz_expectation_phase_wrap_v1",
                    "row_count": 16,
                    "shots": 4096,
                }
            ],
            "bounded_claim_statement": "bounded",
        },
    )
    _write_json(
        tmp_path,
        "stage4_hardware_sweep/offline_verification.json",
        {
            "pass": True,
            "table": [{"outcome": "hardware-positive"}],
        },
    )
    _write_json(tmp_path, "stage4_bitstring_calibration/manifest.json", {"packet_specs": []})
    _write_json(tmp_path, "stage4_bitstring_calibration/offline_verification.json", {"status": "missing-evidence", "pass": False})

    result = run_stage98_audit(artifact_root=tmp_path)

    assert result["stage"] == "stage98_noisy_hardware_robustness_goal_audit"
    assert result["status"] == "completed"
    assert result["decision"]["decision"] == "NOISY_HARDWARE_GOAL_FRAMED_MATCHED_ENCODINGS_REQUIRED"
    assert "matched_positional_score_encodings" in result["decision"]["missing_requirements"]
    assert result["stage4_summary"]["fixed_width_current_records"] is True
    assert result["bitstring_calibration_status"]["known_state_counts_present"] is False
    assert "Noisy quantum hardware improves language-model performance." in result["unsupported_claims"]


def test_stage98_reports_missing_source_artifacts(tmp_path) -> None:
    result = run_stage98_audit(artifact_root=tmp_path)

    assert result["missing_source_artifacts"]
    assert result["stage4_summary"]["active_record_count"] == 0


def test_stage98_outputs_are_written(tmp_path) -> None:
    result = run_stage98_audit(artifact_root=tmp_path)
    paths = write_stage98_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((tmp_path / "out" / "results.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert manifest["stage"] == "stage98_noisy_hardware_robustness_goal_audit"
    assert saved["objective"] == result["objective"]
    assert "matched_positional_score_encodings" in summary
