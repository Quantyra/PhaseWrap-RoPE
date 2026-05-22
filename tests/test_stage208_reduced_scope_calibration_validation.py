from __future__ import annotations

import json

from qrope.stage208_reduced_scope_calibration_validation import run_stage208_reduced_scope_calibration_validation, write_stage208_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _stage207(path, *, reverse_order: bool = True) -> None:
    rows = [
        ("00", "00"),
        ("01", "10" if reverse_order else "01"),
        ("10", "01" if reverse_order else "10"),
        ("11", "11"),
    ]
    _write_json(
        path,
        {
            "decision": "REDUCED_SCOPE_RESULT_COUNTS_COLLECTED_READY_FOR_CALIBRATION",
            "collected_templates": [
                {
                    "template_type": "reduced_scope_known_state_calibration_counts",
                    "raw_counts_by_state": [
                        {"state": state, "counts": {key: 950, "00" if key != "00" else "11": 50}}
                        for state, key in rows
                    ],
                }
            ],
        },
    )


def test_stage208_validates_reversed_q1q0_order(tmp_path) -> None:
    stage207 = tmp_path / "stage207.json"
    _stage207(stage207, reverse_order=True)

    result = run_stage208_reduced_scope_calibration_validation(stage207_results_path=stage207)

    assert result["decision"] == "REDUCED_SCOPE_CALIBRATION_VALIDATED_READY_FOR_METRICS"
    assert result["inferred_bitstring_order"] == "q1q0"
    assert result["blockers"] == []


def test_stage208_validates_direct_q0q1_order(tmp_path) -> None:
    stage207 = tmp_path / "stage207.json"
    _stage207(stage207, reverse_order=False)

    result = run_stage208_reduced_scope_calibration_validation(stage207_results_path=stage207)

    assert result["decision"] == "REDUCED_SCOPE_CALIBRATION_VALIDATED_READY_FOR_METRICS"
    assert result["inferred_bitstring_order"] == "q0q1"


def test_stage208_outputs_do_not_record_secrets_or_live_submit(tmp_path) -> None:
    stage207 = tmp_path / "stage207.json"
    _stage207(stage207)
    result = run_stage208_reduced_scope_calibration_validation(stage207_results_path=stage207)

    paths = write_stage208_outputs(result, tmp_path / "out")
    written = (tmp_path / "out" / "results.json").read_text(encoding="utf-8")
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert "IBM_QUANTUM_TOKEN" not in written
    assert "QISKIT_IBM_TOKEN" not in written
    assert "crn:v1" not in written
    assert "--allow-live-submit" not in written
    assert "--allow-live-submit" not in summary
