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


STAGE149_SCHEMA_VERSION = "qrope_stage149_first_provider_guarded_runner_contract_audit_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE111_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage111_provider_sdk_backend_discovery" / "results.json"
DEFAULT_STAGE118_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage118_provider_payload_dry_run_audit" / "results.json"
DEFAULT_STAGE129_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage129_live_cutover_authorization_audit" / "results.json"
DEFAULT_STAGE133_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage133_authorized_runner_command_packet" / "results.json"
DEFAULT_STAGE145_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage145_first_provider_evidence_path_audit" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage149_first_provider_guarded_runner_contract_audit"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)


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


def _provider_record(payload: dict[str, Any] | None, provider: str) -> dict[str, Any] | None:
    if not isinstance(payload, dict):
        return None
    for record in payload.get("provider_records", []):
        if record.get("provider") == provider:
            return record
    return None


def _command_records(payload: dict[str, Any] | None, provider: str) -> list[dict[str, Any]]:
    if not isinstance(payload, dict):
        return []
    return [record for record in payload.get("command_records", []) if record.get("provider") == provider]


def _synthetic_fixture(root: Path, *, provider: str, cutover_authorized: bool = True) -> dict[str, Path]:
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
            "provider": provider,
            "shots": 1000,
            "window_id": "synthetic_window_0",
        }
    ]
    _write_jsonl(job_shard, jobs)
    _write_jsonl(payloads, [{"job_id": "synthetic_job_0", "provider": provider, "window_id": "synthetic_window_0"}])
    _write_json(stage111, {"provider_records": [{"provider": provider, "status": "ready", "blockers": []}]})
    _write_json(
        stage118,
        {
            "payload_records": [
                {
                    "provider": provider,
                    "window_id": "synthetic_window_0",
                    "payload_output_path": str(payloads.as_posix()),
                    "compiled_payload_count": 1,
                }
            ]
        },
    )
    _write_json(
        stage129,
        {
            "provider_records": [
                {
                    "provider": provider,
                    "cutover_authorized": cutover_authorized,
                    "blockers": [] if cutover_authorized else ["synthetic_cutover_not_authorized"],
                }
            ]
        },
    )
    return {
        "job_shard": job_shard,
        "payloads": payloads,
        "results": results,
        "stage111": stage111,
        "stage118": stage118,
        "stage129": stage129,
    }


def _valid_submitter(*, provider: str, jobs: list[dict[str, Any]], payloads: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "job_id": str(jobs[0]["job_id"]),
            "job_or_task_id": "SYNTHETIC_TASK_0",
            "backend_metadata": {
                "provider": provider,
                "backend": "synthetic_backend",
                "window_id": jobs[0]["window_id"],
                "job_kind": jobs[0]["job_kind"],
            },
            "submitted_at_utc": "1970-01-01T00:00:00Z",
            "completed_at_utc": "1970-01-01T00:00:01Z",
            "counts": {"00": 1000},
        }
    ]


def _invalid_submitter(**_: Any) -> list[dict[str, Any]]:
    return [{"job_id": "unknown", "counts": {}}]


def _runner_code(paths: dict[str, Path], submitter: Any, *, provider: str) -> int:
    return run_guarded_provider_runner(
        provider,
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


def _synthetic_contract_records(provider: str) -> list[dict[str, Any]]:
    if not provider:
        return [
            {
                "check": "first_provider_scope_required",
                "exit_code": None,
                "result_file_written": False,
                "ready": False,
            }
        ]
    records: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory() as temp_text:
        root = Path(temp_text)
        pass_paths = _synthetic_fixture(root / "pass", provider=provider, cutover_authorized=True)
        pass_code = _runner_code(pass_paths, _valid_submitter, provider=provider)
        records.append(
            {
                "check": "valid_injected_submitter_writes_stage114_result",
                "exit_code": pass_code,
                "result_file_written": pass_paths["results"].exists(),
                "ready": pass_code == 0 and pass_paths["results"].exists(),
            }
        )
        blocked_paths = _synthetic_fixture(root / "blocked", provider=provider, cutover_authorized=False)
        blocked_code = _runner_code(blocked_paths, _valid_submitter, provider=provider)
        records.append(
            {
                "check": "stage129_cutover_required_before_write",
                "exit_code": blocked_code,
                "result_file_written": blocked_paths["results"].exists(),
                "ready": blocked_code == 4 and not blocked_paths["results"].exists(),
            }
        )
        invalid_paths = _synthetic_fixture(root / "invalid", provider=provider, cutover_authorized=True)
        invalid_code = _runner_code(invalid_paths, _invalid_submitter, provider=provider)
        records.append(
            {
                "check": "invalid_submitter_result_contract_rejected",
                "exit_code": invalid_code,
                "result_file_written": invalid_paths["results"].exists(),
                "ready": invalid_code == 5 and not invalid_paths["results"].exists(),
            }
        )
    return records


def run_stage149_audit(
    *,
    stage111_results_path: Path = DEFAULT_STAGE111_RESULTS,
    stage118_results_path: Path = DEFAULT_STAGE118_RESULTS,
    stage129_results_path: Path = DEFAULT_STAGE129_RESULTS,
    stage133_results_path: Path = DEFAULT_STAGE133_RESULTS,
    stage145_results_path: Path = DEFAULT_STAGE145_RESULTS,
) -> dict[str, Any]:
    stage111 = _load_json(stage111_results_path)
    stage118 = _load_json(stage118_results_path)
    stage129 = _load_json(stage129_results_path)
    stage133 = _load_json(stage133_results_path)
    stage145 = _load_json(stage145_results_path)
    sources = [
        (stage111_results_path, stage111),
        (stage118_results_path, stage118),
        (stage129_results_path, stage129),
        (stage133_results_path, stage133),
        (stage145_results_path, stage145),
    ]
    missing_sources = [str(path.as_posix()) for path, payload in sources if payload is None]
    provider = str(stage145.get("first_unlock_provider", "")) if isinstance(stage145, dict) else ""
    stage111_provider = _provider_record(stage111, provider)
    stage129_provider = _provider_record(stage129, provider)
    command_records = _command_records(stage133, provider)
    authorized_commands = [record for record in command_records if record.get("command_authorized") is True]
    synthetic_records = _synthetic_contract_records(provider)
    synthetic_ready = bool(synthetic_records) and all(record["ready"] for record in synthetic_records)
    current_cutover_authorized = bool(stage129_provider and stage129_provider.get("cutover_authorized") is True)
    current_stage111_ready = bool(stage111_provider and stage111_provider.get("status") == "ready")
    return {
        "schema_version": STAGE149_SCHEMA_VERSION,
        "stage": "stage149_first_provider_guarded_runner_contract_audit",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": (
            "FIRST_PROVIDER_GUARDED_RUNNER_CONTRACT_READY_CUTOVER_BLOCKED"
            if synthetic_ready and not missing_sources
            else "FIRST_PROVIDER_GUARDED_RUNNER_CONTRACT_INCOMPLETE"
        ),
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "first_unlock_provider": provider,
        "current_stage111_ready": current_stage111_ready,
        "current_stage129_cutover_authorized": current_cutover_authorized,
        "first_provider_runner_command_count": len(command_records),
        "first_provider_authorized_runner_count": len(authorized_commands),
        "synthetic_contract_check_count": len(synthetic_records),
        "synthetic_contract_ready_count": sum(1 for record in synthetic_records if record["ready"]),
        "synthetic_contract_records": synthetic_records,
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "claim_boundary": {
            "supported": [
                "first-provider guarded runner validates Stage 114-shaped result records before writing provider result JSONL",
                "Stage 129 cutover authorization is required before any guarded result write",
                "invalid submitter records fail closed without writing provider result files",
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
            "Clear Stage 140/106/111/129 and Stage 133 authorization, then use the guarded first-provider runner. "
            "Stage 149 only proves the runner contract with synthetic injected submitters."
        ),
    }


def write_stage149_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
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
        "current_stage111_ready": result["current_stage111_ready"],
        "current_stage129_cutover_authorized": result["current_stage129_cutover_authorized"],
        "first_provider_runner_command_count": result["first_provider_runner_command_count"],
        "first_provider_authorized_runner_count": result["first_provider_authorized_runner_count"],
        "synthetic_contract_check_count": result["synthetic_contract_check_count"],
        "synthetic_contract_ready_count": result["synthetic_contract_ready_count"],
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
        writer = csv.DictWriter(handle, fieldnames=("check", "exit_code", "result_file_written", "ready"))
        writer.writeheader()
        for record in result["synthetic_contract_records"]:
            writer.writerow(record)
    return paths


def print_stage149_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"first_unlock_provider: {result['first_unlock_provider']}")
    print(f"current_stage111_ready: {result['current_stage111_ready']}")
    print(f"current_stage129_cutover_authorized: {result['current_stage129_cutover_authorized']}")
    print(f"synthetic_contract_ready_count: {result['synthetic_contract_ready_count']}/{result['synthetic_contract_check_count']}")
    print(f"next_gate: {result['next_gate']}")
