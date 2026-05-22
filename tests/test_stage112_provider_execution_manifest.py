from __future__ import annotations

import json

from qrope.stage112_provider_execution_manifest import run_stage112_manifest, write_stage112_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _plan(tmp_path) -> list[dict[str, object]]:
    calibration_template = tmp_path / "templates" / "calibration.json"
    packet_template = tmp_path / "templates" / "packet.json"
    _write_json(calibration_template, {"shots_per_state": 100, "raw_counts_by_state": [{"state": "00", "openqasm3": "OPENQASM 3.0;"}]})
    _write_json(packet_template, {"shot_count": 200, "raw_counts_by_row": [{"row_id": "row0", "openqasm3": "OPENQASM 3.0;"}]})
    return [
        {
            "window_id": "ibm_runtime__independent_window_00",
            "provider": "ibm_runtime",
            "window_index": 0,
            "steps": [
                {
                    "step_id": "known_state_calibration_execution",
                    "template_path": str(calibration_template.as_posix()),
                    "output_path": str((tmp_path / "windows" / "w0" / "calibration" / "ibm_runtime_known_state_execution.json").as_posix()),
                },
                {
                    "step_id": "matched_packet_execution",
                    "output_dir": str((tmp_path / "windows" / "w0" / "packet_executions").as_posix()),
                    "packet_templates": [
                        {
                            "packet_id": "packet_a",
                            "template_path": str(packet_template.as_posix()),
                            "source_lane_id": "lane_a",
                            "encoding_family": "phasewrap",
                            "circuit_template": "two_ry_product_state_z_readout_v1",
                            "shot_count": 200,
                        }
                    ],
                },
            ],
        }
    ]


def test_stage112_reports_missing_sources(tmp_path) -> None:
    result = run_stage112_manifest(stage107_window_plans_path=tmp_path / "missing107.json", stage111_results_path=tmp_path / "missing111.json")

    assert result["status"] == "incomplete"
    assert result["decision"] == "PROVIDER_EXECUTION_MANIFEST_PREPARED_SUBMISSION_BLOCKED"
    assert len(result["missing_source_artifacts"]) == 2


def test_stage112_builds_jobs_and_blocks_when_stage111_provider_not_ready(tmp_path) -> None:
    _write_json(tmp_path / "plans.json", _plan(tmp_path))
    _write_json(tmp_path / "stage111.json", {"decision": "PROVIDER_SDK_BACKEND_DISCOVERY_BLOCKED", "provider_records": [{"provider": "ibm_runtime", "status": "blocked", "blockers": ["stage106_provider_preflight_not_ready"]}]})

    result = run_stage112_manifest(stage107_window_plans_path=tmp_path / "plans.json", stage111_results_path=tmp_path / "stage111.json")

    assert result["decision"] == "PROVIDER_EXECUTION_MANIFEST_PREPARED_SUBMISSION_BLOCKED"
    assert result["total_job_count"] == 2
    assert result["window_manifests"][0]["submission_ready"] is False
    assert result["window_manifests"][0]["calibration_jobs"][0]["state"] == "00"
    assert result["window_manifests"][0]["packet_jobs"][0]["packet_id"] == "packet_a"


def test_stage112_marks_ready_when_stage111_provider_ready(tmp_path) -> None:
    _write_json(tmp_path / "plans.json", _plan(tmp_path))
    _write_json(tmp_path / "stage111.json", {"decision": "PROVIDER_SDK_BACKEND_DISCOVERY_READY_NO_SUBMISSION", "provider_records": [{"provider": "ibm_runtime", "status": "ready", "blockers": []}]})

    result = run_stage112_manifest(stage107_window_plans_path=tmp_path / "plans.json", stage111_results_path=tmp_path / "stage111.json")

    assert result["decision"] == "PROVIDER_EXECUTION_MANIFEST_READY_FOR_SUBMISSION"
    assert result["submission_ready_window_count"] == 1


def test_stage112_outputs_are_written(tmp_path) -> None:
    _write_json(tmp_path / "plans.json", _plan(tmp_path))
    _write_json(tmp_path / "stage111.json", {"decision": "PROVIDER_SDK_BACKEND_DISCOVERY_BLOCKED", "provider_records": [{"provider": "ibm_runtime", "status": "blocked", "blockers": []}]})
    result = run_stage112_manifest(stage107_window_plans_path=tmp_path / "plans.json", stage111_results_path=tmp_path / "stage111.json")

    paths = write_stage112_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    job_lines = (tmp_path / "out" / "job_manifest.jsonl").read_text(encoding="utf-8").strip().splitlines()

    assert set(paths) == {"manifest", "result", "summary_csv", "job_manifest_jsonl"}
    assert manifest["total_job_count"] == 2
    assert len(job_lines) == 2
