from __future__ import annotations

import json

from qrope.stage174_locked_interpretation_surface_audit import run_stage174_locked_interpretation_surface_audit, write_stage174_outputs


FAMILIES = ["phasewrap", "rope_like", "sinusoidal_like", "alibi_like", "no_position_control"]


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _write_jsonl(path, records) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(record, sort_keys=True) + "\n" for record in records), encoding="utf-8")


def _sources(tmp_path, *, omit_family: str | None = None):
    lane = "ibm_product_seed314_rows16_shots4096"
    templates = []
    jobs = []
    row_ids = ["hwrow-000", "hwrow-001"]
    for family in FAMILIES:
        packet_id = f"{lane}__{family}"
        templates.append(
            {
                "packet_id": packet_id,
                "provider": "ibm_runtime",
                "source_lane_id": lane,
                "circuit_template": "two_ry_product_state_z_readout_v1",
                "encoding_family": family,
                "raw_counts_by_row": [{"row_id": row_id, "counts": {}} for row_id in row_ids],
            }
        )
        if family == omit_family:
            continue
        for row_id in row_ids:
            jobs.append(
                {
                    "job_id": f"{packet_id}__{row_id}",
                    "job_kind": "matched_packet_row",
                    "provider": "ibm_runtime",
                    "window_id": "ibm_runtime__independent_window_00",
                    "source_lane_id": lane,
                    "circuit_template": "two_ry_product_state_z_readout_v1",
                    "encoding_family": family,
                    "packet_id": packet_id,
                    "row_id": row_id,
                    "shots": 4096,
                }
            )
    for state in ("00", "01", "10", "11"):
        jobs.append(
            {
                "job_id": f"cal_{state}",
                "job_kind": "known_state_calibration",
                "provider": "ibm_runtime",
                "window_id": "ibm_runtime__independent_window_00",
                "state": state,
                "shots": 1000,
            }
        )
    shard = tmp_path / "jobs.jsonl"
    _write_jsonl(shard, jobs)
    stage104 = tmp_path / "stage104.json"
    stage163 = tmp_path / "stage163.json"
    stage169 = tmp_path / "stage169.json"
    stage173 = tmp_path / "stage173.json"
    _write_json(
        stage104,
        {
            "decision": "MATCHED_PACKET_EXECUTION_TEMPLATES_PREPARED_CALIBRATION_AND_COUNTS_REQUIRED",
            "required_encoding_families": FAMILIES,
            "templates": templates,
            "matched_group_records": [
                {
                    "provider": "ibm_runtime",
                    "source_lane_id": lane,
                    "circuit_template": "two_ry_product_state_z_readout_v1",
                    "ready": True,
                }
            ],
        },
    )
    _write_json(
        stage163,
        {
            "decision": "FIRST_PROVIDER_PRERUN_LOCK_READY_AWAITING_APPROVAL",
            "window_locks": [{"job_shard_path": shard.as_posix()}],
        },
    )
    _write_json(
        stage169,
        {
            "decision": "TARGETED_IBM_PROBE_SCOPE_LOCKED_TO_STABLE_LANES",
            "stable_target_lanes": [lane],
        },
    )
    _write_json(stage173, {"decision": "LOCKED_RESULT_INGESTION_CONTRACT_READY_AWAITING_PROVIDER_RESULTS"})
    return stage104, stage163, stage169, stage173


def test_stage174_maps_locked_jobs_to_stage104_surface(tmp_path) -> None:
    stage104, stage163, stage169, stage173 = _sources(tmp_path)

    result = run_stage174_locked_interpretation_surface_audit(
        stage104_results_path=stage104,
        stage163_results_path=stage163,
        stage169_results_path=stage169,
        stage173_results_path=stage173,
    )

    assert result["decision"] == "LOCKED_INTERPRETATION_SURFACE_READY_AWAITING_PROVIDER_RESULTS"
    assert result["ready_group_count"] == 1
    assert result["matched_packet_job_count"] == 10
    assert result["calibration_count_by_window"] == {"ibm_runtime__independent_window_00": 4}
    assert result["blockers"] == []


def test_stage174_blocks_missing_comparator_family(tmp_path) -> None:
    stage104, stage163, stage169, stage173 = _sources(tmp_path, omit_family="rope_like")

    result = run_stage174_locked_interpretation_surface_audit(
        stage104_results_path=stage104,
        stage163_results_path=stage163,
        stage169_results_path=stage169,
        stage173_results_path=stage173,
    )

    assert result["decision"] == "LOCKED_INTERPRETATION_SURFACE_AUDIT_BLOCKED"
    assert "locked_interpretation_groups_not_ready" in result["blockers"]
    assert "missing_encoding_families" in result["group_records"][0]["blockers"]


def test_stage174_outputs_do_not_record_secrets_or_live_submit(tmp_path) -> None:
    stage104, stage163, stage169, stage173 = _sources(tmp_path)
    result = run_stage174_locked_interpretation_surface_audit(
        stage104_results_path=stage104,
        stage163_results_path=stage163,
        stage169_results_path=stage169,
        stage173_results_path=stage173,
    )

    paths = write_stage174_outputs(result, tmp_path / "out")
    written = (tmp_path / "out" / "results.json").read_text(encoding="utf-8")
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert "--allow-live-submit" not in written
    assert "--allow-live-submit" not in summary
    assert "IBM_QUANTUM_TOKEN" not in written
    assert "crn:v1" not in written
