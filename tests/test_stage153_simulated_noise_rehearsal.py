from __future__ import annotations

import json

from qrope.stage153_simulated_noise_rehearsal import run_stage153_simulated_noise_rehearsal, write_stage153_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _packet(path, packet_id: str, family: str, component_a: float, component_b: float) -> None:
    score = 0.5 + 0.25 * (component_a + component_b)
    _write_json(
        path,
        {
            "packet_id": packet_id,
            "provider": "simulated_provider",
            "source_lane_id": "lane_0",
            "encoding_family": family,
            "shot_count": 1000,
            "fixed_width": {
                "circuit_template": "two_ry_product_state_z_readout_v1",
            },
            "rows": [
                {
                    "row_id": "row_0",
                    "components": {"component_a": component_a, "component_b": component_b},
                    "ideal_predictions": {"score": score},
                }
            ],
        },
    )


def _manifests(tmp_path, specs: dict[str, tuple[float, float]]):
    packet_dir = tmp_path / "packets"
    packet_paths = []
    for family, components in specs.items():
        path = packet_dir / f"lane_0__{family}.json"
        _packet(path, f"lane_0__{family}", family, *components)
        packet_paths.append(str(path.as_posix()))
    stage99 = tmp_path / "stage99.json"
    stage100 = tmp_path / "stage100.json"
    _write_json(stage99, {"packet_paths": packet_paths})
    _write_json(stage100, {"packet_paths": []})
    return stage99, stage100


def test_stage153_reports_strict_simulated_advantage_when_phasewrap_is_more_noise_stable(tmp_path) -> None:
    stage99, stage100 = _manifests(
        tmp_path,
        {
            "phasewrap": (0.0, 0.0),
            "rope_like": (1.0, 1.0),
            "sinusoidal_like": (0.8, 0.8),
            "alibi_like": (0.6, 0.6),
            "no_position_control": (0.2, 0.2),
        },
    )

    result = run_stage153_simulated_noise_rehearsal(stage99_manifest_path=stage99, stage100_manifest_path=stage100)

    assert result["decision"] == "SIMULATED_NOISE_PHASEWRAP_STRICT_ADVANTAGE_OBSERVED"
    assert result["simulated_only"] is True
    assert result["no_hardware_submission"] is True
    assert result["phasewrap_positional_advantage_group_count"] > 0
    assert result["phasewrap_strict_advantage_group_count"] > 0


def test_stage153_reports_no_advantage_when_control_is_best(tmp_path) -> None:
    stage99, stage100 = _manifests(
        tmp_path,
        {
            "phasewrap": (1.0, 1.0),
            "rope_like": (0.8, 0.8),
            "sinusoidal_like": (0.6, 0.6),
            "alibi_like": (0.4, 0.4),
            "no_position_control": (0.0, 0.0),
        },
    )

    result = run_stage153_simulated_noise_rehearsal(stage99_manifest_path=stage99, stage100_manifest_path=stage100)

    assert result["decision"] == "SIMULATED_NOISE_PHASEWRAP_ADVANTAGE_NOT_OBSERVED"
    assert result["phasewrap_strict_advantage_group_count"] == 0


def test_stage153_outputs_are_written(tmp_path) -> None:
    stage99, stage100 = _manifests(
        tmp_path,
        {
            "phasewrap": (0.0, 0.0),
            "rope_like": (1.0, 1.0),
            "sinusoidal_like": (0.8, 0.8),
            "alibi_like": (0.6, 0.6),
            "no_position_control": (0.2, 0.2),
        },
    )
    result = run_stage153_simulated_noise_rehearsal(stage99_manifest_path=stage99, stage100_manifest_path=stage100)

    paths = write_stage153_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert manifest["simulated_only"] is True
    assert "phasewrap_beats_positional_comparators" in summary
