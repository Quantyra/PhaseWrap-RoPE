from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


STAGE115_SCHEMA_VERSION = "qrope_stage115_provider_result_collector_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE114_MANIFEST = DEFAULT_ARTIFACT_ROOT / "stage114_provider_result_capture_contract" / "manifest.json"
DEFAULT_STAGE114_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage114_provider_result_capture_contract"
DEFAULT_STAGE113_PROVIDER_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage113_job_result_evidence_assembler" / "provider_job_results.jsonl"
DEFAULT_STAGE152_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage152_first_provider_live_execution_guard" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage115_provider_result_collector"
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


def _counts_present(counts: Any) -> bool:
    if not isinstance(counts, dict) or not counts:
        return False
    try:
        return sum(int(value) for value in counts.values()) > 0
    except (TypeError, ValueError):
        return False


def _job_ids(path: Path) -> set[str]:
    records = _load_jsonl(path) or []
    return {str(record.get("job_id")) for record in records if record.get("job_id")}


def _validate_result_record(record: dict[str, Any], expected_ids: set[str]) -> list[str]:
    missing = []
    for field in ("job_id", "job_or_task_id", "backend_metadata", "submitted_at_utc", "completed_at_utc", "counts"):
        if field not in record or record.get(field) in (None, "", []):
            missing.append(field)
    if record.get("job_id") not in expected_ids:
        missing.append("unknown_job_id")
    if not _counts_present(record.get("counts")):
        missing.append("counts")
    return sorted(set(missing))


def _shard_records(stage114_manifest: dict[str, Any] | None, stage114_output_dir: Path) -> list[dict[str, Any]]:
    if not stage114_manifest:
        return []
    records = []
    for shard_path_text in stage114_manifest.get("job_shard_paths", []):
        shard_path = Path(str(shard_path_text))
        try:
            relative = shard_path.relative_to(stage114_output_dir)
        except ValueError:
            relative = shard_path
        parts = relative.parts
        provider = parts[1] if len(parts) >= 4 and parts[0] == "job_shards" else ""
        window_id = parts[2] if len(parts) >= 4 and parts[0] == "job_shards" else shard_path.parent.name
        result_path = stage114_output_dir / "provider_results" / provider / window_id / "provider_job_results.jsonl"
        records.append(
            {
                "provider": provider,
                "window_id": window_id,
                "job_shard_path": str(shard_path.as_posix()),
                "result_path": str(result_path.as_posix()),
            }
        )
    return records


def _validate_shard(record: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    shard_path = Path(str(record["job_shard_path"]))
    result_path = Path(str(record["result_path"]))
    expected_ids = _job_ids(shard_path)
    results = _load_jsonl(result_path)
    result_records: list[dict[str, Any]] = []
    missing = []
    if results is None:
        missing.append("provider_result_file_missing")
        results = []
    seen: set[str] = set()
    duplicate_ids: set[str] = set()
    ready_count = 0
    for result in results:
        job_id = str(result.get("job_id"))
        if job_id in seen:
            duplicate_ids.add(job_id)
        seen.add(job_id)
        problems = _validate_result_record(result, expected_ids)
        if problems:
            result_records.append({"job_id": job_id, "result_path": str(result_path.as_posix()), "missing_evidence": problems, "ready": False})
        else:
            ready_count += 1
    for duplicate_id in sorted(duplicate_ids):
        result_records.append({"job_id": duplicate_id, "result_path": str(result_path.as_posix()), "missing_evidence": ["duplicate_job_id"], "ready": False})
    missing_ids = sorted(expected_ids - seen)
    if missing_ids:
        missing.append("job_results_missing")
    unknown_count = sum(1 for result in results if str(result.get("job_id")) not in expected_ids)
    ready = bool(expected_ids) and len(missing_ids) == 0 and not duplicate_ids and unknown_count == 0 and ready_count == len(expected_ids)
    shard_summary = {
        **record,
        "expected_job_count": len(expected_ids),
        "result_record_count": len(results),
        "ready_result_count": ready_count,
        "missing_job_count": len(missing_ids),
        "duplicate_job_count": len(duplicate_ids),
        "unknown_job_count": unknown_count,
        "missing_evidence": sorted(set(missing)),
        "ready": ready,
    }
    return shard_summary, result_records


def _stage152_write_ready(stage152: dict[str, Any] | None, selected_providers: set[str]) -> tuple[bool, list[str]]:
    if not selected_providers:
        return False, ["selected_provider_missing"]
    if not isinstance(stage152, dict):
        return False, ["stage152_live_execution_guard_missing"]
    first_provider = str(stage152.get("first_unlock_provider", ""))
    if first_provider and first_provider not in selected_providers:
        return True, []
    blockers = []
    if stage152.get("decision") != "FIRST_PROVIDER_LIVE_EXECUTION_GUARD_READY_FOR_GUARDED_RUNNER":
        blockers.append("stage152_live_execution_guard_not_ready")
    if stage152.get("missing_source_artifacts"):
        blockers.append("stage152_missing_source_artifacts")
    if stage152.get("blockers"):
        blockers.append("stage152_blockers_present")
    if stage152.get("stage144_ready_for_authorized_runner") is not True:
        blockers.append("stage152_stage144_not_ready")
    if stage152.get("stage144_first_blocked_transition") not in (None, "", {}):
        blockers.append("stage152_stage144_blocked_transition_present")
    stage144_ready_transition_count = int(stage152.get("stage144_ready_transition_count") or 0)
    stage144_transition_count = int(stage152.get("stage144_transition_count") or 0)
    if stage144_transition_count <= 0 or stage144_ready_transition_count != stage144_transition_count:
        blockers.append("stage152_stage144_transition_counts_incomplete")
    if stage152.get("stage151_metadata_guard_ready") is not True:
        blockers.append("stage152_stage151_metadata_guard_not_ready")
    runner_count = int(stage152.get("first_provider_runner_command_count") or 0)
    authorized_runner_count = int(stage152.get("first_provider_authorized_runner_count") or 0)
    live_submit_ready_count = int(stage152.get("first_provider_live_submit_ready_count") or 0)
    if first_provider and authorized_runner_count <= 0:
        blockers.append("stage152_no_authorized_first_provider_runner")
    if first_provider and runner_count <= 0:
        blockers.append("stage152_first_provider_runner_commands_missing")
    if first_provider and stage152.get("all_first_provider_commands_authorized") is not True:
        blockers.append("stage152_not_all_first_provider_commands_authorized")
    if first_provider and stage152.get("all_first_provider_commands_live_submit_ready") is not True:
        blockers.append("stage152_not_all_first_provider_commands_live_submit_ready")
    if first_provider and runner_count > 0 and authorized_runner_count != runner_count:
        blockers.append("stage152_authorized_runner_count_incomplete")
    if first_provider and runner_count > 0 and live_submit_ready_count != runner_count:
        blockers.append("stage152_live_submit_ready_count_incomplete")
    return not blockers, sorted(set(blockers))


def run_stage115_collector(
    *,
    stage114_manifest_path: Path = DEFAULT_STAGE114_MANIFEST,
    stage114_output_dir: Path = DEFAULT_STAGE114_OUTPUT_DIR,
    stage113_provider_results_path: Path = DEFAULT_STAGE113_PROVIDER_RESULTS,
    stage152_results_path: Path = DEFAULT_STAGE152_RESULTS,
    write_stage113_input: bool = False,
    provider: str | None = None,
) -> dict[str, Any]:
    stage114 = _load_json(stage114_manifest_path)
    stage152 = _load_json(stage152_results_path)
    missing_sources = [] if isinstance(stage114, dict) else [str(stage114_manifest_path.as_posix())]
    shard_summaries = []
    invalid_records = []
    all_shard_records = _shard_records(stage114, stage114_output_dir)
    selected_shard_records = [
        record for record in all_shard_records if provider is None or record.get("provider") == provider
    ]
    for shard_record in selected_shard_records:
        summary, records = _validate_shard(shard_record)
        shard_summaries.append(summary)
        invalid_records.extend(records)
    ready = bool(shard_summaries) and all(record["ready"] for record in shard_summaries) and not missing_sources
    selected_providers = {str(record.get("provider")) for record in selected_shard_records if record.get("provider")}
    stage152_write_ready, stage152_write_blockers = _stage152_write_ready(stage152, selected_providers)
    wrote_stage113_input = False
    if ready and write_stage113_input and stage152_write_ready:
        stage113_provider_results_path.parent.mkdir(parents=True, exist_ok=True)
        with stage113_provider_results_path.open("w", encoding="utf-8") as handle:
            for shard in shard_summaries:
                for record in _load_jsonl(Path(str(shard["result_path"]))) or []:
                    handle.write(json.dumps(record, sort_keys=True) + "\n")
        wrote_stage113_input = True
    return {
        "schema_version": STAGE115_SCHEMA_VERSION,
        "stage": "stage115_provider_result_collector",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": (
            "PROVIDER_RESULTS_COLLECTED_FOR_STAGE113"
            if wrote_stage113_input
            else "PROVIDER_RESULTS_COLLECTION_BLOCKED_LIVE_GUARD_REQUIRED"
            if ready and write_stage113_input and not stage152_write_ready
            else "PROVIDER_RESULTS_READY_TO_COLLECT"
            if ready
            else "PROVIDER_RESULTS_COLLECTION_BLOCKED_RESULTS_MISSING"
        ),
        "source_artifacts": [str(stage114_manifest_path.as_posix())],
        "missing_source_artifacts": missing_sources,
        "stage114_decision": stage114.get("decision") if isinstance(stage114, dict) else None,
        "stage152_results_path": str(stage152_results_path.as_posix()),
        "stage152_decision": stage152.get("decision") if isinstance(stage152, dict) else None,
        "stage152_missing_source_artifacts": stage152.get("missing_source_artifacts") if isinstance(stage152, dict) else None,
        "stage152_blockers": stage152.get("blockers") if isinstance(stage152, dict) else None,
        "stage152_stage144_ready_for_authorized_runner": (
            stage152.get("stage144_ready_for_authorized_runner") if isinstance(stage152, dict) else None
        ),
        "stage152_stage144_ready_transition_count": (
            stage152.get("stage144_ready_transition_count") if isinstance(stage152, dict) else None
        ),
        "stage152_stage144_transition_count": stage152.get("stage144_transition_count") if isinstance(stage152, dict) else None,
        "stage152_stage144_first_blocked_transition": (
            stage152.get("stage144_first_blocked_transition") if isinstance(stage152, dict) else None
        ),
        "stage152_stage151_metadata_guard_ready": stage152.get("stage151_metadata_guard_ready") if isinstance(stage152, dict) else None,
        "stage152_first_provider_runner_command_count": (
            stage152.get("first_provider_runner_command_count") if isinstance(stage152, dict) else None
        ),
        "stage152_first_provider_authorized_runner_count": (
            stage152.get("first_provider_authorized_runner_count") if isinstance(stage152, dict) else None
        ),
        "stage152_first_provider_live_submit_ready_count": (
            stage152.get("first_provider_live_submit_ready_count") if isinstance(stage152, dict) else None
        ),
        "stage152_all_first_provider_commands_authorized": (
            stage152.get("all_first_provider_commands_authorized") if isinstance(stage152, dict) else None
        ),
        "stage152_all_first_provider_commands_live_submit_ready": (
            stage152.get("all_first_provider_commands_live_submit_ready") if isinstance(stage152, dict) else None
        ),
        "stage152_write_ready": stage152_write_ready,
        "stage152_write_blockers": stage152_write_blockers,
        "provider_scope": provider or "all",
        "write_stage113_input": write_stage113_input,
        "stage113_provider_results_path": str(stage113_provider_results_path.as_posix()),
        "wrote_stage113_input": wrote_stage113_input,
        "shard_count": len(shard_summaries),
        "available_shard_count": len(all_shard_records),
        "ready_shard_count": sum(1 for record in shard_summaries if record["ready"]),
        "expected_job_count": sum(record["expected_job_count"] for record in shard_summaries),
        "result_record_count": sum(record["result_record_count"] for record in shard_summaries),
        "missing_job_count": sum(record["missing_job_count"] for record in shard_summaries),
        "invalid_result_record_count": len(invalid_records),
        "shard_records": shard_summaries,
        "invalid_result_records": invalid_records,
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "claim_boundary": {
            "supported": [
                "validation and collection of Stage 114 provider/window result JSONL shards",
                "optional provider-scoped collection for first-provider execution without requiring other providers first",
                "Stage 113 input writing is blocked until Stage 152 authorizes the first-provider guarded live runner",
                "duplicate, unknown, missing, and empty-count result detection before Stage 113 assembly",
                "optional generation of the single Stage 113 provider_job_results.jsonl input",
            ],
            "excluded": [
                "hardware job submission",
                "provider credentials or secret values",
                "Stage 113 evidence assembly",
                "Stage 101 calibration verification",
                "a noisy-hardware robustness result",
            ],
        },
        "next_gate": (
            "Populate every selected Stage 114 provider result shard after Stage 152 readiness, rerun this collector "
            "with --write-stage113-input, then run Stage 113 with --write-evidence."
        ),
    }


def write_stage115_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "stage114_decision": result["stage114_decision"],
        "stage152_results_path": result["stage152_results_path"],
        "stage152_decision": result["stage152_decision"],
        "stage152_missing_source_artifacts": result["stage152_missing_source_artifacts"],
        "stage152_blockers": result["stage152_blockers"],
        "stage152_stage144_ready_for_authorized_runner": result["stage152_stage144_ready_for_authorized_runner"],
        "stage152_stage144_ready_transition_count": result["stage152_stage144_ready_transition_count"],
        "stage152_stage144_transition_count": result["stage152_stage144_transition_count"],
        "stage152_stage144_first_blocked_transition": result["stage152_stage144_first_blocked_transition"],
        "stage152_stage151_metadata_guard_ready": result["stage152_stage151_metadata_guard_ready"],
        "stage152_first_provider_runner_command_count": result["stage152_first_provider_runner_command_count"],
        "stage152_first_provider_authorized_runner_count": result["stage152_first_provider_authorized_runner_count"],
        "stage152_first_provider_live_submit_ready_count": result["stage152_first_provider_live_submit_ready_count"],
        "stage152_all_first_provider_commands_authorized": result["stage152_all_first_provider_commands_authorized"],
        "stage152_all_first_provider_commands_live_submit_ready": result[
            "stage152_all_first_provider_commands_live_submit_ready"
        ],
        "stage152_write_ready": result["stage152_write_ready"],
        "stage152_write_blockers": result["stage152_write_blockers"],
        "provider_scope": result["provider_scope"],
        "write_stage113_input": result["write_stage113_input"],
        "stage113_provider_results_path": result["stage113_provider_results_path"],
        "wrote_stage113_input": result["wrote_stage113_input"],
        "shard_count": result["shard_count"],
        "available_shard_count": result["available_shard_count"],
        "ready_shard_count": result["ready_shard_count"],
        "expected_job_count": result["expected_job_count"],
        "result_record_count": result["result_record_count"],
        "missing_job_count": result["missing_job_count"],
        "invalid_result_record_count": result["invalid_result_record_count"],
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
            fieldnames=("provider", "window_id", "ready", "expected_job_count", "result_record_count", "ready_result_count", "missing_job_count", "duplicate_job_count", "unknown_job_count", "missing_evidence"),
        )
        writer.writeheader()
        for record in result["shard_records"]:
            writer.writerow(
                {
                    "provider": record["provider"],
                    "window_id": record["window_id"],
                    "ready": record["ready"],
                    "expected_job_count": record["expected_job_count"],
                    "result_record_count": record["result_record_count"],
                    "ready_result_count": record["ready_result_count"],
                    "missing_job_count": record["missing_job_count"],
                    "duplicate_job_count": record["duplicate_job_count"],
                    "unknown_job_count": record["unknown_job_count"],
                    "missing_evidence": "; ".join(record["missing_evidence"]),
                }
            )
    return paths


def print_stage115_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"provider_scope: {result['provider_scope']}")
    print(f"ready_shard_count: {result['ready_shard_count']}/{result['shard_count']}")
    print(f"expected_job_count: {result['expected_job_count']}")
    print(f"result_record_count: {result['result_record_count']}")
    print(f"missing_job_count: {result['missing_job_count']}")
    print(f"stage152_write_ready: {result['stage152_write_ready']}")
    print(f"wrote_stage113_input: {result['wrote_stage113_input']}")
    print(f"next_gate: {result['next_gate']}")
