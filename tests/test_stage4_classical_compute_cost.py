from __future__ import annotations

import json

from scripts.estimate_stage4_classical_compute_cost import (
    SCHEMA_VERSION,
    build_cost_estimate,
    elapsed_seconds,
    estimate_classical_ops,
    write_outputs,
)


def _verification_fixture() -> dict:
    return {
        "records": [
            {
                "record_id": "synthetic-record",
                "provider": "ibm_runtime",
                "backend_label": "Synthetic Backend",
                "family": "two_qubit_zz_expectation_phase_wrap_v1",
                "row_count": 4,
                "shots": 256,
                "submitted_at_utc": "2026-01-01T00:00:00Z",
                "completed_at_utc": "2026-01-01T00:00:10Z",
                "pass": True,
            },
            {
                "record_id": "failed-record",
                "provider": "ibm_runtime",
                "backend_label": "Failed Backend",
                "family": "two_qubit_zz_expectation_phase_wrap_v1",
                "row_count": 4,
                "shots": 256,
                "pass": False,
            },
        ]
    }


def test_elapsed_seconds_parses_utc_z_timestamps() -> None:
    assert elapsed_seconds("2026-01-01T00:00:00Z", "2026-01-01T00:00:10Z") == 10.0
    assert elapsed_seconds(None, "2026-01-01T00:00:10Z") is None


def test_estimate_classical_ops_is_deterministic() -> None:
    ops = estimate_classical_ops(4)
    assert ops["bitstring_bins_per_row"] == 4
    assert ops["total_static_ops"] == 256


def test_build_cost_estimate_filters_to_passing_records() -> None:
    result = build_cost_estimate(_verification_fixture(), assumed_ops_per_second=1_000.0)
    assert result["schema_version"] == SCHEMA_VERSION
    assert result["record_count"] == 1
    assert result["records"][0]["total_hardware_shots"] == 1024
    assert result["records"][0]["recorded_hardware_elapsed_seconds"] == 10.0
    assert result["records"][0]["classical_static_ops"] == 256
    assert result["records"][0]["classical_estimated_seconds_at_assumed_rate"] == 0.256
    assert result["totals"]["classical_estimated_cost_usd"] == 0.0


def test_write_outputs(tmp_path) -> None:
    result = build_cost_estimate(_verification_fixture())
    paths = write_outputs(result, tmp_path)
    manifest = json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))
    saved = json.loads((tmp_path / "results.json").read_text(encoding="utf-8"))
    assert set(paths) == {"manifest", "results", "summary_csv"}
    assert manifest["schema_version"] == SCHEMA_VERSION
    assert saved["records"] == result["records"]
    assert (tmp_path / "summary.csv").exists()
