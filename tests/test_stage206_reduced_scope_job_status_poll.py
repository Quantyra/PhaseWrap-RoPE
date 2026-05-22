from __future__ import annotations

import json

from qrope.stage206_reduced_scope_job_status_poll import run_stage206_reduced_scope_job_status_poll, write_stage206_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _stage205(path) -> None:
    records = [{"template_type": "reduced_scope_packet_execution_counts", "packet_id": f"p{i}", "runtime_job_id": f"job-{i}"} for i in range(20)]
    records.append({"template_type": "reduced_scope_known_state_calibration_counts", "packet_id": "", "runtime_job_id": "job-cal"})
    _write_json(
        path,
        {
            "decision": "REDUCED_SCOPE_HARDWARE_SUBMITTED_AWAITING_RESULTS",
            "submission_records": records,
        },
    )


def test_stage206_polls_pending_jobs(tmp_path) -> None:
    stage205 = tmp_path / "stage205.json"
    _stage205(stage205)

    result = run_stage206_reduced_scope_job_status_poll(
        stage205_results_path=stage205,
        fetch_status=lambda runtime_job_id: {"runtime_job_id": runtime_job_id, "status": "QUEUED"},
    )

    assert result["decision"] == "REDUCED_SCOPE_RUNTIME_JOBS_SUBMITTED_RESULTS_PENDING"
    assert result["polled_runtime_job_count"] == 21
    assert result["completed_runtime_job_count"] == 0
    assert result["no_hardware_submission"] is True


def test_stage206_marks_complete_when_all_done(tmp_path) -> None:
    stage205 = tmp_path / "stage205.json"
    _stage205(stage205)

    result = run_stage206_reduced_scope_job_status_poll(
        stage205_results_path=stage205,
        fetch_status=lambda runtime_job_id: {"runtime_job_id": runtime_job_id, "status": "DONE"},
    )

    assert result["decision"] == "REDUCED_SCOPE_RUNTIME_JOBS_COMPLETE_READY_FOR_RESULT_COLLECTION"
    assert result["completed_runtime_job_count"] == 21


def test_stage206_outputs_do_not_record_secrets_or_live_submit(tmp_path) -> None:
    stage205 = tmp_path / "stage205.json"
    _stage205(stage205)
    result = run_stage206_reduced_scope_job_status_poll(
        stage205_results_path=stage205,
        fetch_status=lambda runtime_job_id: {"runtime_job_id": runtime_job_id, "status": "QUEUED"},
    )

    paths = write_stage206_outputs(result, tmp_path / "out")
    written = (tmp_path / "out" / "results.json").read_text(encoding="utf-8")
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert "IBM_QUANTUM_TOKEN" not in written
    assert "QISKIT_IBM_TOKEN" not in written
    assert "crn:v1" not in written
    assert "--allow-live-submit" not in written
    assert "--allow-live-submit" not in summary
