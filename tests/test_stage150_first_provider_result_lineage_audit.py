from __future__ import annotations

import json

from qrope.stage150_first_provider_result_lineage_audit import run_stage150_audit, write_stage150_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _write_jsonl(path, records) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(record, sort_keys=True) + "\n" for record in records), encoding="utf-8")


def _paths(tmp_path) -> dict[str, object]:
    return {
        "stage112_job_manifest_path": tmp_path / "stage112" / "job_manifest.jsonl",
        "stage114_manifest_path": tmp_path / "stage114" / "manifest.json",
        "stage145_results_path": tmp_path / "stage145" / "results.json",
        "stage148_results_path": tmp_path / "stage148" / "results.json",
        "stage149_results_path": tmp_path / "stage149" / "results.json",
    }


def _calibration_job(job_id="ibm_runtime__independent_window_00__calibration__state_00"):
    return {
        "job_id": job_id,
        "job_kind": "known_state_calibration",
        "openqasm3": "OPENQASM 3.0;\nqubit[2] q;\n",
        "provider": "ibm_runtime",
        "shots": 1000,
        "state": "00",
        "target_counts_container": "raw_counts_by_state",
        "target_counts_key": "00",
        "target_evidence_path": (
            "logs/automated_stage_gates/stage107_window_execution_orchestrator/windows/"
            "ibm_runtime__independent_window_00/calibration/ibm_runtime_known_state_execution.json"
        ),
        "template_path": "logs/automated_stage_gates/stage102_calibration_execution_package/execution_templates/ibm_runtime_known_state_execution.json",
        "window_id": "ibm_runtime__independent_window_00",
    }


def _packet_job(job_id="ibm_runtime__independent_window_00__packet__packet0__phasewrap__hwrow-000"):
    return {
        "circuit_template": "two_ry_product_state_z_readout_v1",
        "encoding_family": "phasewrap",
        "job_id": job_id,
        "job_kind": "matched_packet_row",
        "openqasm3": "OPENQASM 3.0;\nqubit[2] q;\n",
        "packet_id": "packet0__phasewrap",
        "provider": "ibm_runtime",
        "row_id": "hwrow-000",
        "shots": 4096,
        "source_lane_id": "ibm_product_seed314_rows16_shots4096",
        "target_counts_container": "raw_counts_by_row",
        "target_counts_key": "hwrow-000",
        "target_evidence_path": (
            "logs/automated_stage_gates/stage107_window_execution_orchestrator/windows/"
            "ibm_runtime__independent_window_00/packet_executions/packet0__phasewrap.json"
        ),
        "template_path": "logs/automated_stage_gates/stage104_matched_packet_execution_package/packet_execution_templates/packet0__phasewrap.json",
        "window_id": "ibm_runtime__independent_window_00",
    }


def _fixture(tmp_path, paths, jobs=None) -> None:
    jobs = jobs or [_calibration_job(), _packet_job()]
    shard_path = tmp_path / "stage114" / "job_shards" / "ibm_runtime" / "ibm_runtime__independent_window_00" / "jobs.jsonl"
    _write_jsonl(paths["stage112_job_manifest_path"], jobs)
    _write_jsonl(shard_path, jobs)
    _write_json(
        paths["stage114_manifest_path"],
        {
            "job_shard_paths": [str(shard_path)],
            "required_result_fields": [
                "job_id",
                "job_or_task_id",
                "backend_metadata",
                "submitted_at_utc",
                "completed_at_utc",
                "counts",
            ],
        },
    )
    _write_json(paths["stage145_results_path"], {"first_unlock_provider": "ibm_runtime"})
    _write_json(
        paths["stage148_results_path"],
        {
            "provider_scope": "ibm_runtime",
            "calibration_records": [{"provider": "ibm_runtime", "window_id": "ibm_runtime__independent_window_00"}],
            "lane_records": [{"provider": "ibm_runtime", "window_id": "ibm_runtime__independent_window_00"}],
        },
    )
    _write_json(
        paths["stage149_results_path"],
        {
            "first_unlock_provider": "ibm_runtime",
            "decision": "FIRST_PROVIDER_GUARDED_RUNNER_CONTRACT_READY_CUTOVER_BLOCKED",
            "synthetic_contract_check_count": 3,
            "synthetic_contract_ready_count": 3,
        },
    )


def test_stage150_readies_first_provider_result_lineage_contract(tmp_path) -> None:
    paths = _paths(tmp_path)
    _fixture(tmp_path, paths)

    result = run_stage150_audit(**paths)

    assert result["decision"] == "FIRST_PROVIDER_RESULT_LINEAGE_CONTRACT_READY_EXECUTION_BLOCKED"
    assert result["job_count"] == 2
    assert result["calibration_job_count"] == 1
    assert result["packet_job_count"] == 1
    assert result["stage114_shard_assignment_count"] == 2
    assert result["required_backend_metadata_fields"] == ["provider", "backend", "window_id", "job_kind"]
    assert result["no_hardware_submission"] is True


def test_stage150_fails_closed_on_duplicate_or_incomplete_packet_lineage(tmp_path) -> None:
    paths = _paths(tmp_path)
    duplicate_id = "duplicate_job"
    bad_packet = _packet_job(duplicate_id)
    bad_packet.pop("row_id")
    jobs = [_calibration_job(duplicate_id), bad_packet]
    _fixture(tmp_path, paths, jobs=jobs)

    result = run_stage150_audit(**paths)
    missing = {item for record in result["job_records"] for item in record["missing_evidence"]}

    assert result["decision"] == "FIRST_PROVIDER_RESULT_LINEAGE_CONTRACT_INCOMPLETE"
    assert "job_id_unique" in missing
    assert "row_id" in missing


def test_stage150_outputs_are_written(tmp_path) -> None:
    paths = _paths(tmp_path)
    _fixture(tmp_path, paths)
    result = run_stage150_audit(**paths)

    written = write_stage150_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(written) == {"manifest", "result", "summary_csv"}
    assert manifest["decision"] == "FIRST_PROVIDER_RESULT_LINEAGE_CONTRACT_READY_EXECUTION_BLOCKED"
    assert "ibm_runtime__independent_window_00" in summary
