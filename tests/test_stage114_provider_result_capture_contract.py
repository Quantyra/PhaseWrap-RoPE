from __future__ import annotations

import json

from qrope.stage114_provider_result_capture_contract import run_stage114_contract, write_stage114_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _write_jsonl(path, records) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(record, sort_keys=True) + "\n" for record in records), encoding="utf-8")


def _jobs() -> list[dict[str, object]]:
    return [
        {"job_id": "job_a", "provider": "ibm_runtime", "window_id": "window_0", "job_kind": "known_state_calibration"},
        {"job_id": "job_b", "provider": "ibm_runtime", "window_id": "window_0", "job_kind": "matched_packet_row"},
        {"job_id": "job_c", "provider": "amazon_braket", "window_id": "window_1", "job_kind": "known_state_calibration"},
    ]


def test_stage114_reports_missing_sources(tmp_path) -> None:
    result = run_stage114_contract(stage112_job_manifest_path=tmp_path / "missing_jobs.jsonl", stage113_manifest_path=tmp_path / "missing113.json")

    assert result["status"] == "incomplete"
    assert result["decision"] == "PROVIDER_RESULT_CAPTURE_CONTRACT_INCOMPLETE"
    assert len(result["missing_source_artifacts"]) == 2


def test_stage114_groups_jobs_into_provider_window_shards(tmp_path) -> None:
    _write_jsonl(tmp_path / "jobs.jsonl", _jobs())
    _write_json(tmp_path / "stage113.json", {"decision": "JOB_RESULT_EVIDENCE_ASSEMBLY_BLOCKED_RESULTS_MISSING"})

    result = run_stage114_contract(stage112_job_manifest_path=tmp_path / "jobs.jsonl", stage113_manifest_path=tmp_path / "stage113.json")

    assert result["decision"] == "PROVIDER_RESULT_CAPTURE_CONTRACT_PREPARED_RESULTS_REQUIRED"
    assert result["job_count"] == 3
    assert result["shard_count"] == 2
    assert "counts" in result["required_result_fields"]


def test_stage114_outputs_schema_shards_and_stubs(tmp_path) -> None:
    jobs = _jobs()
    _write_jsonl(tmp_path / "jobs.jsonl", jobs)
    _write_json(tmp_path / "stage113.json", {"decision": "JOB_RESULT_EVIDENCE_ASSEMBLY_BLOCKED_RESULTS_MISSING"})
    result = run_stage114_contract(stage112_job_manifest_path=tmp_path / "jobs.jsonl", stage113_manifest_path=tmp_path / "stage113.json")

    paths = write_stage114_outputs(result, jobs, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    schema = json.loads((tmp_path / "out" / "provider_job_result_schema.json").read_text(encoding="utf-8"))
    shard = tmp_path / "out" / "job_shards" / "ibm_runtime" / "window_0" / "jobs.jsonl"
    stub = tmp_path / "out" / "result_stubs" / "ibm_runtime" / "window_0" / "provider_job_results.stub.jsonl"

    assert set(paths) == {"manifest", "result", "summary_csv", "schema"}
    assert manifest["shard_count"] == 2
    assert schema["required_fields"] == ["job_id", "job_or_task_id", "backend_metadata", "submitted_at_utc", "completed_at_utc", "counts"]
    assert len(shard.read_text(encoding="utf-8").splitlines()) == 2
    stub_record = json.loads(stub.read_text(encoding="utf-8").splitlines()[0])
    assert stub_record["counts"] == {}
    assert stub_record["job_or_task_id"] == ""
