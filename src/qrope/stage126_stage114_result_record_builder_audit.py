from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from qrope.provider_adapters.common import build_stage114_result_record


STAGE126_SCHEMA_VERSION = "qrope_stage126_stage114_result_record_builder_audit_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE114_SCHEMA = DEFAULT_ARTIFACT_ROOT / "stage114_provider_result_capture_contract" / "provider_job_result_schema.json"
DEFAULT_STAGE123_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage123_provider_submission_plan_audit" / "results.json"
DEFAULT_STAGE125_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage125_provider_result_normalization_audit" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage126_stage114_result_record_builder_audit"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _load_first_jsonl(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            return json.loads(line)
    return None


def _plan_paths(stage123_results_path: Path) -> list[Path]:
    base = stage123_results_path.parent / "submission_plans"
    return sorted(base.glob("*/*/submission_plans.jsonl"))


def _counts_for_provider(provider: str) -> dict[str, int]:
    if provider == "ibm_runtime":
        return {"00": 8, "11": 2}
    return {"01": 4, "10": 6}


def _required_fields(schema: dict[str, Any] | None) -> list[str]:
    return list(schema.get("required_fields", [])) if isinstance(schema, dict) else []


def _record_ready(record: dict[str, Any], required_fields: list[str]) -> list[str]:
    missing = []
    for field in required_fields:
        if field not in record or record.get(field) in (None, "", []):
            missing.append(field)
    counts = record.get("counts")
    if not isinstance(counts, dict) or not counts:
        missing.append("counts")
    else:
        try:
            if sum(int(value) for value in counts.values()) <= 0:
                missing.append("counts")
        except (TypeError, ValueError):
            missing.append("counts")
    return sorted(set(missing))


def _provider_record(plan_path: Path, required_fields: list[str]) -> tuple[dict[str, Any], dict[str, Any] | None]:
    plan = _load_first_jsonl(plan_path)
    missing = []
    result_record = None
    if not plan:
        missing.append("submission_plan_missing")
    else:
        provider = str(plan.get("provider", ""))
        try:
            result_record = build_stage114_result_record(
                plan=plan,
                job_or_task_id=f"DRY_RUN_TASK::{plan.get('job_id')}",
                backend_metadata={"backend": "dry-run-backend", "result_source": "stage126_record_builder_audit_not_hardware"},
                submitted_at_utc="1970-01-01T00:00:00Z",
                completed_at_utc="1970-01-01T00:00:01Z",
                counts=_counts_for_provider(provider),
            )
            missing.extend(_record_ready(result_record, required_fields))
        except Exception as exc:  # noqa: BLE001 - audit reports builder failures.
            missing.append(f"record_builder_failed:{exc}")
    provider = str(plan.get("provider", "")) if plan else plan_path.parts[-3]
    window_id = str(plan.get("window_id", "")) if plan else plan_path.parts[-2]
    return (
        {
            "provider": provider,
            "window_id": window_id,
            "submission_plan_path": str(plan_path.as_posix()),
            "required_fields": required_fields,
            "record_ready": result_record is not None and not missing,
            "missing_evidence": sorted(set(missing)),
            "ready": result_record is not None and not missing,
        },
        result_record,
    )


def run_stage126_audit(
    *,
    stage114_schema_path: Path = DEFAULT_STAGE114_SCHEMA,
    stage123_results_path: Path = DEFAULT_STAGE123_RESULTS,
    stage125_results_path: Path = DEFAULT_STAGE125_RESULTS,
) -> dict[str, Any]:
    schema = _load_json(stage114_schema_path)
    stage123 = _load_json(stage123_results_path)
    stage125 = _load_json(stage125_results_path)
    sources = [(stage114_schema_path, schema), (stage123_results_path, stage123), (stage125_results_path, stage125)]
    missing_sources = [str(path.as_posix()) for path, payload in sources if payload is None]
    required_fields = _required_fields(schema)
    provider_records = []
    built_records: dict[str, dict[str, Any]] = {}
    for plan_path in _plan_paths(stage123_results_path):
        record, result_record = _provider_record(plan_path, required_fields)
        provider_records.append(record)
        if result_record:
            built_records[f"{record['provider']}::{record['window_id']}"] = result_record
    ready = bool(provider_records) and all(record["ready"] for record in provider_records) and not missing_sources
    return {
        "schema_version": STAGE126_SCHEMA_VERSION,
        "stage": "stage126_stage114_result_record_builder_audit",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": (
            "STAGE114_RESULT_RECORD_BUILDER_READY_EXECUTION_BLOCKED"
            if ready
            else "STAGE114_RESULT_RECORD_BUILDER_INCOMPLETE"
        ),
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "stage123_decision": stage123.get("decision") if isinstance(stage123, dict) else None,
        "stage125_decision": stage125.get("decision") if isinstance(stage125, dict) else None,
        "required_result_fields": required_fields,
        "provider_window_count": len(provider_records),
        "ready_provider_window_count": sum(1 for record in provider_records if record["ready"]),
        "provider_records": provider_records,
        "built_records": built_records,
        "no_hardware_submission": True,
        "provider_credentials_required": True,
        "secret_values_recorded": False,
        "claim_boundary": {
            "supported": [
                "normalized provider counts can be assembled into Stage 114-shaped result records",
                "result records include job IDs, provider task IDs, backend metadata, timestamps, and non-empty counts",
                "record assembly remains isolated from real provider result paths before live SDK submission",
            ],
            "excluded": [
                "hardware job submission",
                "provider credentials or secret values",
                "live provider SDK submission",
                "real provider result records",
                "Stage 113 evidence assembly",
                "a noisy-hardware robustness result",
            ],
        },
        "next_gate": (
            "Use the Stage 126 record builder inside live provider SDK submitters so real measured counts become "
            "validated Stage 114 result records only after Stage 106/111 readiness clears."
        ),
    }


def write_stage126_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    built_dir = output_dir / "built_result_records"
    built_paths = []
    for key, record in result["built_records"].items():
        provider, window_id = key.split("::", 1)
        path = built_dir / provider / window_id / "provider_job_result.record_builder_sample.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(record, indent=2, sort_keys=True), encoding="utf-8")
        built_paths.append(str(path.as_posix()))
    result_without_built = {key: value for key, value in result.items() if key != "built_records"}
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "stage123_decision": result["stage123_decision"],
        "stage125_decision": result["stage125_decision"],
        "required_result_fields": result["required_result_fields"],
        "provider_window_count": result["provider_window_count"],
        "ready_provider_window_count": result["ready_provider_window_count"],
        "built_result_record_paths": built_paths,
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
    (output_dir / "results.json").write_text(json.dumps(result_without_built, indent=2, sort_keys=True), encoding="utf-8")
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=("provider", "window_id", "record_ready", "ready", "missing_evidence"),
        )
        writer.writeheader()
        for record in result["provider_records"]:
            writer.writerow(
                {
                    "provider": record["provider"],
                    "window_id": record["window_id"],
                    "record_ready": record["record_ready"],
                    "ready": record["ready"],
                    "missing_evidence": "; ".join(record["missing_evidence"]),
                }
            )
    return paths


def print_stage126_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"ready_provider_window_count: {result['ready_provider_window_count']}/{result['provider_window_count']}")
    print(f"next_gate: {result['next_gate']}")
