from __future__ import annotations

import json

from qrope.stage116_provider_runner_plan import run_stage116_runner_plan, write_stage116_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _write_jsonl(path, records) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(record, sort_keys=True) + "\n" for record in records), encoding="utf-8")


def _fixture(tmp_path, *, provider_status: str = "blocked"):
    shard = tmp_path / "stage114" / "job_shards" / "ibm_runtime" / "window_0" / "jobs.jsonl"
    _write_jsonl(shard, [{"job_id": "job_cal", "job_kind": "known_state_calibration"}, {"job_id": "job_packet", "job_kind": "matched_packet_row"}])
    _write_json(
        tmp_path / "stage114.json",
        {
            "decision": "PROVIDER_RESULT_CAPTURE_CONTRACT_PREPARED_RESULTS_REQUIRED",
            "required_result_fields": ["job_id", "counts"],
            "job_shard_paths": [str(shard.as_posix())],
        },
    )
    _write_json(
        tmp_path / "stage111.json",
        {
            "decision": "PROVIDER_SDK_BACKEND_DISCOVERY_READY_NO_SUBMISSION" if provider_status == "ready" else "PROVIDER_SDK_BACKEND_DISCOVERY_BLOCKED",
            "provider_records": [{"provider": "ibm_runtime", "status": provider_status, "blockers": [] if provider_status == "ready" else ["stage106_provider_preflight_not_ready"]}],
        },
    )
    _write_json(tmp_path / "stage118.json", {"decision": "PROVIDER_PAYLOAD_DRY_RUN_COMPILED_EXECUTION_BLOCKED"})
    _write_json(tmp_path / "stage129.json", {"decision": "LIVE_CUTOVER_BLOCKED_READINESS_REQUIRED"})


def test_stage116_reports_missing_sources(tmp_path) -> None:
    result = run_stage116_runner_plan(
        stage111_results_path=tmp_path / "missing111.json",
        stage114_manifest_path=tmp_path / "missing114.json",
        stage118_results_path=tmp_path / "missing118.json",
        stage129_results_path=tmp_path / "missing129.json",
    )

    assert result["status"] == "incomplete"
    assert result["decision"] == "PROVIDER_RUNNER_PLAN_PREPARED_EXECUTION_BLOCKED"
    assert len(result["missing_source_artifacts"]) == 4


def test_stage116_blocks_runner_when_stage111_provider_not_ready(tmp_path) -> None:
    _fixture(tmp_path, provider_status="blocked")

    result = run_stage116_runner_plan(
        stage111_results_path=tmp_path / "stage111.json",
        stage114_manifest_path=tmp_path / "stage114.json",
        stage118_results_path=tmp_path / "stage118.json",
        stage129_results_path=tmp_path / "stage129.json",
    )

    assert result["decision"] == "PROVIDER_RUNNER_PLAN_PREPARED_EXECUTION_BLOCKED"
    assert result["ready_runner_count"] == 0
    assert result["runner_records"][0]["job_count"] == 2
    assert "stage111_provider_not_ready" in result["runner_records"][0]["blockers"]


def test_stage116_marks_runner_ready_when_stage111_provider_ready(tmp_path) -> None:
    _fixture(tmp_path, provider_status="ready")

    result = run_stage116_runner_plan(
        stage111_results_path=tmp_path / "stage111.json",
        stage114_manifest_path=tmp_path / "stage114.json",
        stage118_results_path=tmp_path / "stage118.json",
        stage129_results_path=tmp_path / "stage129.json",
    )

    assert result["decision"] == "PROVIDER_RUNNER_PLAN_READY_FOR_EXECUTION"
    assert result["ready_runner_count"] == 1
    assert "run_ibm_runtime_stage112_jobs.py" in result["runner_records"][0]["runner_command"]
    assert "--stage129-results" in result["runner_records"][0]["runner_command"]


def test_stage116_outputs_are_written(tmp_path) -> None:
    _fixture(tmp_path, provider_status="blocked")
    result = run_stage116_runner_plan(
        stage111_results_path=tmp_path / "stage111.json",
        stage114_manifest_path=tmp_path / "stage114.json",
        stage118_results_path=tmp_path / "stage118.json",
        stage129_results_path=tmp_path / "stage129.json",
    )

    paths = write_stage116_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert manifest["runner_count"] == 1
    assert "window_0" in summary
