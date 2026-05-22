from __future__ import annotations

import json

from qrope.stage168_real_source_seed_expansion_plan import run_stage168_expansion_plan, write_stage168_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _record(seed: int, family: str, lane_kind: str) -> dict:
    return {
        "provider": "ibm_runtime",
        "seed": seed,
        "family": family,
        "lane_id": f"ibm_{lane_kind}_seed{seed}_rows16_shots4096",
        "rows": 16,
        "shots": 4096,
    }


def test_stage168_requires_real_ibm_seed_expansion_when_only_one_pair_exists(tmp_path) -> None:
    stage4 = tmp_path / "stage4.json"
    stage167 = tmp_path / "stage167.json"
    _write_json(
        stage4,
        {
            "records": [
                _record(314, "two_qubit_zz_expectation_phase_wrap_v1", "product"),
                _record(314, "two_qubit_cx_parity_phase_wrap_v2", "cx"),
            ]
        },
    )
    _write_json(stage167, {"decision": "EXPANDED_SIMULATED_SEED_STRESS_DOES_NOT_SUPPORT_BROADENED_HARDWARE_PROBE"})

    result = run_stage168_expansion_plan(stage4_manifest_path=stage4, stage167_results_path=stage167)

    assert result["decision"] == "REAL_SOURCE_SEED_EXPANSION_REQUIRED_BEFORE_BROADENED_SCOPE"
    assert result["current_real_ibm_seed_pair_count"] == 1
    assert result["missing_real_ibm_seed_pair_count"] == 1
    assert len(result["recommended_expansion_requests"]) == 2
    assert "real_ibm_seed_pair_count_below_broadened_scope_threshold" in result["blockers"]


def test_stage168_allows_broadened_scope_only_with_real_seeds_and_supportive_stress(tmp_path) -> None:
    stage4 = tmp_path / "stage4.json"
    stage167 = tmp_path / "stage167.json"
    _write_json(
        stage4,
        {
            "records": [
                _record(314, "two_qubit_zz_expectation_phase_wrap_v1", "product"),
                _record(314, "two_qubit_cx_parity_phase_wrap_v2", "cx"),
                _record(577, "two_qubit_zz_expectation_phase_wrap_v1", "product"),
                _record(577, "two_qubit_cx_parity_phase_wrap_v2", "cx"),
            ]
        },
    )
    _write_json(stage167, {"decision": "EXPANDED_SIMULATED_SEED_STRESS_SUPPORTS_BROADENED_HARDWARE_PROBE"})

    result = run_stage168_expansion_plan(stage4_manifest_path=stage4, stage167_results_path=stage167)

    assert result["decision"] == "REAL_SOURCE_SEED_EXPANSION_NOT_REQUIRED_FOR_BROADENED_SCOPE"
    assert result["blockers"] == []
    assert result["recommended_expansion_requests"] == []


def test_stage168_outputs_are_written(tmp_path) -> None:
    stage4 = tmp_path / "stage4.json"
    stage167 = tmp_path / "stage167.json"
    _write_json(
        stage4,
        {
            "records": [
                _record(314, "two_qubit_zz_expectation_phase_wrap_v1", "product"),
                _record(314, "two_qubit_cx_parity_phase_wrap_v2", "cx"),
            ]
        },
    )
    _write_json(stage167, {"decision": "EXPANDED_SIMULATED_SEED_STRESS_DOES_NOT_SUPPORT_BROADENED_HARDWARE_PROBE"})
    result = run_stage168_expansion_plan(stage4_manifest_path=stage4, stage167_results_path=stage167)

    paths = write_stage168_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert manifest["current_real_ibm_seed_pair_count"] == 1
    assert "ibm_product_seed577_rows16_shots4096" in summary
