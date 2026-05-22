from __future__ import annotations

import json

from qrope.stage160_first_provider_post_run_analysis_packet import (
    run_stage160_post_run_analysis_packet,
    write_stage160_outputs,
)


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _sources(tmp_path, *, result_count=0, missing_count=328):
    stage159 = tmp_path / "stage159.json"
    stage164 = tmp_path / "stage164.json"
    stage115 = tmp_path / "stage115.json"
    stage113 = tmp_path / "stage113.json"
    stage135 = tmp_path / "stage135.json"
    _write_json(
        stage159,
        {
            "decision": "FIRST_PROVIDER_BACKEND_PREFLIGHT_READY_AWAITING_APPROVAL",
            "first_unlock_provider": "ibm_runtime",
            "approval_phrase_required": "APPROVE IBM RUNTIME STAGE133 LIVE RUN",
            "backend_lookup_ready": True,
        },
    )
    _write_json(
        stage164,
        {
            "decision": (
                "FIRST_PROVIDER_RESULT_LOCK_VERIFIED_READY_FOR_STAGE115"
                if missing_count == 0
                else "FIRST_PROVIDER_RESULT_LOCK_VERIFICATION_BLOCKED_RESULTS_MISSING"
            ),
            "hash_match_count": 2,
            "window_count": 2,
            "expected_result_record_count": 328,
            "provider_result_record_count": result_count,
            "missing_result_record_count": missing_count,
        },
    )
    _write_json(
        stage115,
        {
            "decision": "PROVIDER_RESULTS_COLLECTION_BLOCKED_RESULTS_MISSING",
            "provider_scope": "ibm_runtime",
            "expected_job_count": 328,
            "result_record_count": result_count,
            "missing_job_count": missing_count,
        },
    )
    _write_json(
        stage113,
        {
            "decision": "JOB_RESULT_EVIDENCE_ASSEMBLY_BLOCKED_RESULTS_MISSING",
            "provider_scope": "ibm_runtime",
        },
    )
    _write_json(stage135, {"decision": "POST_COLLECTION_CLAIM_GATE_SEQUENCE_PREPARED_EXECUTION_BLOCKED"})
    return stage159, stage164, stage115, stage113, stage135


def test_stage160_packet_ready_awaiting_provider_results(tmp_path) -> None:
    stage159, stage164, stage115, stage113, stage135 = _sources(tmp_path)

    result = run_stage160_post_run_analysis_packet(
        stage159_results_path=stage159,
        stage164_results_path=stage164,
        stage115_results_path=stage115,
        stage113_results_path=stage113,
        stage135_results_path=stage135,
    )

    assert result["decision"] == "FIRST_PROVIDER_POST_RUN_ANALYSIS_PACKET_READY_AWAITING_PROVIDER_RESULTS"
    assert result["no_hardware_submission"] is True
    assert result["runnable_hardware_commands_recorded"] is False
    assert result["command_count"] == 12
    assert result["command_records"][0]["stage_id"] == "stage164"
    assert result["blockers"] == ["provider_result_records_missing", "stage164_provider_result_records_missing"]


def test_stage160_sequence_ready_when_provider_results_are_complete(tmp_path) -> None:
    stage159, stage164, stage115, stage113, stage135 = _sources(tmp_path, result_count=328, missing_count=0)

    result = run_stage160_post_run_analysis_packet(
        stage159_results_path=stage159,
        stage164_results_path=stage164,
        stage115_results_path=stage115,
        stage113_results_path=stage113,
        stage135_results_path=stage135,
    )

    assert result["decision"] == "FIRST_PROVIDER_POST_RUN_ANALYSIS_SEQUENCE_READY"
    assert result["blockers"] == []


def test_stage160_blocks_if_stage159_is_not_ready(tmp_path) -> None:
    stage159, stage164, stage115, stage113, stage135 = _sources(tmp_path)
    _write_json(stage159, {"decision": "FIRST_PROVIDER_BACKEND_PREFLIGHT_BLOCKED", "first_unlock_provider": "ibm_runtime"})

    result = run_stage160_post_run_analysis_packet(
        stage159_results_path=stage159,
        stage164_results_path=stage164,
        stage115_results_path=stage115,
        stage113_results_path=stage113,
        stage135_results_path=stage135,
    )

    assert result["decision"] == "FIRST_PROVIDER_POST_RUN_ANALYSIS_PACKET_BLOCKED"
    assert "stage159_backend_preflight_not_ready" in result["blockers"]


def test_stage160_outputs_do_not_record_live_submit_or_secrets(tmp_path) -> None:
    stage159, stage164, stage115, stage113, stage135 = _sources(tmp_path)
    result = run_stage160_post_run_analysis_packet(
        stage159_results_path=stage159,
        stage164_results_path=stage164,
        stage115_results_path=stage115,
        stage113_results_path=stage113,
        stage135_results_path=stage135,
    )

    paths = write_stage160_outputs(result, tmp_path / "out")
    written = (tmp_path / "out" / "results.json").read_text(encoding="utf-8")
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert "--allow-live-submit" not in written
    assert "--allow-live-submit" not in summary
    assert "crn:v1" not in written
    assert "IBM_QUANTUM_TOKEN" not in written
