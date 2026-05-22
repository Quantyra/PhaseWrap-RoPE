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

    result = run_stage115_collector(
        stage114_manifest_path=root / "manifest.json",
        stage114_output_dir=root,
        stage113_provider_results_path=tmp_path / "stage113.jsonl",
        write_stage113_input=True,
    )

    assert result["decision"] == "PROVIDER_RESULTS_COLLECTED_FOR_STAGE113"
    assert result["wrote_stage113_input"] is True
    assert len((tmp_path / "stage113.jsonl").read_text(encoding="utf-8").splitlines()) == 2


def test_stage115_can_collect_provider_scoped_shards(tmp_path) -> None:
    root, ibm_result = _multi_provider_stage114_fixture(tmp_path)
    _write_jsonl(ibm_result, [_result("ibm_job")])

    result = run_stage115_collector(
        stage114_manifest_path=root / "manifest.json",
        stage114_output_dir=root,
        stage113_provider_results_path=tmp_path / "stage113.jsonl",
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
