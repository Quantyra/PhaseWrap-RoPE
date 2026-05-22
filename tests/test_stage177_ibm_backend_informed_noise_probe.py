from __future__ import annotations

import json

from qrope.stage177_ibm_backend_informed_noise_probe import (
    run_stage177_ibm_backend_informed_noise_probe,
    write_stage177_outputs,
)


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _sources(tmp_path):
    stage159 = tmp_path / "stage159.json"
    stage169 = tmp_path / "stage169.json"
    _write_json(stage159, {"decision": "FIRST_PROVIDER_BACKEND_PREFLIGHT_READY_AWAITING_APPROVAL"})
    _write_json(
        stage169,
        {
            "decision": "TARGETED_IBM_PROBE_SCOPE_LOCKED_TO_STABLE_LANES",
            "stable_target_lanes": ["ibm_cx_seed314_rows16_shots4096", "ibm_product_seed314_rows16_shots4096"],
        },
    )
    return stage159, stage169


def _packet(path, lane_id: str, family: str, circuit_template: str, component_a: float, component_b: float) -> None:
    score = 0.5 + 0.25 * (component_a + component_b)
    _write_json(
        path,
        {
            "packet_id": f"{lane_id}__{family}",
            "provider": "ibm_runtime",
            "source_lane_id": lane_id,
            "encoding_family": family,
            "shot_count": 4096,
            "fixed_width": {"circuit_template": circuit_template},
            "rows": [
                {
                    "row_id": "row_0",
                    "components": {"component_a": component_a, "component_b": component_b},
                    "ideal_predictions": {"score": score},
                }
            ],
        },
    )


def _manifests(tmp_path, *, phasewrap_components=(0.0, 0.0)):
    packet_dir = tmp_path / "packets"
    packet_paths = []
    lanes = {
        "ibm_product_seed314_rows16_shots4096": "two_ry_product_state_z_readout_v1",
        "ibm_cx_seed314_rows16_shots4096": "two_ry_cx_parity_z_readout_v1",
    }
    specs = {
        "phasewrap": phasewrap_components,
        "rope_like": (1.0, 1.0),
        "sinusoidal_like": (0.8, 0.8),
        "alibi_like": (0.6, 0.6),
        "no_position_control": (0.2, 0.2),
    }
    for lane_id, template in lanes.items():
        for family, components in specs.items():
            path = packet_dir / f"{lane_id}__{family}.json"
            _packet(path, lane_id, family, template, *components)
            packet_paths.append(str(path.as_posix()))
    stage99 = tmp_path / "stage99.json"
    stage100 = tmp_path / "stage100.json"
    _write_json(stage99, {"packet_paths": packet_paths[:5]})
    _write_json(stage100, {"packet_paths": packet_paths[5:]})
    return stage99, stage100


def _snapshot() -> dict:
    qubit = [
        {"name": "readout_error", "value": 0.012},
        {"name": "T1", "value": 120000.0},
        {"name": "T2", "value": 90000.0},
    ]
    return {
        "backend": "ibm_fez",
        "num_qubits": 156,
        "operational": True,
        "pending_jobs": 3,
        "coupling_edge_count": 352,
        "last_update_date": "2026-05-22T00:00:00Z",
        "qubits": [qubit, qubit],
        "gates": [
            {"gate": "sx", "qubits": [0], "parameters": [{"name": "gate_error", "value": 0.0002}]},
            {"gate": "x", "qubits": [1], "parameters": [{"name": "gate_error", "value": 0.0003}]},
            {"gate": "ecr", "qubits": [0, 1], "parameters": [{"name": "gate_error", "value": 0.008}]},
        ],
    }


def test_stage177_supports_targeted_run_when_primary_ibm_stochastic_model_wins(tmp_path) -> None:
    stage159, stage169 = _sources(tmp_path)
    stage99, stage100 = _manifests(tmp_path)

    result = run_stage177_ibm_backend_informed_noise_probe(
        stage159_results_path=stage159,
        stage169_results_path=stage169,
        stage99_manifest_path=stage99,
        stage100_manifest_path=stage100,
        allow_backend_properties_lookup=True,
        backend_snapshot_lookup=lambda env: _snapshot(),
    )

    assert result["decision"] == "IBM_BACKEND_INFORMED_SIM_SUPPORTS_TARGETED_HARDWARE_RUN"
    assert result["backend_property_stats"]["readout_error_median"] == 0.012
    assert result["primary_stable_target_count"] >= 2
    assert result["no_hardware_submission"] is True


def test_stage177_blocks_without_explicit_read_only_lookup_flag(tmp_path) -> None:
    stage159, stage169 = _sources(tmp_path)
    stage99, stage100 = _manifests(tmp_path)

    result = run_stage177_ibm_backend_informed_noise_probe(
        stage159_results_path=stage159,
        stage169_results_path=stage169,
        stage99_manifest_path=stage99,
        stage100_manifest_path=stage100,
        allow_backend_properties_lookup=False,
        backend_snapshot_lookup=lambda env: _snapshot(),
    )

    assert result["decision"] == "IBM_BACKEND_INFORMED_NOISE_PROBE_INCOMPLETE"
    assert "backend_properties_lookup_not_requested" in result["blockers"]


def test_stage177_outputs_omit_secrets_and_live_submit_commands(tmp_path) -> None:
    stage159, stage169 = _sources(tmp_path)
    stage99, stage100 = _manifests(tmp_path)
    result = run_stage177_ibm_backend_informed_noise_probe(
        stage159_results_path=stage159,
        stage169_results_path=stage169,
        stage99_manifest_path=stage99,
        stage100_manifest_path=stage100,
        env={"IBM_QUANTUM_TOKEN": "token", "IBM_QUANTUM_INSTANCE_CRN": "crn:v1:secret"},
        allow_backend_properties_lookup=True,
        backend_snapshot_lookup=lambda env: _snapshot(),
    )

    paths = write_stage177_outputs(result, tmp_path / "out")
    written = (tmp_path / "out" / "results.json").read_text(encoding="utf-8")
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert "IBM_QUANTUM_TOKEN" not in written
    assert "crn:v1" not in written
    assert "--allow-live-submit" not in written
    assert "--allow-live-submit" not in summary
