from __future__ import annotations

import json

from qrope.stage207_reduced_scope_result_collector import run_stage207_reduced_scope_result_collector, write_stage207_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _sources(tmp_path):
    stage205 = tmp_path / "stage205.json"
    stage203 = tmp_path / "stage203.json"
    templates = [
        {
            "template_type": "reduced_scope_packet_execution_counts",
            "packet_id": f"packet-{index}",
            "raw_counts_by_row": [{"row_id": "r0", "counts": {}}, {"row_id": "r1", "counts": {}}],
        }
        for index in range(20)
    ]
    calibration = {
        "template_type": "reduced_scope_known_state_calibration_counts",
        "raw_counts_by_state": [{"state": "00", "counts": {}}, {"state": "01", "counts": {}}],
    }
    _write_json(
        stage205,
        {
            "decision": "REDUCED_SCOPE_HARDWARE_SUBMITTED_AWAITING_RESULTS",
            "submission_records": [
                *[
                    {"packet_id": f"packet-{index}", "runtime_job_id": f"job-{index}", "submitted_at_utc": "t0", "backend_metadata": {"backend": "ibm_fez"}}
                    for index in range(20)
                ],
                {"packet_id": "", "runtime_job_id": "job-cal", "submitted_at_utc": "t0", "backend_metadata": {"backend": "ibm_fez"}},
            ],
        },
    )
    _write_json(
        stage203,
        {
            "execution_templates": templates,
            "calibration_template": calibration,
        },
    )
    return stage205, stage203


def test_stage207_collects_completed_counts(tmp_path) -> None:
    stage205, stage203 = _sources(tmp_path)

    def fake_fetch(runtime_job_id):
        return {"status": "DONE", "counts_by_circuit": [{"00": 9, "11": 1}, {"01": 8, "10": 2}]}

    result = run_stage207_reduced_scope_result_collector(stage205_results_path=stage205, stage203_results_path=stage203, fetch_result=fake_fetch)

    assert result["decision"] == "REDUCED_SCOPE_RESULT_COUNTS_COLLECTED_READY_FOR_CALIBRATION"
    assert result["collected_template_count"] == 21
    assert result["collected_templates"][0]["raw_counts_by_row"][0]["counts"] == {"00": 9, "11": 1}


def test_stage207_blocks_when_jobs_pending(tmp_path) -> None:
    stage205, stage203 = _sources(tmp_path)

    result = run_stage207_reduced_scope_result_collector(
        stage205_results_path=stage205,
        stage203_results_path=stage203,
        fetch_result=lambda runtime_job_id: {"status": "QUEUED", "counts_by_circuit": []},
    )

    assert result["decision"] == "REDUCED_SCOPE_RESULT_COLLECTION_PENDING_OR_BLOCKED"
    assert "runtime_jobs_not_complete" in result["blockers"]
    assert result["collected_template_count"] == 0


def test_stage207_outputs_do_not_record_secrets_or_live_submit(tmp_path) -> None:
    stage205, stage203 = _sources(tmp_path)
    result = run_stage207_reduced_scope_result_collector(
        stage205_results_path=stage205,
        stage203_results_path=stage203,
        fetch_result=lambda runtime_job_id: {"status": "QUEUED", "counts_by_circuit": []},
    )

    paths = write_stage207_outputs(result, tmp_path / "out")
    written = (tmp_path / "out" / "results.json").read_text(encoding="utf-8")
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert "IBM_QUANTUM_TOKEN" not in written
    assert "QISKIT_IBM_TOKEN" not in written
    assert "crn:v1" not in written
    assert "--allow-live-submit" not in written
    assert "--allow-live-submit" not in summary
