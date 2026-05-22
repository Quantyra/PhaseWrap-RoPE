from __future__ import annotations

import json

from qrope.stage166_simulated_evidence_sufficiency_audit import run_stage166_sufficiency_audit, write_stage166_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _manifest(*lanes):
    return {"packet_paths": [f"logs/packets/{lane}__phasewrap.json" for lane in lanes]}


def _stage165(*targets):
    return {
        "decision": "SIMULATED_NOISE_STABLE_TARGETED_HARDWARE_PROBE_RECOMMENDED",
        "target_records": list(targets),
    }


def _target(provider, lane, template, noise_model="ry_offset_0p02rad"):
    return {
        "provider": provider,
        "source_lane_id": lane,
        "circuit_template": template,
        "noise_model_id": noise_model,
        "stable_target": True,
    }


def test_stage166_separates_targeted_probe_from_broad_claim(tmp_path) -> None:
    stage99 = tmp_path / "stage99.json"
    stage100 = tmp_path / "stage100.json"
    stage153 = tmp_path / "stage153.json"
    stage165 = tmp_path / "stage165.json"
    _write_json(stage99, _manifest("ibm_product_seed314_rows16_shots4096"))
    _write_json(stage100, _manifest("ibm_cx_seed314_rows16_shots4096"))
    _write_json(stage153, {"decision": "SIMULATED_NOISE_PHASEWRAP_STRICT_ADVANTAGE_OBSERVED"})
    _write_json(
        stage165,
        _stage165(
            _target("ibm_runtime", "ibm_product_seed314_rows16_shots4096", "two_ry_product_state_z_readout_v1"),
            _target("ibm_runtime", "ibm_cx_seed314_rows16_shots4096", "two_ry_cx_parity_z_readout_v1"),
        ),
    )

    result = run_stage166_sufficiency_audit(
        stage99_manifest_path=stage99,
        stage100_manifest_path=stage100,
        stage153_results_path=stage153,
        stage165_results_path=stage165,
    )

    assert result["decision"] == "SIMULATED_EVIDENCE_TARGETED_PROBE_READY_BROAD_CLAIM_INSUFFICIENT"
    assert result["targeted_probe_ready_providers"] == ["ibm_runtime"]
    assert result["broad_simulated_claim_ready_providers"] == []
    record = result["stable_provider_records"][0]
    assert record["stable_seed_count"] == 1
    assert "stable_seed_count_below_broad_claim_threshold" in record["broad_claim_blockers"]
    assert "stable_noise_model_count_below_broad_claim_threshold" in record["broad_claim_blockers"]


def test_stage166_marks_broad_claim_ready_when_seed_and_noise_thresholds_clear(tmp_path) -> None:
    stage99 = tmp_path / "stage99.json"
    stage100 = tmp_path / "stage100.json"
    stage153 = tmp_path / "stage153.json"
    stage165 = tmp_path / "stage165.json"
    _write_json(stage99, _manifest("ibm_product_seed314_rows16_shots4096", "ibm_product_seed2718_rows16_shots4096"))
    _write_json(stage100, _manifest("ibm_cx_seed314_rows16_shots4096", "ibm_cx_seed2718_rows16_shots4096"))
    _write_json(stage153, {"decision": "SIMULATED_NOISE_PHASEWRAP_STRICT_ADVANTAGE_OBSERVED"})
    _write_json(
        stage165,
        _stage165(
            _target("ibm_runtime", "ibm_product_seed314_rows16_shots4096", "two_ry_product_state_z_readout_v1"),
            _target("ibm_runtime", "ibm_cx_seed314_rows16_shots4096", "two_ry_cx_parity_z_readout_v1"),
            _target("ibm_runtime", "ibm_product_seed2718_rows16_shots4096", "two_ry_product_state_z_readout_v1", "biased_observable_plus_2pct"),
            _target("ibm_runtime", "ibm_cx_seed2718_rows16_shots4096", "two_ry_cx_parity_z_readout_v1", "biased_observable_plus_2pct"),
        ),
    )

    result = run_stage166_sufficiency_audit(
        stage99_manifest_path=stage99,
        stage100_manifest_path=stage100,
        stage153_results_path=stage153,
        stage165_results_path=stage165,
    )

    assert result["decision"] == "SIMULATED_EVIDENCE_BROAD_CLAIM_READY_PENDING_HARDWARE"
    assert result["broad_simulated_claim_ready_providers"] == ["ibm_runtime"]
    assert result["stable_provider_records"][0]["broad_claim_blockers"] == []


def test_stage166_outputs_are_written(tmp_path) -> None:
    stage99 = tmp_path / "stage99.json"
    stage100 = tmp_path / "stage100.json"
    stage153 = tmp_path / "stage153.json"
    stage165 = tmp_path / "stage165.json"
    _write_json(stage99, _manifest("ibm_product_seed314_rows16_shots4096"))
    _write_json(stage100, _manifest("ibm_cx_seed314_rows16_shots4096"))
    _write_json(stage153, {"decision": "SIMULATED_NOISE_PHASEWRAP_STRICT_ADVANTAGE_OBSERVED"})
    _write_json(
        stage165,
        _stage165(
            _target("ibm_runtime", "ibm_product_seed314_rows16_shots4096", "two_ry_product_state_z_readout_v1"),
            _target("ibm_runtime", "ibm_cx_seed314_rows16_shots4096", "two_ry_cx_parity_z_readout_v1"),
        ),
    )
    result = run_stage166_sufficiency_audit(
        stage99_manifest_path=stage99,
        stage100_manifest_path=stage100,
        stage153_results_path=stage153,
        stage165_results_path=stage165,
    )

    paths = write_stage166_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert manifest["targeted_probe_ready_providers"] == ["ibm_runtime"]
    assert "stable_seed_count_below_broad_claim_threshold" in summary
