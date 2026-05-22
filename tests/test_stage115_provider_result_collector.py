from __future__ import annotations

import json

from qrope.stage115_provider_result_collector import run_stage115_collector, write_stage115_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _write_jsonl(path, records) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(record, sort_keys=True) + "\n" for record in records), encoding="utf-8")


def _stage114_fixture(tmp_path):
    root = tmp_path / "stage114"
    shard = root / "job_shards" / "ibm_runtime" / "window_0" / "jobs.jsonl"
    result = root / "provider_results" / "ibm_runtime" / "window_0" / "provider_job_results.jsonl"
    _write_jsonl(shard, [{"job_id": "job_a"}, {"job_id": "job_b"}])
    _write_json(
        root / "manifest.json",
        {
            "decision": "PROVIDER_RESULT_CAPTURE_CONTRACT_PREPARED_RESULTS_REQUIRED",
            "job_shard_paths": [str(shard.as_posix())],
        },
    )
    return root, result


def _multi_provider_stage114_fixture(tmp_path):
    root = tmp_path / "stage114"
    ibm_shard = root / "job_shards" / "ibm_runtime" / "window_0" / "jobs.jsonl"
    braket_shard = root / "job_shards" / "amazon_braket" / "window_0" / "jobs.jsonl"
    ibm_result = root / "provider_results" / "ibm_runtime" / "window_0" / "provider_job_results.jsonl"
    _write_jsonl(ibm_shard, [{"job_id": "ibm_job"}])
    _write_jsonl(braket_shard, [{"job_id": "braket_job"}])
    _write_json(
        root / "manifest.json",
        {
            "decision": "PROVIDER_RESULT_CAPTURE_CONTRACT_PREPARED_RESULTS_REQUIRED",
            "job_shard_paths": [str(ibm_shard.as_posix()), str(braket_shard.as_posix())],
        },
    )
    return root, ibm_result


def _result(job_id: str) -> dict[str, object]:
    return {
        "job_id": job_id,
        "job_or_task_id": f"task-{job_id}",
        "backend_metadata": {"backend": "backend_a"},
        "submitted_at_utc": "2026-05-21T00:00:00Z",
        "completed_at_utc": "2026-05-21T00:01:00Z",
        "counts": {"00": 10},
    }


def _stage152_ready(path) -> None:
    _write_json(
        path,
        {
            "decision": "FIRST_PROVIDER_LIVE_EXECUTION_GUARD_READY_FOR_GUARDED_RUNNER",
            "first_unlock_provider": "ibm_runtime",
            "missing_source_artifacts": [],
            "blockers": [],
            "stage144_ready_for_authorized_runner": True,
            "stage144_ready_transition_count": 9,
            "stage144_transition_count": 9,
            "stage144_first_blocked_transition": None,
            "stage151_metadata_guard_ready": True,
            "first_provider_runner_command_count": 1,
            "first_provider_authorized_runner_count": 1,
            "first_provider_live_submit_ready_count": 1,
            "all_first_provider_commands_authorized": True,
            "all_first_provider_commands_live_submit_ready": True,
        },
    )


def _stage152_blocked(path) -> None:
    _write_json(
        path,
        {
            "decision": "FIRST_PROVIDER_LIVE_EXECUTION_GUARD_PREPARED_EXECUTION_BLOCKED",
            "first_unlock_provider": "ibm_runtime",
            "missing_source_artifacts": [],
            "blockers": ["stage144_post_configuration_chain_not_ready"],
            "stage144_ready_for_authorized_runner": False,
            "stage144_ready_transition_count": 8,
            "stage144_transition_count": 9,
            "stage144_first_blocked_transition": {"stage": "stage140_local_provider_configuration_readiness"},
            "stage151_metadata_guard_ready": True,
            "first_provider_runner_command_count": 1,
            "first_provider_authorized_runner_count": 0,
            "first_provider_live_submit_ready_count": 0,
            "all_first_provider_commands_authorized": False,
            "all_first_provider_commands_live_submit_ready": False,
        },
    )


def test_stage115_reports_missing_manifest(tmp_path) -> None:
    result = run_stage115_collector(stage114_manifest_path=tmp_path / "missing.json")

    assert result["status"] == "incomplete"
    assert result["decision"] == "PROVIDER_RESULTS_COLLECTION_BLOCKED_RESULTS_MISSING"
    assert result["missing_source_artifacts"]


def test_stage115_blocks_when_provider_result_shard_is_missing(tmp_path) -> None:
    root, _ = _stage114_fixture(tmp_path)

    result = run_stage115_collector(stage114_manifest_path=root / "manifest.json", stage114_output_dir=root)

    assert result["decision"] == "PROVIDER_RESULTS_COLLECTION_BLOCKED_RESULTS_MISSING"
    assert result["missing_job_count"] == 2
    assert result["ready_shard_count"] == 0


def test_stage115_detects_complete_shard_without_writing_by_default(tmp_path) -> None:
    root, result_path = _stage114_fixture(tmp_path)
    _write_jsonl(result_path, [_result("job_a"), _result("job_b")])

    result = run_stage115_collector(stage114_manifest_path=root / "manifest.json", stage114_output_dir=root, stage113_provider_results_path=tmp_path / "stage113.jsonl")

    assert result["decision"] == "PROVIDER_RESULTS_READY_TO_COLLECT"
    assert result["ready_shard_count"] == 1
    assert not (tmp_path / "stage113.jsonl").exists()


def test_stage115_writes_stage113_input_when_enabled(tmp_path) -> None:
    root, result_path = _stage114_fixture(tmp_path)
    _write_jsonl(result_path, [_result("job_a"), _result("job_b")])
    _stage152_ready(tmp_path / "stage152.json")

    result = run_stage115_collector(
        stage114_manifest_path=root / "manifest.json",
        stage114_output_dir=root,
        stage113_provider_results_path=tmp_path / "stage113.jsonl",
        stage152_results_path=tmp_path / "stage152.json",
        write_stage113_input=True,
    )

    assert result["decision"] == "PROVIDER_RESULTS_COLLECTED_FOR_STAGE113"
    assert result["wrote_stage113_input"] is True
    assert len((tmp_path / "stage113.jsonl").read_text(encoding="utf-8").splitlines()) == 2


def test_stage115_blocks_stage113_input_write_when_stage152_not_ready(tmp_path) -> None:
    root, result_path = _stage114_fixture(tmp_path)
    _write_jsonl(result_path, [_result("job_a"), _result("job_b")])
    _stage152_blocked(tmp_path / "stage152.json")

    result = run_stage115_collector(
        stage114_manifest_path=root / "manifest.json",
        stage114_output_dir=root,
        stage113_provider_results_path=tmp_path / "stage113.jsonl",
        stage152_results_path=tmp_path / "stage152.json",
        write_stage113_input=True,
    )

    assert result["decision"] == "PROVIDER_RESULTS_COLLECTION_BLOCKED_LIVE_GUARD_REQUIRED"
    assert result["wrote_stage113_input"] is False
    assert "stage152_live_execution_guard_not_ready" in result["stage152_write_blockers"]
    assert not (tmp_path / "stage113.jsonl").exists()


def test_stage115_blocks_stage113_input_write_when_stage152_ready_decision_lacks_stage144_evidence(tmp_path) -> None:
    root, result_path = _stage114_fixture(tmp_path)
    _write_jsonl(result_path, [_result("job_a"), _result("job_b")])
    _write_json(
        tmp_path / "stage152.json",
        {
            "decision": "FIRST_PROVIDER_LIVE_EXECUTION_GUARD_READY_FOR_GUARDED_RUNNER",
            "first_unlock_provider": "ibm_runtime",
            "missing_source_artifacts": [],
            "blockers": [],
            "stage144_ready_for_authorized_runner": False,
            "stage144_ready_transition_count": 8,
            "stage144_transition_count": 9,
            "stage144_first_blocked_transition": {"stage": "stage140_local_provider_configuration_readiness"},
            "stage151_metadata_guard_ready": True,
            "first_provider_runner_command_count": 1,
            "first_provider_authorized_runner_count": 1,
            "first_provider_live_submit_ready_count": 1,
            "all_first_provider_commands_authorized": True,
            "all_first_provider_commands_live_submit_ready": True,
        },
    )

    result = run_stage115_collector(
        stage114_manifest_path=root / "manifest.json",
        stage114_output_dir=root,
        stage113_provider_results_path=tmp_path / "stage113.jsonl",
        stage152_results_path=tmp_path / "stage152.json",
        write_stage113_input=True,
    )

    assert result["decision"] == "PROVIDER_RESULTS_COLLECTION_BLOCKED_LIVE_GUARD_REQUIRED"
    assert result["wrote_stage113_input"] is False
    assert "stage152_stage144_not_ready" in result["stage152_write_blockers"]
    assert "stage152_stage144_blocked_transition_present" in result["stage152_write_blockers"]
    assert "stage152_stage144_transition_counts_incomplete" in result["stage152_write_blockers"]
    assert not (tmp_path / "stage113.jsonl").exists()


def test_stage115_blocks_stage113_input_write_when_stage152_lacks_complete_live_submit_readiness(tmp_path) -> None:
    root, result_path = _stage114_fixture(tmp_path)
    _write_jsonl(result_path, [_result("job_a"), _result("job_b")])
    _write_json(
        tmp_path / "stage152.json",
        {
            "decision": "FIRST_PROVIDER_LIVE_EXECUTION_GUARD_READY_FOR_GUARDED_RUNNER",
            "first_unlock_provider": "ibm_runtime",
            "missing_source_artifacts": [],
            "blockers": [],
            "stage144_ready_for_authorized_runner": True,
            "stage144_ready_transition_count": 9,
            "stage144_transition_count": 9,
            "stage144_first_blocked_transition": None,
            "stage151_metadata_guard_ready": True,
            "first_provider_runner_command_count": 2,
            "first_provider_authorized_runner_count": 1,
            "first_provider_live_submit_ready_count": 1,
            "all_first_provider_commands_authorized": False,
            "all_first_provider_commands_live_submit_ready": False,
        },
    )

    result = run_stage115_collector(
        stage114_manifest_path=root / "manifest.json",
        stage114_output_dir=root,
        stage113_provider_results_path=tmp_path / "stage113.jsonl",
        stage152_results_path=tmp_path / "stage152.json",
        write_stage113_input=True,
    )

    assert result["decision"] == "PROVIDER_RESULTS_COLLECTION_BLOCKED_LIVE_GUARD_REQUIRED"
    assert result["wrote_stage113_input"] is False
    assert "stage152_not_all_first_provider_commands_authorized" in result["stage152_write_blockers"]
    assert "stage152_not_all_first_provider_commands_live_submit_ready" in result["stage152_write_blockers"]
    assert "stage152_authorized_runner_count_incomplete" in result["stage152_write_blockers"]
    assert "stage152_live_submit_ready_count_incomplete" in result["stage152_write_blockers"]
    assert not (tmp_path / "stage113.jsonl").exists()


def test_stage115_blocks_stage113_input_write_when_stage152_blockers_remain(tmp_path) -> None:
    root, result_path = _stage114_fixture(tmp_path)
    _write_jsonl(result_path, [_result("job_a"), _result("job_b")])
    _write_json(
        tmp_path / "stage152.json",
        {
            "decision": "FIRST_PROVIDER_LIVE_EXECUTION_GUARD_READY_FOR_GUARDED_RUNNER",
            "first_unlock_provider": "ibm_runtime",
            "missing_source_artifacts": [],
            "blockers": ["stage133_no_authorized_first_provider_commands"],
            "stage144_ready_for_authorized_runner": True,
            "stage144_ready_transition_count": 9,
            "stage144_transition_count": 9,
            "stage144_first_blocked_transition": None,
            "stage151_metadata_guard_ready": True,
            "first_provider_runner_command_count": 1,
            "first_provider_authorized_runner_count": 1,
            "first_provider_live_submit_ready_count": 1,
            "all_first_provider_commands_authorized": True,
            "all_first_provider_commands_live_submit_ready": True,
        },
    )

    result = run_stage115_collector(
        stage114_manifest_path=root / "manifest.json",
        stage114_output_dir=root,
        stage113_provider_results_path=tmp_path / "stage113.jsonl",
        stage152_results_path=tmp_path / "stage152.json",
        write_stage113_input=True,
    )

    assert result["decision"] == "PROVIDER_RESULTS_COLLECTION_BLOCKED_LIVE_GUARD_REQUIRED"
    assert result["wrote_stage113_input"] is False
    assert result["stage152_blockers"] == ["stage133_no_authorized_first_provider_commands"]
    assert "stage152_blockers_present" in result["stage152_write_blockers"]
    assert not (tmp_path / "stage113.jsonl").exists()


def test_stage115_can_collect_provider_scoped_shards(tmp_path) -> None:
    root, ibm_result = _multi_provider_stage114_fixture(tmp_path)
    _write_jsonl(ibm_result, [_result("ibm_job")])
    _stage152_ready(tmp_path / "stage152.json")

    result = run_stage115_collector(
        stage114_manifest_path=root / "manifest.json",
        stage114_output_dir=root,
        stage113_provider_results_path=tmp_path / "stage113.jsonl",
        stage152_results_path=tmp_path / "stage152.json",
        write_stage113_input=True,
        provider="ibm_runtime",
    )

    assert result["provider_scope"] == "ibm_runtime"
    assert result["available_shard_count"] == 2
    assert result["shard_count"] == 1
    assert result["decision"] == "PROVIDER_RESULTS_COLLECTED_FOR_STAGE113"


def test_stage115_outputs_are_written(tmp_path) -> None:
    root, _ = _stage114_fixture(tmp_path)
    result = run_stage115_collector(stage114_manifest_path=root / "manifest.json", stage114_output_dir=root)

    paths = write_stage115_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert manifest["expected_job_count"] == 2
    assert "window_0" in summary
