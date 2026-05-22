from __future__ import annotations

import json

from qrope.stage105_independent_rerun_protocol import (
    MIN_HOURS_BETWEEN_WINDOWS,
    build_rerun_windows,
    run_stage105_protocol,
    write_stage105_outputs,
)


def _write_json(path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _template(path, packet_id: str, provider: str) -> None:
    payload = {
        "packet_id": packet_id,
        "provider": provider,
        "source_lane_id": f"{provider}_lane",
        "encoding_family": "phasewrap",
        "circuit_template": "two_ry_product_state_z_readout_v1",
        "raw_counts_by_row": [{"row_id": "row0", "counts": {}}],
        "shot_count": 100,
    }
    _write_json(path, payload)


def test_build_rerun_windows_requires_two_windows_per_provider() -> None:
    records = [
        {
            "template_path": "a.json",
            "packet_id": "a",
            "provider": "ibm_runtime",
            "source_lane_id": "lane",
            "encoding_family": "phasewrap",
            "circuit_template": "template",
            "row_count": 1,
            "shot_count": 100,
            "missing": False,
        }
    ]

    windows = build_rerun_windows(records)

    assert len(windows) == 2
    assert windows[0]["minimum_separation_from_previous_window_hours"] == 0
    assert windows[1]["minimum_separation_from_previous_window_hours"] == MIN_HOURS_BETWEEN_WINDOWS
    assert windows[1]["requires_fresh_stage101_calibration"] is True


def test_stage105_protocol_incomplete_when_template_surface_is_short(tmp_path) -> None:
    template_path = tmp_path / "packet.json"
    _template(template_path, "packet", "ibm_runtime")
    _write_json(tmp_path / "stage101.json", {"known_state_calibration_pass": False})
    _write_json(tmp_path / "stage103.json", {"decision": "ROBUSTNESS_METRICS_PREREGISTERED_HARDWARE_COUNTS_REQUIRED"})
    _write_json(tmp_path / "stage104.json", {"template_count": 1, "template_paths": [str(template_path)]})

    result = run_stage105_protocol(
        stage101_results_path=tmp_path / "stage101.json",
        stage103_manifest_path=tmp_path / "stage103.json",
        stage104_manifest_path=tmp_path / "stage104.json",
    )

    assert result["status"] == "incomplete"
    assert result["window_count"] == 2


def test_stage105_protocol_completes_with_twenty_templates_across_two_providers(tmp_path) -> None:
    paths = []
    for index in range(10):
        path = tmp_path / f"ibm_{index}.json"
        _template(path, f"ibm_{index}", "ibm_runtime")
        paths.append(str(path))
    for index in range(10):
        path = tmp_path / f"braket_{index}.json"
        _template(path, f"braket_{index}", "amazon_braket")
        paths.append(str(path))
    _write_json(tmp_path / "stage101.json", {"known_state_calibration_pass": False})
    _write_json(tmp_path / "stage103.json", {"decision": "ROBUSTNESS_METRICS_PREREGISTERED_HARDWARE_COUNTS_REQUIRED"})
    _write_json(tmp_path / "stage104.json", {"template_count": 20, "template_paths": paths})

    result = run_stage105_protocol(
        stage101_results_path=tmp_path / "stage101.json",
        stage103_manifest_path=tmp_path / "stage103.json",
        stage104_manifest_path=tmp_path / "stage104.json",
    )

    assert result["status"] == "completed"
    assert result["decision"] == "INDEPENDENT_RERUN_PROTOCOL_PREREGISTERED_EXECUTION_REQUIRED"
    assert result["provider_count"] == 2
    assert result["window_count"] == 4
    assert result["packet_template_count"] == 20


def test_stage105_outputs_are_written(tmp_path) -> None:
    paths = []
    for index in range(10):
        path = tmp_path / f"ibm_{index}.json"
        _template(path, f"ibm_{index}", "ibm_runtime")
        paths.append(str(path))
    for index in range(10):
        path = tmp_path / f"braket_{index}.json"
        _template(path, f"braket_{index}", "amazon_braket")
        paths.append(str(path))
    _write_json(tmp_path / "stage101.json", {"known_state_calibration_pass": False})
    _write_json(tmp_path / "stage103.json", {"decision": "ROBUSTNESS_METRICS_PREREGISTERED_HARDWARE_COUNTS_REQUIRED"})
    _write_json(tmp_path / "stage104.json", {"template_count": 20, "template_paths": paths})
    result = run_stage105_protocol(
        stage101_results_path=tmp_path / "stage101.json",
        stage103_manifest_path=tmp_path / "stage103.json",
        stage104_manifest_path=tmp_path / "stage104.json",
    )

    output_paths = write_stage105_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    windows = json.loads((tmp_path / "out" / "rerun_windows.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(output_paths) == {"manifest", "result", "summary_csv", "rerun_windows"}
    assert manifest["window_count"] == 4
    assert len(windows) == 4
    assert "independent_window_01" in summary
