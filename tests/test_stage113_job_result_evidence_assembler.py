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

    result = run_stage113_assembler(stage112_job_manifest_path=tmp_path / "jobs.jsonl", provider_results_path=tmp_path / "results.jsonl")

    assert result["decision"] == "JOB_RESULTS_READY_FOR_STAGE109_EVIDENCE_ASSEMBLY"
    assert result["ready_job_result_count"] == 2
    assert result["assembled_evidence_count"] == 0
    assert not calibration_target.exists()


def test_stage113_writes_evidence_when_explicitly_enabled(tmp_path) -> None:
    jobs, results, calibration_target, packet_target = _fixture(tmp_path)
    _write_jsonl(tmp_path / "jobs.jsonl", jobs)
    _write_jsonl(tmp_path / "results.jsonl", results)

    result = run_stage113_assembler(stage112_job_manifest_path=tmp_path / "jobs.jsonl", provider_results_path=tmp_path / "results.jsonl", write_evidence=True)

    calibration = json.loads(calibration_target.read_text(encoding="utf-8"))
    packet = json.loads(packet_target.read_text(encoding="utf-8"))
    assert result["decision"] == "JOB_RESULTS_ASSEMBLED_INTO_STAGE109_EVIDENCE"
    assert result["assembled_evidence_count"] == 2
    assert calibration["raw_counts_by_state"][0]["counts"] == {"00": 100}
    assert packet["raw_counts_by_row"][0]["counts"] == {"10": 10, "11": 90}
    assert packet["no_hardware_submission"] is False


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

    result = run_stage113_assembler(
        stage112_job_manifest_path=tmp_path / "jobs.jsonl",
        provider_results_path=tmp_path / "results.jsonl",
        write_evidence=True,
        provider="ibm_runtime",
    )

    assert result["provider_scope"] == "ibm_runtime"
    assert result["available_job_count"] == 3
    assert result["job_count"] == 2
    assert result["decision"] == "JOB_RESULTS_ASSEMBLED_INTO_STAGE109_EVIDENCE"
    assert calibration_target.exists()
    assert not braket_target.exists()


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
