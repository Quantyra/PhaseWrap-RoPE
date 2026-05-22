from __future__ import annotations

import json

from qrope.stage169_targeted_probe_scope_selection import run_stage169_scope_selection, write_stage169_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _write_jsonl(path, records) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(record, sort_keys=True) + "\n" for record in records), encoding="utf-8")


def test_stage169_selects_only_stable_locked_lanes(tmp_path) -> None:
    shard = tmp_path / "jobs.jsonl"
    _write_jsonl(
        shard,
        [
            {
                "job_kind": "matched_packet_row",
                "provider": "ibm_runtime",
                "source_lane_id": "ibm_product_seed314_rows16_shots4096",
                "circuit_template": "two_ry_product_state_z_readout_v1",
                "encoding_family": "phasewrap",
                "shots": 4096,
            },
            {
                "job_kind": "matched_packet_row",
                "provider": "ibm_runtime",
                "source_lane_id": "ibm_cx_seed314_rows16_shots4096",
                "circuit_template": "two_ry_cx_parity_z_readout_v1",
                "encoding_family": "phasewrap",
                "shots": 4096,
            },
        ],
    )
    stage165 = tmp_path / "stage165.json"
    stage163 = tmp_path / "stage163.json"
    _write_json(
        stage165,
        {
            "decision": "SIMULATED_NOISE_STABLE_TARGETED_HARDWARE_PROBE_RECOMMENDED",
            "target_records": [
                {"provider": "ibm_runtime", "source_lane_id": "ibm_product_seed314_rows16_shots4096", "stable_target": True},
                {"provider": "ibm_runtime", "source_lane_id": "ibm_cx_seed314_rows16_shots4096", "stable_target": True},
                {"provider": "ibm_runtime", "source_lane_id": "ibm_product_seed577_rows16_shots4096", "stable_target": False},
            ],
        },
    )
    _write_json(
        stage163,
        {
            "decision": "FIRST_PROVIDER_PRERUN_LOCK_READY_AWAITING_APPROVAL",
            "approved_job_count": 2,
            "locked_total_shots": 8192,
            "window_locks": [{"window_id": "window_0", "job_shard_path": shard.as_posix()}],
        },
    )

    result = run_stage169_scope_selection(stage165_results_path=stage165, stage163_results_path=stage163)

    assert result["decision"] == "TARGETED_IBM_PROBE_SCOPE_LOCKED_TO_STABLE_LANES"
    assert result["stable_target_lanes"] == ["ibm_cx_seed314_rows16_shots4096", "ibm_product_seed314_rows16_shots4096"]
    assert result["excluded_recommended_lanes"] == ["ibm_product_seed577_rows16_shots4096"]
    assert result["blockers"] == []


def test_stage169_blocks_when_stable_lane_is_not_locked(tmp_path) -> None:
    shard = tmp_path / "jobs.jsonl"
    _write_jsonl(shard, [])
    stage165 = tmp_path / "stage165.json"
    stage163 = tmp_path / "stage163.json"
    _write_json(
        stage165,
        {
            "decision": "SIMULATED_NOISE_STABLE_TARGETED_HARDWARE_PROBE_RECOMMENDED",
            "target_records": [{"provider": "ibm_runtime", "source_lane_id": "ibm_product_seed314_rows16_shots4096", "stable_target": True}],
        },
    )
    _write_json(
        stage163,
        {
            "decision": "FIRST_PROVIDER_PRERUN_LOCK_READY_AWAITING_APPROVAL",
            "window_locks": [{"window_id": "window_0", "job_shard_path": shard.as_posix()}],
        },
    )

    result = run_stage169_scope_selection(stage165_results_path=stage165, stage163_results_path=stage163)

    assert result["decision"] == "TARGETED_PROBE_SCOPE_SELECTION_BLOCKED"
    assert "stable_target_lanes_not_covered_by_locked_shards" in result["blockers"]


def test_stage169_outputs_are_written(tmp_path) -> None:
    shard = tmp_path / "jobs.jsonl"
    _write_jsonl(
        shard,
        [
            {
                "job_kind": "matched_packet_row",
                "provider": "ibm_runtime",
                "source_lane_id": "ibm_product_seed314_rows16_shots4096",
                "circuit_template": "two_ry_product_state_z_readout_v1",
                "encoding_family": "phasewrap",
                "shots": 4096,
            }
        ],
    )
    stage165 = tmp_path / "stage165.json"
    stage163 = tmp_path / "stage163.json"
    _write_json(
        stage165,
        {
            "decision": "SIMULATED_NOISE_STABLE_TARGETED_HARDWARE_PROBE_RECOMMENDED",
            "target_records": [{"provider": "ibm_runtime", "source_lane_id": "ibm_product_seed314_rows16_shots4096", "stable_target": True}],
        },
    )
    _write_json(
        stage163,
        {
            "decision": "FIRST_PROVIDER_PRERUN_LOCK_READY_AWAITING_APPROVAL",
            "window_locks": [{"window_id": "window_0", "job_shard_path": shard.as_posix()}],
        },
    )
    result = run_stage169_scope_selection(stage165_results_path=stage165, stage163_results_path=stage163)

    paths = write_stage169_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert manifest["stable_target_lane_count"] == 1
    assert "selected_stable_stage165_target" in summary
