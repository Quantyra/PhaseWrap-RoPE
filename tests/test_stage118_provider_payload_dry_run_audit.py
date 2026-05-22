from __future__ import annotations

import json
from pathlib import Path

from qrope.stage118_provider_payload_dry_run_audit import run_stage118_audit, write_stage118_outputs


def _write_json(path, payload) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _write_jsonl(path, records) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(record, sort_keys=True) + "\n" for record in records), encoding="utf-8")


def _fixture(tmp_path):
    shard = tmp_path / "stage114" / "job_shards" / "ibm_runtime" / "window_0" / "jobs.jsonl"
    jobs = [
        {
            "job_id": "job_cal",
            "job_kind": "known_state_calibration",
            "openqasm3": "OPENQASM 3.0;\nqubit[2] q;\n",
            "provider": "ibm_runtime",
            "shots": 1000,
            "target_evidence_path": "calibration.json",
            "window_id": "window_0",
        },
        {
            "job_id": "job_packet",
            "job_kind": "matched_packet_row",
            "openqasm3": "OPENQASM 3.0;\nqubit[2] q;\n",
            "provider": "ibm_runtime",
            "shots": 1000,
            "target_evidence_path": "packet.json",
            "window_id": "window_0",
        },
    ]
    _write_jsonl(shard, jobs)
    _write_json(
        tmp_path / "stage116.json",
        {
            "decision": "PROVIDER_RUNNER_PLAN_PREPARED_EXECUTION_BLOCKED",
            "runner_records": [
                {
                    "provider": "ibm_runtime",
                    "window_id": "window_0",
                    "job_count": 2,
                    "job_shard_path": str(shard.as_posix()),
                    "provider_result_path": "provider_results.jsonl",
                }
            ],
        },
    )
    return tmp_path / "stage116.json"


def test_stage118_reports_missing_source() -> None:
    result = run_stage118_audit(stage116_results_path=Path("missing_stage116.json"))

    assert result["status"] == "incomplete"
    assert result["decision"] == "PROVIDER_PAYLOAD_DRY_RUN_INCOMPLETE"
    assert result["compiled_payload_count"] == 0


def test_stage118_compiles_payloads_from_runner_shard(tmp_path) -> None:
    stage116 = _fixture(tmp_path)

    result = run_stage118_audit(stage116_results_path=stage116, output_dir=tmp_path / "out")

    assert result["decision"] == "PROVIDER_PAYLOAD_DRY_RUN_COMPILED_EXECUTION_BLOCKED"
    assert result["compiled_payload_count"] == 2
    assert result["expected_job_count"] == 2
    assert result["payload_records"][0]["ready"] is True
    payloads = next(iter(result["payloads_by_path"].values()))
    assert payloads[0]["provider_submission_kind"] == "ibm_runtime_openqasm3_sampler"
    assert payloads[0]["dry_run_only"] is True
    assert "openqasm3_sha256" in payloads[0]


def test_stage118_outputs_are_written(tmp_path) -> None:
    stage116 = _fixture(tmp_path)
    result = run_stage118_audit(stage116_results_path=stage116, output_dir=tmp_path / "out")

    paths = write_stage118_outputs(result, tmp_path / "out")
    manifest = json.loads((tmp_path / "out" / "manifest.json").read_text(encoding="utf-8"))
    summary = (tmp_path / "out" / "summary.csv").read_text(encoding="utf-8")
    payload_file = tmp_path / "out" / "dry_run_payloads" / "ibm_runtime" / "window_0" / "submission_payloads.jsonl"

    assert set(paths) == {"manifest", "result", "summary_csv"}
    assert manifest["compiled_payload_count"] == 2
    assert "window_0" in summary
    assert payload_file.exists()
    assert len(payload_file.read_text(encoding="utf-8").splitlines()) == 2
