from __future__ import annotations

import json

from qrope.stage145_first_provider_evidence_path_audit import run_stage145_audit, write_stage145_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _paths(tmp_path) -> dict[str, object]:
    return {
        "stage113_results_path": tmp_path / "stage113.json",
        "stage114_manifest_path": tmp_path / "stage114.json",
        "stage115_results_path": tmp_path / "stage115.json",
        "stage133_results_path": tmp_path / "stage133.json",
        "stage135_results_path": tmp_path / "stage135.json",
        "stage137_results_path": tmp_path / "stage137.json",
        "stage144_results_path": tmp_path / "stage144.json",
    }


def _fixture(paths, *, ready: bool) -> None:
    provider = "ibm_runtime"
    _write_json(
        paths["stage144_results_path"],
        {
            "decision": "POST_CONFIGURATION_RERUN_CHAIN_READY_FOR_AUTHORIZED_RUNNER"
            if ready
            else "POST_CONFIGURATION_RERUN_CHAIN_PREPARED_EXECUTION_BLOCKED",
            "first_unlock_provider": provider,
            "transition_count": 9,
            "ready_transition_count": 9 if ready else 2,
            "first_blocked_transition": None
            if ready
            else {"stage": "stage140_local_provider_configuration_readiness"},
            "first_provider_authorized_runner_count": 1 if ready else 0,
            "next_command": "python scripts/run_stage140_local_provider_configuration_readiness.py --load-dotenv",
        },
    )
    _write_json(
        paths["stage133_results_path"],
        {
            "decision": "AUTHORIZED_RUNNER_COMMANDS_READY_FOR_EXECUTION" if ready else "AUTHORIZED_RUNNER_COMMANDS_PREPARED_EXECUTION_BLOCKED",
            "command_records": [{"provider": provider, "command_authorized": ready, "job_count": 164}],
        },
    )
    _write_json(
        paths["stage115_results_path"],
        {
            "decision": "PROVIDER_RESULTS_COLLECTED_FOR_STAGE113" if ready else "PROVIDER_RESULTS_COLLECTION_BLOCKED_RESULTS_MISSING",
            "wrote_stage113_input": ready,
            "stage152_write_ready": ready,
            "stage152_write_blockers": [],
            "stage152_first_provider_runner_command_count": 1 if ready else 0,
            "stage152_first_provider_authorized_runner_count": 1 if ready else 0,
            "stage152_first_provider_live_submit_ready_count": 1 if ready else 0,
            "stage152_all_first_provider_commands_authorized": ready,
            "stage152_all_first_provider_commands_live_submit_ready": ready,
            "provider_scope": provider,
            "shard_count": 1,
            "ready_shard_count": 1 if ready else 0,
            "expected_job_count": 164,
            "result_record_count": 164 if ready else 0,
            "missing_job_count": 0 if ready else 164,
            "invalid_result_record_count": 0,
            "shard_records": [
                {
                    "provider": provider,
                    "window_id": "window_0",
                    "ready": ready,
                    "expected_job_count": 164,
                    "result_record_count": 164 if ready else 0,
                    "missing_job_count": 0 if ready else 164,
                }
            ],
        },
    )
    _write_json(
        paths["stage113_results_path"],
        {
            "decision": "JOB_RESULTS_ASSEMBLED_INTO_STAGE109_EVIDENCE"
            if ready
            else "JOB_RESULT_EVIDENCE_ASSEMBLY_BLOCKED_RESULTS_MISSING",
            "stage115_write_ready": ready,
            "stage115_write_blockers": [],
            "assembled_evidence_count": 3 if ready else 0,
        },
    )
    _write_json(paths["stage114_manifest_path"], {"required_result_fields": ["job_id", "counts"]})
    _write_json(paths["stage135_results_path"], {"decision": "POST_COLLECTION_CLAIM_GATE_SEQUENCE_PREPARED_EXECUTION_BLOCKED"})
    _write_json(
        paths["stage137_results_path"],
        {
            "decision": "AUDITABILITY_METRICS_READY_FOR_CLAIM_GATE"
            if ready
            else "AUDITABILITY_METRICS_BLOCKED_HARDWARE_COUNTS_REQUIRED"
        },
    )


def test_stage145_reports_current_first_provider_execution_blocker(tmp_path) -> None:
    paths = _paths(tmp_path)
    _fixture(paths, ready=False)

    result = run_stage145_audit(**paths)

    assert result["decision"] == "FIRST_PROVIDER_EVIDENCE_PATH_PREPARED_RESULTS_BLOCKED"
    assert result["first_unlock_provider"] == "ibm_runtime"
    assert result["first_blocked_readiness_record"]["name"] == "post_configuration_authorized_runner_chain"
    assert result["first_provider_missing_job_count"] == 164
    assert "--provider ibm_runtime" in result["provider_scoped_commands"][0]
    assert "stage144_not_ready_for_authorized_runner" in result["first_blocked_readiness_record"]["blockers"]


def test_stage145_rejects_stage144_ready_decision_with_incomplete_transition_counts(tmp_path) -> None:
    paths = _paths(tmp_path)
    _fixture(paths, ready=True)
    stage144 = json.loads(paths["stage144_results_path"].read_text(encoding="utf-8"))
    stage144["ready_transition_count"] = 8
    _write_json(paths["stage144_results_path"], stage144)

    result = run_stage145_audit(**paths)

    assert result["decision"] == "FIRST_PROVIDER_EVIDENCE_PATH_PREPARED_RESULTS_BLOCKED"
    assert result["first_blocked_readiness_record"]["name"] == "post_configuration_authorized_runner_chain"
    assert "stage144_transition_counts_incomplete" in result["first_blocked_readiness_record"]["blockers"]


def test_stage145_reports_ready_first_provider_evidence_path(tmp_path) -> None:
    paths = _paths(tmp_path)
    _fixture(paths, ready=True)

    result = run_stage145_audit(**paths)

    assert result["decision"] == "FIRST_PROVIDER_EVIDENCE_PATH_READY_FOR_CLAIM_GATES"
    assert result["first_blocked_readiness_record"] is None
    assert result["first_provider_authorized_runner_count"] == 1
    assert result["first_provider_ready_shard_count"] == 1


def test_stage145_blocks_ready_shards_without_guarded_stage113_input(tmp_path) -> None:
    paths = _paths(tmp_path)
    _fixture(paths, ready=True)
    stage115 = json.loads(paths["stage115_results_path"].read_text(encoding="utf-8"))
    stage115["decision"] = "PROVIDER_RESULTS_READY_TO_COLLECT"
    stage115["wrote_stage113_input"] = False
    stage115["stage152_write_ready"] = False
    stage115["stage152_write_blockers"] = ["stage152_live_execution_guard_not_ready"]
    _write_json(paths["stage115_results_path"], stage115)

    result = run_stage145_audit(**paths)

    assert result["decision"] == "FIRST_PROVIDER_EVIDENCE_PATH_PREPARED_RESULTS_BLOCKED"
    guarded_record = next(record for record in result["readiness_records"] if record["name"] == "first_provider_stage115_guarded_stage113_input")
    assert guarded_record["ready"] is False
    assert "stage115_not_collected_for_stage113" in guarded_record["blockers"]
    assert "stage115_stage152_write_not_ready" in guarded_record["blockers"]


def test_stage145_blocks_guarded_stage113_input_with_non_first_provider_scope(tmp_path) -> None:
    paths = _paths(tmp_path)
    _fixture(paths, ready=True)
    stage115 = json.loads(paths["stage115_results_path"].read_text(encoding="utf-8"))
    stage115["provider_scope"] = "all"
    _write_json(paths["stage115_results_path"], stage115)

    result = run_stage145_audit(**paths)

    assert result["decision"] == "FIRST_PROVIDER_EVIDENCE_PATH_PREPARED_RESULTS_BLOCKED"
    guarded_record = next(record for record in result["readiness_records"] if record["name"] == "first_provider_stage115_guarded_stage113_input")
    assert guarded_record["ready"] is False
    assert "stage115_provider_scope_mismatch" in guarded_record["blockers"]


def test_stage145_blocks_stage113_ready_decision_without_assembled_evidence(tmp_path) -> None:
    paths = _paths(tmp_path)
    _fixture(paths, ready=True)
    stage113 = json.loads(paths["stage113_results_path"].read_text(encoding="utf-8"))
    stage113["decision"] = "JOB_RESULTS_READY_FOR_STAGE109_EVIDENCE_ASSEMBLY"
    stage113["assembled_evidence_count"] = 0
    _write_json(paths["stage113_results_path"], stage113)

    result = run_stage145_audit(**paths)

    assert result["decision"] == "FIRST_PROVIDER_EVIDENCE_PATH_PREPARED_RESULTS_BLOCKED"
    assembly_record = next(record for record in result["readiness_records"] if record["name"] == "first_provider_stage113_evidence_assembly")
    assert "stage113_not_assembled_into_stage109_evidence" in assembly_record["blockers"]
    assert "stage113_no_assembled_evidence" in assembly_record["blockers"]


def test_stage145_outputs_are_written(tmp_path) -> None:
    paths = _paths(tmp_path)
    _fixture(paths, ready=False)
    result = run_stage145_audit(**paths)

    written = write_stage145_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(written) == {"manifest", "result", "summary_csv"}
    assert manifest["decision"] == "FIRST_PROVIDER_EVIDENCE_PATH_PREPARED_RESULTS_BLOCKED"
    assert "post_configuration_authorized_runner_chain" in summary
