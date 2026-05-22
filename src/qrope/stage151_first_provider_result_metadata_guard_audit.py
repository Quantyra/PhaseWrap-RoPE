from __future__ import annotations

import csv
import json
import sys
import tempfile
from pathlib import Path
from typing import Any


RUNNER_DIR = Path(__file__).resolve().parents[2] / "scripts" / "provider_runners"
sys.path.insert(0, str(RUNNER_DIR))

from runner_guard import run_guarded_provider_runner  # noqa: E402


STAGE151_SCHEMA_VERSION = "qrope_stage151_first_provider_result_metadata_guard_audit_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE150_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage150_first_provider_result_lineage_audit" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage151_first_provider_result_metadata_guard_audit"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)
REQUIRED_BACKEND_METADATA_FIELDS = ("provider", "backend", "window_id", "job_kind")


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(record, sort_keys=True) + "\n" for record in records), encoding="utf-8")


def _synthetic_fixture(root: Path) -> dict[str, Path]:
    job_shard = root / "jobs.jsonl"
    payloads = root / "payloads.jsonl"
    results = root / "results.jsonl"
    stage111 = root / "stage111.json"
    stage118 = root / "stage118.json"
    stage129 = root / "stage129.json"
    jobs = [
        {
            "job_id": "synthetic_job_0",
            "job_kind": "known_state_calibration",
            "openqasm3": "OPENQASM 3.0;\n",
            "provider": "ibm_runtime",
            "shots": 1000,
            "window_id": "synthetic_window_0",
        }
    ]
    _write_jsonl(job_shard, jobs)
    _write_jsonl(payloads, [{"job_id": "synthetic_job_0", "provider": "ibm_runtime", "window_id": "synthetic_window_0"}])
    _write_json(stage111, {"provider_records": [{"provider": "ibm_runtime", "status": "ready", "blockers": []}]})
    _write_json(
        stage118,
        {
            "payload_records": [
                {
                    "provider": "ibm_runtime",
                    "window_id": "synthetic_window_0",
                    "payload_output_path": str(payloads.as_posix()),
                    "compiled_payload_count": 1,
                }
            ]
        },
    )
    _write_json(stage129, {"provider_records": [{"provider": "ibm_runtime", "cutover_authorized": True, "blockers": []}]})
    return {
        "job_shard": job_shard,
        "payloads": payloads,
        "results": results,
        "stage111": stage111,
        "stage118": stage118,
        "stage129": stage129,
    }


def _result(jobs: list[dict[str, Any]], provider: str, metadata_overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    metadata = {
        "provider": provider,
        "backend": "synthetic_backend",
        "window_id": jobs[0]["window_id"],
        "job_kind": jobs[0]["job_kind"],
    }
    if metadata_overrides:
        for key, value in metadata_overrides.items():
            if value is None:
                metadata.pop(key, None)
            else:
                metadata[key] = value
    return {
        "job_id": jobs[0]["job_id"],
        "job_or_task_id": "SYNTHETIC_TASK_0",
        "backend_metadata": metadata,
        "submitted_at_utc": "1970-01-01T00:00:00Z",
        "completed_at_utc": "1970-01-01T00:00:01Z",
        "counts": {"00": 1000},
    }


def _submitter(metadata_overrides: dict[str, Any] | None = None) -> Any:
    def submit(*, provider: str, jobs: list[dict[str, Any]], payloads: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [_result(jobs, provider, metadata_overrides)]

    return submit


def _runner_code(paths: dict[str, Path], submitter: Any) -> int:
    return run_guarded_provider_runner(
        "ibm_runtime",
        [
            "--job-shard",
            str(paths["job_shard"]),
            "--provider-results",
            str(paths["results"]),
            "--stage111-results",
            str(paths["stage111"]),
            "--stage118-results",
            str(paths["stage118"]),
            "--stage129-results",
            str(paths["stage129"]),
            "--allow-live-submit",
        ],
        submitter=submitter,
    )


def _synthetic_guard_records() -> list[dict[str, Any]]:
    records = []
    scenarios = [
        ("complete_backend_metadata_writes_result", _submitter(), 0, True),
        ("missing_backend_field_rejected", _submitter({"backend": None}), 5, False),
        ("wrong_window_metadata_rejected", _submitter({"window_id": "wrong_window"}), 5, False),
        ("wrong_job_kind_metadata_rejected", _submitter({"job_kind": "matched_packet_row"}), 5, False),
    ]
    with tempfile.TemporaryDirectory() as temp_text:
        root = Path(temp_text)
        for name, submitter, expected_code, expected_written in scenarios:
            paths = _synthetic_fixture(root / name)
            code = _runner_code(paths, submitter)
            written = paths["results"].exists()
            records.append(
                {
                    "check": name,
                    "exit_code": code,
                    "expected_exit_code": expected_code,
                    "result_file_written": written,
                    "expected_result_file_written": expected_written,
                    "ready": code == expected_code and written is expected_written,
                }
            )
    return records


def run_stage151_audit(*, stage150_results_path: Path = DEFAULT_STAGE150_RESULTS) -> dict[str, Any]:
    stage150 = _load_json(stage150_results_path)
    missing_sources = [str(stage150_results_path.as_posix())] if stage150 is None else []
    stage150_statistical_source_contract_ready = bool(
        isinstance(stage150, dict) and stage150.get("stage148_statistical_source_contract_ready") is True
    )
    stage150_ready = bool(
        isinstance(stage150, dict)
        and stage150.get("decision") == "FIRST_PROVIDER_RESULT_LINEAGE_CONTRACT_READY_EXECUTION_BLOCKED"
        and all(field in stage150.get("required_backend_metadata_fields", []) for field in REQUIRED_BACKEND_METADATA_FIELDS)
        and stage150_statistical_source_contract_ready
    )
    synthetic_records = _synthetic_guard_records()
    synthetic_ready = bool(synthetic_records) and all(record["ready"] for record in synthetic_records)
    ready = stage150_ready and synthetic_ready and not missing_sources
    return {
        "schema_version": STAGE151_SCHEMA_VERSION,
        "stage": "stage151_first_provider_result_metadata_guard_audit",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": (
            "FIRST_PROVIDER_RESULT_METADATA_GUARD_READY_EXECUTION_BLOCKED"
            if ready
            else "FIRST_PROVIDER_RESULT_METADATA_GUARD_INCOMPLETE"
        ),
        "source_artifacts": [str(stage150_results_path.as_posix())],
        "missing_source_artifacts": missing_sources,
        "first_unlock_provider": stage150.get("first_unlock_provider") if isinstance(stage150, dict) else "",
        "stage150_lineage_contract_ready": stage150_ready,
        "stage150_statistical_source_contract_ready": stage150_statistical_source_contract_ready,
        "stage150_stage146_ready": stage150.get("stage148_stage146_ready") if isinstance(stage150, dict) else None,
        "stage150_stage147_ready": stage150.get("stage148_stage147_ready") if isinstance(stage150, dict) else None,
        "required_backend_metadata_fields": list(REQUIRED_BACKEND_METADATA_FIELDS),
        "synthetic_guard_check_count": len(synthetic_records),
        "synthetic_guard_ready_count": sum(1 for record in synthetic_records if record["ready"]),
        "synthetic_guard_records": synthetic_records,
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "claim_boundary": {
            "supported": [
                "guarded runner rejects missing backend metadata before provider result writes",
                "guarded runner rejects window and job-kind metadata mismatches against the Stage 112 job shard",
                "complete Stage 150 backend metadata is required on the write path before live IBM result capture",
                "Stage 150 result-lineage readiness must include Stage 148 provider and Stage 146/147 source-contract readiness",
            ],
            "excluded": [
                "provider credential values",
                "hardware job submission",
                "live provider SDK client creation",
                "real provider result records",
                "a noisy-hardware robustness or auditability conclusion",
            ],
        },
        "next_gate": (
            "After IBM cutover and Stage 133 authorization, live provider submitters must pass this metadata guard "
            "before any Stage 114 provider result JSONL is written."
        ),
    }


def write_stage151_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "first_unlock_provider": result["first_unlock_provider"],
        "stage150_lineage_contract_ready": result["stage150_lineage_contract_ready"],
        "stage150_statistical_source_contract_ready": result["stage150_statistical_source_contract_ready"],
        "stage150_stage146_ready": result["stage150_stage146_ready"],
        "stage150_stage147_ready": result["stage150_stage147_ready"],
        "required_backend_metadata_fields": result["required_backend_metadata_fields"],
        "synthetic_guard_check_count": result["synthetic_guard_check_count"],
        "synthetic_guard_ready_count": result["synthetic_guard_ready_count"],
        "no_hardware_submission": result["no_hardware_submission"],
        "provider_credentials_required": result["provider_credentials_required"],
        "secret_values_recorded": result["secret_values_recorded"],
        "result_path": str((output_dir / "results.json").as_posix()),
        "summary_csv_path": str((output_dir / "summary.csv").as_posix()),
        "claim_boundary": result["claim_boundary"],
        "next_gate": result["next_gate"],
    }
    paths = {
        "manifest": str(output_dir / "manifest.json"),
        "result": str(output_dir / "results.json"),
        "summary_csv": str(output_dir / "summary.csv"),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=("check", "exit_code", "expected_exit_code", "result_file_written", "expected_result_file_written", "ready"),
        )
        writer.writeheader()
        for record in result["synthetic_guard_records"]:
            writer.writerow(record)
    return paths


def print_stage151_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"first_unlock_provider: {result['first_unlock_provider']}")
    print(f"stage150_lineage_contract_ready: {result['stage150_lineage_contract_ready']}")
    print(f"stage150_statistical_source_contract_ready: {result['stage150_statistical_source_contract_ready']}")
    print(f"synthetic_guard_ready_count: {result['synthetic_guard_ready_count']}/{result['synthetic_guard_check_count']}")
    print(f"next_gate: {result['next_gate']}")
