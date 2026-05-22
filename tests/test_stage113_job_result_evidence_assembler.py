from __future__ import annotations

import json

from qrope.stage113_job_result_evidence_assembler import run_stage113_assembler, write_stage113_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _write_jsonl(path, records) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(record, sort_keys=True) for record in records) + "\n", encoding="utf-8")


def _fixture(tmp_path):
    calibration_template = tmp_path / "templates" / "calibration.json"
    packet_template = tmp_path / "templates" / "packet.json"
    calibration_target = tmp_path / "evidence" / "calibration.json"
    packet_target = tmp_path / "evidence" / "packet.json"
    _write_json(
        calibration_template,
        {
            "provider": "ibm_runtime",
            "job_or_task_ids": [],
            "backend_metadata": {"provider": "ibm_runtime", "backend": ""},
            "submitted_at_utc": "",
            "completed_at_utc": "",
            "raw_counts_by_state": [{"state": "00", "counts": {}, "openqasm3": "OPENQASM 3.0;"}],
        },
    )
    _write_json(
        packet_template,
        {
            "provider": "ibm_runtime",
            "packet_id": "packet_a",
            "job_or_task_ids": [],
            "backend_metadata": {"provider": "ibm_runtime", "backend": ""},
            "submitted_at_utc": "",
            "completed_at_utc": "",
            "raw_counts_by_row": [{"row_id": "row0", "counts": {}, "openqasm3": "OPENQASM 3.0;"}],
        },
    )
    jobs = [
        {
            "job_id": "job_cal",
            "job_kind": "known_state_calibration",
            "provider": "ibm_runtime",
            "window_id": "window0",
            "target_evidence_path": str(calibration_target.as_posix()),
            "target_counts_container": "raw_counts_by_state",
            "target_counts_key": "00",
            "template_path": str(calibration_template.as_posix()),
        },
        {
            "job_id": "job_packet",
            "job_kind": "matched_packet_row",
            "provider": "ibm_runtime",
            "window_id": "window0",
            "target_evidence_path": str(packet_target.as_posix()),
            "target_counts_container": "raw_counts_by_row",
            "target_counts_key": "row0",
            "template_path": str(packet_template.as_posix()),
        },
    ]
    results = [
        {
            "job_id": "job_cal",
            "job_or_task_id": "task-cal",
            "backend_metadata": {"provider": "ibm_runtime", "backend": "backend_a"},
            "submitted_at_utc": "2026-05-21T00:00:00Z",
            "completed_at_utc": "2026-05-21T00:01:00Z",
            "counts": {"00": 100},
        },
        {
            "job_id": "job_packet",
            "job_or_task_id": "task-packet",
            "backend_metadata": {"provider": "ibm_runtime", "backend": "backend_a"},
            "submitted_at_utc": "2026-05-21T00:02:00Z",
            "completed_at_utc": "2026-05-21T00:03:00Z",
            "counts": {"11": 90, "10": 10},
        },
    ]
    return jobs, results, calibration_target, packet_target


def _stage115_collected(path, provider_results_path, *, provider_scope: str = "all") -> None:
    _write_json(
        path,
        {
            "decision": "PROVIDER_RESULTS_COLLECTED_FOR_STAGE113",
            "wrote_stage113_input": True,
            "stage113_provider_results_path": str(provider_results_path.as_posix()),
            "provider_scope": provider_scope,
            "stage152_write_ready": True,
            "stage152_write_blockers": [],
            "stage152_first_provider_runner_command_count": 1,
            "stage152_first_provider_authorized_runner_count": 1,
            "stage152_first_provider_live_submit_ready_count": 1,
            "stage152_all_first_provider_commands_authorized": True,
            "stage152_all_first_provider_commands_live_submit_ready": True,
            "shard_count": 1,
            "ready_shard_count": 1,
            "expected_job_count": 2,
            "result_record_count": 2,
            "missing_job_count": 0,
            "invalid_result_record_count": 0,
        },
    )


def _stage115_blocked(path, provider_results_path) -> None:
    _write_json(
        path,
        {
            "decision": "PROVIDER_RESULTS_COLLECTION_BLOCKED_LIVE_GUARD_REQUIRED",
            "wrote_stage113_input": False,
            "stage113_provider_results_path": str(provider_results_path.as_posix()),
            "provider_scope": "all",
            "stage152_write_ready": False,
            "stage152_write_blockers": ["stage152_live_execution_guard_not_ready"],
            "stage152_first_provider_runner_command_count": 1,
            "stage152_first_provider_authorized_runner_count": 0,
            "stage152_first_provider_live_submit_ready_count": 0,
            "stage152_all_first_provider_commands_authorized": False,
            "stage152_all_first_provider_commands_live_submit_ready": False,
            "shard_count": 1,
            "ready_shard_count": 0,
            "expected_job_count": 2,
            "result_record_count": 0,
            "missing_job_count": 2,
            "invalid_result_record_count": 0,
        },
    )


def test_stage113_reports_missing_sources(tmp_path) -> None:
    result = run_stage113_assembler(stage112_job_manifest_path=tmp_path / "missing_jobs.jsonl", provider_results_path=tmp_path / "missing_results.jsonl")

    assert result["status"] == "incomplete"
    assert result["decision"] == "JOB_RESULT_EVIDENCE_ASSEMBLY_BLOCKED_RESULTS_MISSING"
    assert len(result["missing_source_artifacts"]) == 2


def test_stage113_blocks_when_results_are_missing(tmp_path) -> None:
    jobs, _, _, _ = _fixture(tmp_path)
    _write_jsonl(tmp_path / "jobs.jsonl", jobs)

    result = run_stage113_assembler(stage112_job_manifest_path=tmp_path / "jobs.jsonl", provider_results_path=tmp_path / "missing_results.jsonl")

    assert result["job_count"] == 2
    assert result["provider_result_count"] == 0
    assert result["missing_job_result_count"] == 2


def test_stage113_detects_complete_results_without_writing_by_default(tmp_path) -> None:
    jobs, results, calibration_target, _ = _fixture(tmp_path)
    _write_jsonl(tmp_path / "jobs.jsonl", jobs)
    _write_jsonl(tmp_path / "results.jsonl", results)
    _stage115_collected(tmp_path / "stage115.json", tmp_path / "results.jsonl", provider_scope="ibm_runtime")

    result = run_stage113_assembler(
        stage112_job_manifest_path=tmp_path / "jobs.jsonl",
        provider_results_path=tmp_path / "results.jsonl",
        stage115_results_path=tmp_path / "stage115.json",
    )

    assert result["decision"] == "JOB_RESULTS_READY_FOR_STAGE109_EVIDENCE_ASSEMBLY"
    assert result["ready_job_result_count"] == 2
    assert result["assembled_evidence_count"] == 0
    assert not calibration_target.exists()


def test_stage113_blocks_duplicate_result_records(tmp_path) -> None:
    jobs, results, calibration_target, _ = _fixture(tmp_path)
    _write_jsonl(tmp_path / "jobs.jsonl", jobs)
    _write_jsonl(tmp_path / "results.jsonl", results + [results[0]])
    _stage115_collected(tmp_path / "stage115.json", tmp_path / "results.jsonl", provider_scope="ibm_runtime")

    result = run_stage113_assembler(
        stage112_job_manifest_path=tmp_path / "jobs.jsonl",
        provider_results_path=tmp_path / "results.jsonl",
        stage115_results_path=tmp_path / "stage115.json",
        write_evidence=True,
    )

    assert result["decision"] == "JOB_RESULT_EVIDENCE_ASSEMBLY_BLOCKED_RESULTS_MISSING"
    assert result["duplicate_result_record_count"] == 1
    assert result["assembled_evidence_count"] == 0
    assert not calibration_target.exists()


def test_stage113_blocks_unknown_result_records(tmp_path) -> None:
    jobs, results, calibration_target, _ = _fixture(tmp_path)
    unknown = dict(results[0])
    unknown["job_id"] = "unknown_job"
    _write_jsonl(tmp_path / "jobs.jsonl", jobs)
    _write_jsonl(tmp_path / "results.jsonl", results + [unknown])
    _stage115_collected(tmp_path / "stage115.json", tmp_path / "results.jsonl", provider_scope="ibm_runtime")

    result = run_stage113_assembler(
        stage112_job_manifest_path=tmp_path / "jobs.jsonl",
        provider_results_path=tmp_path / "results.jsonl",
        stage115_results_path=tmp_path / "stage115.json",
        write_evidence=True,
    )

    assert result["decision"] == "JOB_RESULT_EVIDENCE_ASSEMBLY_BLOCKED_RESULTS_MISSING"
    assert result["unknown_result_record_count"] == 1
    assert result["assembled_evidence_count"] == 0
    assert not calibration_target.exists()


def test_stage113_writes_evidence_when_explicitly_enabled(tmp_path) -> None:
    jobs, results, calibration_target, packet_target = _fixture(tmp_path)
    _write_jsonl(tmp_path / "jobs.jsonl", jobs)
    _write_jsonl(tmp_path / "results.jsonl", results)
    _stage115_collected(tmp_path / "stage115.json", tmp_path / "results.jsonl")

    result = run_stage113_assembler(
        stage112_job_manifest_path=tmp_path / "jobs.jsonl",
        provider_results_path=tmp_path / "results.jsonl",
        stage115_results_path=tmp_path / "stage115.json",
        write_evidence=True,
    )

    calibration = json.loads(calibration_target.read_text(encoding="utf-8"))
    packet = json.loads(packet_target.read_text(encoding="utf-8"))
    assert result["decision"] == "JOB_RESULTS_ASSEMBLED_INTO_STAGE109_EVIDENCE"
    assert result["assembled_evidence_count"] == 2
    assert calibration["raw_counts_by_state"][0]["counts"] == {"00": 100}
    assert packet["raw_counts_by_row"][0]["counts"] == {"10": 10, "11": 90}
    assert packet["no_hardware_submission"] is False
    assert packet["stage113_live_submit_provenance"]["ready"] is True
    assert packet["stage113_live_submit_provenance"]["stage152_all_first_provider_commands_authorized"] is True
    assert packet["stage113_live_submit_provenance"]["stage152_all_first_provider_commands_live_submit_ready"] is True


def test_stage113_blocks_evidence_write_without_stage115_collection(tmp_path) -> None:
    jobs, results, calibration_target, packet_target = _fixture(tmp_path)
    _write_jsonl(tmp_path / "jobs.jsonl", jobs)
    _write_jsonl(tmp_path / "results.jsonl", results)
    _stage115_blocked(tmp_path / "stage115.json", tmp_path / "results.jsonl")

    result = run_stage113_assembler(
        stage112_job_manifest_path=tmp_path / "jobs.jsonl",
        provider_results_path=tmp_path / "results.jsonl",
        stage115_results_path=tmp_path / "stage115.json",
        write_evidence=True,
    )

    assert result["decision"] == "JOB_RESULT_EVIDENCE_ASSEMBLY_BLOCKED_STAGE115_COLLECTION_REQUIRED"
    assert "stage115_not_collected_for_stage113" in result["stage115_write_blockers"]
    assert not calibration_target.exists()
    assert not packet_target.exists()


def test_stage113_blocks_evidence_write_when_stage115_counters_are_incomplete(tmp_path) -> None:
    jobs, results, calibration_target, packet_target = _fixture(tmp_path)
    _write_jsonl(tmp_path / "jobs.jsonl", jobs)
    _write_jsonl(tmp_path / "results.jsonl", results)
    _write_json(
        tmp_path / "stage115.json",
        {
            "decision": "PROVIDER_RESULTS_COLLECTED_FOR_STAGE113",
            "wrote_stage113_input": True,
            "stage113_provider_results_path": str((tmp_path / "results.jsonl").as_posix()),
            "provider_scope": "all",
            "stage152_write_ready": False,
            "stage152_write_blockers": ["stage152_stage144_not_ready"],
            "stage152_first_provider_runner_command_count": 2,
            "stage152_first_provider_authorized_runner_count": 1,
            "stage152_first_provider_live_submit_ready_count": 1,
            "stage152_all_first_provider_commands_authorized": False,
            "stage152_all_first_provider_commands_live_submit_ready": False,
            "shard_count": 1,
            "ready_shard_count": 0,
            "expected_job_count": 2,
            "result_record_count": 1,
            "missing_job_count": 1,
            "invalid_result_record_count": 0,
        },
    )

    result = run_stage113_assembler(
        stage112_job_manifest_path=tmp_path / "jobs.jsonl",
        provider_results_path=tmp_path / "results.jsonl",
        stage115_results_path=tmp_path / "stage115.json",
        write_evidence=True,
    )

    assert result["decision"] == "JOB_RESULT_EVIDENCE_ASSEMBLY_BLOCKED_STAGE115_COLLECTION_REQUIRED"
    assert "stage115_stage152_write_not_ready" in result["stage115_write_blockers"]
    assert "stage115_stage152_commands_not_all_authorized" in result["stage115_write_blockers"]
    assert "stage115_stage152_commands_not_all_live_submit_ready" in result["stage115_write_blockers"]
    assert "stage115_stage152_authorized_runner_count_incomplete" in result["stage115_write_blockers"]
    assert "stage115_stage152_live_submit_ready_count_incomplete" in result["stage115_write_blockers"]
    assert "stage115_shards_not_all_ready" in result["stage115_write_blockers"]
    assert "stage115_result_count_mismatch" in result["stage115_write_blockers"]
    assert not calibration_target.exists()
    assert not packet_target.exists()


def test_stage113_can_assemble_provider_scoped_results(tmp_path) -> None:
    jobs, results, calibration_target, _ = _fixture(tmp_path)
    braket_target = tmp_path / "evidence" / "braket.json"
    braket_template = tmp_path / "templates" / "braket.json"
    _write_json(
        braket_template,
        {
            "provider": "amazon_braket",
            "raw_counts_by_state": [{"state": "00", "counts": {}}],
        },
    )
    jobs.append(
        {
            "job_id": "braket_job",
            "job_kind": "known_state_calibration",
            "provider": "amazon_braket",
            "window_id": "window0",
            "target_evidence_path": str(braket_target.as_posix()),
            "target_counts_container": "raw_counts_by_state",
            "target_counts_key": "00",
            "template_path": str(braket_template.as_posix()),
        }
    )
    _write_jsonl(tmp_path / "jobs.jsonl", jobs)
    _write_jsonl(tmp_path / "results.jsonl", results)
    _stage115_collected(tmp_path / "stage115.json", tmp_path / "results.jsonl", provider_scope="ibm_runtime")

    result = run_stage113_assembler(
        stage112_job_manifest_path=tmp_path / "jobs.jsonl",
        provider_results_path=tmp_path / "results.jsonl",
        stage115_results_path=tmp_path / "stage115.json",
        write_evidence=True,
        provider="ibm_runtime",
    )

    assert result["provider_scope"] == "ibm_runtime"
    assert result["available_job_count"] == 3
    assert result["job_count"] == 2
    assert result["decision"] == "JOB_RESULTS_ASSEMBLED_INTO_STAGE109_EVIDENCE"
    assert calibration_target.exists()
    assert not braket_target.exists()


def test_stage113_blocks_provider_scoped_write_with_unscoped_stage115_collection(tmp_path) -> None:
    jobs, results, calibration_target, _ = _fixture(tmp_path)
    _write_jsonl(tmp_path / "jobs.jsonl", jobs)
    _write_jsonl(tmp_path / "results.jsonl", results)
    _stage115_collected(tmp_path / "stage115.json", tmp_path / "results.jsonl", provider_scope="all")

    result = run_stage113_assembler(
        stage112_job_manifest_path=tmp_path / "jobs.jsonl",
        provider_results_path=tmp_path / "results.jsonl",
        stage115_results_path=tmp_path / "stage115.json",
        write_evidence=True,
        provider="ibm_runtime",
    )

    assert result["decision"] == "JOB_RESULT_EVIDENCE_ASSEMBLY_BLOCKED_STAGE115_COLLECTION_REQUIRED"
    assert "stage115_provider_scope_mismatch" in result["stage115_write_blockers"]
    assert not calibration_target.exists()


def test_stage113_outputs_are_written(tmp_path) -> None:
    jobs, _, _, _ = _fixture(tmp_path)
    _write_jsonl(tmp_path / "jobs.jsonl", jobs)
    result = run_stage113_assembler(stage112_job_manifest_path=tmp_path / "jobs.jsonl", provider_results_path=tmp_path / "missing_results.jsonl")

    paths = write_stage113_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert manifest["job_count"] == 2
    assert "job_cal" in summary
