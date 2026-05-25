from __future__ import annotations

import csv
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


STAGE216_SCHEMA_VERSION = "qrope_stage216_full_replacement_merged_result_counts_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_ORIGINAL_STAGE214_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage214_full_replacement_result_collector_250usd" / "results.json"
DEFAULT_REPLACEMENT_STAGE214_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage214_full_replacement_result_collector_after_stage215_250usd" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage216_full_replacement_merged_result_counts_250usd"


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _template_key(template: dict[str, Any]) -> str:
    return str(template.get("packet_id") or "__calibration__")


def _record_source_label(index: int) -> str:
    return "stage214_original_13" if index == 0 else "stage214_stage215_replacement_8"


def run_stage216_full_replacement_merged_result_counts(
    *,
    original_stage214_results_path: Path = DEFAULT_ORIGINAL_STAGE214_RESULTS,
    replacement_stage214_results_path: Path = DEFAULT_REPLACEMENT_STAGE214_RESULTS,
) -> dict[str, Any]:
    sources = [
        (original_stage214_results_path, _load_json(original_stage214_results_path)),
        (replacement_stage214_results_path, _load_json(replacement_stage214_results_path)),
    ]
    missing_sources = [str(path.as_posix()) for path, payload in sources if not isinstance(payload, dict)]
    blockers: list[str] = []
    if missing_sources:
        blockers.append("source_artifacts_missing")
    merged: dict[str, dict[str, Any]] = {}
    records: list[dict[str, Any]] = []
    for index, (_, payload) in enumerate(sources):
        if not isinstance(payload, dict):
            continue
        source_label = _record_source_label(index)
        for template in payload.get("collected_templates", []):
            if isinstance(template, dict):
                merged[_template_key(template)] = template
        for record in payload.get("collection_records", []):
            if isinstance(record, dict) and record.get("counts_recorded"):
                annotated = dict(record)
                annotated["source_collection_artifact"] = source_label
                records.append(annotated)
    if len(merged) != 21:
        blockers.append("merged_template_count_mismatch")
    decision = "FULL_REPLACEMENT_ALL_RESULT_COUNTS_MERGED_READY_FOR_CALIBRATION" if not blockers else "FULL_REPLACEMENT_MERGED_RESULT_COUNTS_INCOMPLETE"
    return {
        "schema_version": STAGE216_SCHEMA_VERSION,
        "stage": "stage216_full_replacement_merged_result_counts",
        "status": "completed" if not missing_sources else "incomplete",
        "decision": decision,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "blockers": sorted(set(blockers)),
        "expected_template_count": 21,
        "merged_template_count": len(merged),
        "collection_records": records,
        "collected_templates": [merged[key] for key in sorted(merged)],
        "secret_values_recorded": False,
        "claim_boundary": {
            "supported": ["merged provider result-count collection for all full replacement templates across the original and allocated IBM instances"],
            "excluded": ["calibration pass/fail", "robustness or auditability interpretation"],
        },
        "next_gate": "Validate known-state calibration before computing full 4096-shot hardware metrics.",
    }


def write_stage216_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_keys = (
        "schema_version", "stage", "status", "decision", "source_artifacts",
        "missing_source_artifacts", "blockers", "expected_template_count", "merged_template_count",
        "secret_values_recorded", "claim_boundary", "next_gate",
    )
    manifest = {key: result[key] for key in manifest_keys}
    manifest["result_path"] = str((output_dir / "results.json").as_posix())
    manifest["summary_csv_path"] = str((output_dir / "summary.csv").as_posix())
    paths = {"manifest": str(output_dir / "manifest.json"), "result": str(output_dir / "results.json"), "summary_csv": str(output_dir / "summary.csv")}
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=("packet_id", "runtime_job_id", "status", "source_collection_artifact"))
        writer.writeheader()
        for record in result["collection_records"]:
            writer.writerow({field: record.get(field, "") for field in writer.fieldnames})
    return paths


def print_stage216_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"merged_template_count: {result['merged_template_count']}/{result['expected_template_count']}")
    print(f"blockers: {', '.join(result['blockers'])}")
    print(f"next_gate: {result['next_gate']}")
