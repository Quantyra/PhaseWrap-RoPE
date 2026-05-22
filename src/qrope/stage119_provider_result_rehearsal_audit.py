from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


STAGE119_SCHEMA_VERSION = "qrope_stage119_provider_result_rehearsal_audit_v1"
REHEARSAL_RECORD_SCHEMA_VERSION = "qrope_stage119_provider_result_rehearsal_record_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE118_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage118_provider_payload_dry_run_audit" / "results.json"
DEFAULT_STAGE114_SCHEMA = DEFAULT_ARTIFACT_ROOT / "stage114_provider_result_capture_contract" / "provider_job_result_schema.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage119_provider_result_rehearsal_audit"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _load_jsonl(path: Path) -> list[dict[str, Any]] | None:
    if not path.exists():
        return None
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _rehearsal_output_path(output_dir: Path, provider: str, window_id: str) -> Path:
    return output_dir / "rehearsal_results" / provider / window_id / "provider_job_results.rehearsal.jsonl"


def _synthetic_counts(payload: dict[str, Any]) -> dict[str, int]:
    shots = int(payload.get("shots") or 1)
    key = str(payload.get("target_counts_key") or "00")
    if len(key) == 2 and set(key) <= {"0", "1"}:
        return {key: shots}
    return {"00": shots}


def _rehearsal_record(payload: dict[str, Any]) -> dict[str, Any]:
    job_id = str(payload.get("job_id", ""))
    return {
        "schema_version": REHEARSAL_RECORD_SCHEMA_VERSION,
        "dry_run_only": True,
        "not_hardware_evidence": True,
        "job_id": job_id,
        "job_or_task_id": f"DRY_RUN_REHEARSAL::{job_id}",
        "backend_metadata": {
            "provider": payload.get("provider"),
            "window_id": payload.get("window_id"),
            "job_kind": payload.get("job_kind"),
            "provider_submission_kind": payload.get("provider_submission_kind"),
            "openqasm3_sha256": payload.get("openqasm3_sha256"),
            "result_source": "synthetic_contract_rehearsal_not_hardware",
        },
        "submitted_at_utc": "1970-01-01T00:00:00Z",
        "completed_at_utc": "1970-01-01T00:00:00Z",
        "counts": _synthetic_counts(payload),
    }


def _counts_present(counts: Any) -> bool:
    if not isinstance(counts, dict) or not counts:
        return False
    try:
        return sum(int(value) for value in counts.values()) > 0
    except (TypeError, ValueError):
        return False


def _validate_required_fields(record: dict[str, Any], required_fields: list[str]) -> list[str]:
    missing = []
    for field in required_fields:
        if field not in record or record.get(field) in (None, "", []):
            missing.append(field)
    if "counts" in required_fields and not _counts_present(record.get("counts")):
        missing.append("counts")
    if record.get("dry_run_only") is not True:
        missing.append("dry_run_marker_missing")
    if record.get("not_hardware_evidence") is not True:
        missing.append("not_hardware_marker_missing")
    return sorted(set(missing))


def _payload_record_rehearsal(
    payload_record: dict[str, Any],
    *,
    required_fields: list[str],
    output_dir: Path,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    provider = str(payload_record.get("provider", ""))
    window_id = str(payload_record.get("window_id", ""))
    payload_path = Path(str(payload_record.get("payload_output_path", "")))
    payloads = _load_jsonl(payload_path)
    missing = []
    if payloads is None:
        missing.append("payload_file_missing")
        payloads = []
    records = [_rehearsal_record(payload) for payload in payloads]
    invalid_records = []
    for record in records:
        problems = _validate_required_fields(record, required_fields)
        if problems:
            invalid_records.append({"job_id": record.get("job_id"), "missing_evidence": problems})
    if int(payload_record.get("compiled_payload_count", 0)) != len(records):
        missing.append("payload_count_mismatch")
    output_path = _rehearsal_output_path(output_dir, provider, window_id)
    return (
        {
            "provider": provider,
            "window_id": window_id,
            "payload_output_path": str(payload_path.as_posix()),
            "rehearsal_result_path": str(output_path.as_posix()),
            "expected_payload_count": payload_record.get("compiled_payload_count", 0),
            "rehearsal_record_count": len(records),
            "invalid_rehearsal_record_count": len(invalid_records),
            "missing_evidence": sorted(set(missing)),
            "ready": not missing and not invalid_records and bool(records),
        },
        records,
        invalid_records,
    )


def run_stage119_audit(
    *,
    stage118_results_path: Path = DEFAULT_STAGE118_RESULTS,
    stage114_schema_path: Path = DEFAULT_STAGE114_SCHEMA,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
) -> dict[str, Any]:
    stage118 = _load_json(stage118_results_path)
    schema = _load_json(stage114_schema_path)
    sources = [(stage118_results_path, stage118), (stage114_schema_path, schema)]
    missing_sources = [str(path.as_posix()) for path, payload in sources if payload is None]
    required_fields = list(schema.get("required_fields", [])) if isinstance(schema, dict) else []
    rehearsal_records = []
    rehearsals_by_path: dict[str, list[dict[str, Any]]] = {}
    invalid_records = []
    if isinstance(stage118, dict) and required_fields:
        for payload_record in stage118.get("payload_records", []):
            summary, records, invalid = _payload_record_rehearsal(
                payload_record,
                required_fields=required_fields,
                output_dir=output_dir,
            )
            rehearsal_records.append(summary)
            rehearsals_by_path[summary["rehearsal_result_path"]] = records
            invalid_records.extend({**item, "provider": summary["provider"], "window_id": summary["window_id"]} for item in invalid)
    ready = bool(rehearsal_records) and all(record["ready"] for record in rehearsal_records) and not missing_sources
    return {
        "schema_version": STAGE119_SCHEMA_VERSION,
        "stage": "stage119_provider_result_rehearsal_audit",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": (
            "PROVIDER_RESULT_REHEARSAL_READY_EXECUTION_BLOCKED"
            if ready
            else "PROVIDER_RESULT_REHEARSAL_INCOMPLETE"
        ),
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "stage118_decision": stage118.get("decision") if isinstance(stage118, dict) else None,
        "required_result_fields": required_fields,
        "runner_count": len(rehearsal_records),
        "ready_rehearsal_count": sum(1 for record in rehearsal_records if record["ready"]),
        "expected_payload_count": sum(int(record["expected_payload_count"]) for record in rehearsal_records),
        "rehearsal_record_count": sum(int(record["rehearsal_record_count"]) for record in rehearsal_records),
        "invalid_rehearsal_record_count": len(invalid_records),
        "rehearsal_records": rehearsal_records,
        "invalid_rehearsal_records": invalid_records,
        "rehearsals_by_path": rehearsals_by_path,
        "no_hardware_submission": True,
        "provider_credentials_required": True,
        "secret_values_recorded": False,
        "claim_boundary": {
            "supported": [
                "Stage 118 payloads can be transformed into Stage 114-shaped result records",
                "required Stage 114 result fields are present in isolated dry-run rehearsal records",
                "live runner implementation has a validated result-record target before submission",
            ],
            "excluded": [
                "hardware job submission",
                "provider credentials or secret values",
                "real provider result records",
                "Stage 113 evidence assembly",
                "a noisy-hardware robustness result",
            ],
        },
        "next_gate": (
            "Clear Stage 106/111 provider readiness, then replace rehearsal counts and dry-run identifiers with real "
            "provider job IDs, timestamps, backend metadata, and measured counts in Stage 114 provider result paths."
        ),
    }


def write_stage119_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    for path_text, records in result["rehearsals_by_path"].items():
        path = Path(path_text)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("".join(json.dumps(record, sort_keys=True) + "\n" for record in records), encoding="utf-8")
    result_without_rehearsals = {key: value for key, value in result.items() if key != "rehearsals_by_path"}
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "stage118_decision": result["stage118_decision"],
        "required_result_fields": result["required_result_fields"],
        "runner_count": result["runner_count"],
        "ready_rehearsal_count": result["ready_rehearsal_count"],
        "expected_payload_count": result["expected_payload_count"],
        "rehearsal_record_count": result["rehearsal_record_count"],
        "invalid_rehearsal_record_count": result["invalid_rehearsal_record_count"],
        "rehearsal_result_paths": list(result["rehearsals_by_path"]),
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
    (output_dir / "results.json").write_text(json.dumps(result_without_rehearsals, indent=2, sort_keys=True), encoding="utf-8")
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=(
                "provider",
                "window_id",
                "expected_payload_count",
                "rehearsal_record_count",
                "invalid_rehearsal_record_count",
                "ready",
                "missing_evidence",
            ),
        )
        writer.writeheader()
        for record in result["rehearsal_records"]:
            writer.writerow(
                {
                    "provider": record["provider"],
                    "window_id": record["window_id"],
                    "expected_payload_count": record["expected_payload_count"],
                    "rehearsal_record_count": record["rehearsal_record_count"],
                    "invalid_rehearsal_record_count": record["invalid_rehearsal_record_count"],
                    "ready": record["ready"],
                    "missing_evidence": "; ".join(record["missing_evidence"]),
                }
            )
    return paths


def print_stage119_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"rehearsal_record_count: {result['rehearsal_record_count']}/{result['expected_payload_count']}")
    print(f"ready_rehearsal_count: {result['ready_rehearsal_count']}/{result['runner_count']}")
    print(f"invalid_rehearsal_record_count: {result['invalid_rehearsal_record_count']}")
    print(f"next_gate: {result['next_gate']}")
