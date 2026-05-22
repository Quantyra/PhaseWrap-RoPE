from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


STAGE109_SCHEMA_VERSION = "qrope_stage109_window_evidence_intake_validator_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE107_WINDOW_PLANS = DEFAULT_ARTIFACT_ROOT / "stage107_window_execution_orchestrator" / "window_execution_plans.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage109_window_evidence_intake_validator"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _step(plan: dict[str, Any], step_id: str) -> dict[str, Any]:
    for item in plan.get("steps", []):
        if item.get("step_id") == step_id:
            return item
    return {}


def _has_nonempty_counts(counts: Any) -> bool:
    if not isinstance(counts, dict) or not counts:
        return False
    try:
        return sum(int(value) for value in counts.values()) > 0
    except (TypeError, ValueError):
        return False


def _expected_row_ids(packet_template: dict[str, Any]) -> list[str]:
    template_path = Path(str(packet_template.get("template_path", "")))
    template = _load_json(template_path) if str(template_path) else None
    if isinstance(template, dict):
        rows = template.get("raw_counts_by_row", [])
        row_ids = [str(row.get("row_id")) for row in rows if row.get("row_id") is not None]
        if row_ids:
            return row_ids
    row_count = int(packet_template.get("row_count", 0) or 0)
    return [f"hwrow-{index:03d}" for index in range(row_count)]


def _stage101_ready(stage101: dict[str, Any] | None) -> bool:
    return bool(
        stage101
        and stage101.get("known_state_calibration_pass") is True
        and stage101.get("decision") == "KNOWN_STATE_CALIBRATION_VERIFIED_READY_FOR_MATCHED_HARDWARE_EXECUTION"
    )


def _stage103_ready(stage103: dict[str, Any] | None) -> bool:
    return bool(stage103 and stage103.get("ready_to_interpret_hardware_metrics") is True)


def _packet_record(packet_template: dict[str, Any], packet_output_dir: Path) -> dict[str, Any]:
    packet_id = str(packet_template["packet_id"])
    execution_path = packet_output_dir / f"{packet_id}.json"
    execution = _load_json(execution_path)
    missing: list[str] = []
    expected_row_ids = _expected_row_ids(packet_template)
    observed_row_ids: list[str] = []

    if not isinstance(execution, dict):
        missing.append("packet_execution_json")
    else:
        for field in ("job_or_task_ids", "backend_metadata", "submitted_at_utc", "completed_at_utc", "raw_counts_by_row"):
            if field not in execution or execution.get(field) in (None, "", []):
                missing.append(field)
        rows = execution.get("raw_counts_by_row", [])
        if isinstance(rows, list):
            rows_by_id = {str(row.get("row_id")): row for row in rows if isinstance(row, dict) and row.get("row_id") is not None}
            observed_row_ids = sorted(rows_by_id)
            for row_id in expected_row_ids:
                row = rows_by_id.get(row_id)
                if row is None:
                    missing.append(f"raw_counts_by_row.{row_id}")
                elif not _has_nonempty_counts(row.get("counts")):
                    missing.append(f"raw_counts_by_row.{row_id}.counts")
        else:
            missing.append("raw_counts_by_row")

    return {
        "packet_id": packet_id,
        "provider": packet_template.get("provider"),
        "encoding_family": packet_template.get("encoding_family"),
        "source_lane_id": packet_template.get("source_lane_id"),
        "circuit_template": packet_template.get("circuit_template"),
        "execution_path": str(execution_path.as_posix()),
        "expected_row_count": len(expected_row_ids),
        "observed_row_count": len(observed_row_ids),
        "missing_evidence": sorted(set(missing)),
        "ready": not missing,
    }


def _window_record(plan: dict[str, Any]) -> dict[str, Any]:
    calibration_step = _step(plan, "known_state_calibration_execution")
    packet_step = _step(plan, "matched_packet_execution")
    calibration_execution_path = Path(str(calibration_step.get("output_path", "")))
    calibration_dir = calibration_execution_path.parent
    stage101_results_path = calibration_dir / "stage101" / "results.json"
    packet_output_dir = Path(str(packet_step.get("output_dir", "")))
    stage103_results_path = packet_output_dir.parent / "stage103" / "results.json"

    calibration_execution = _load_json(calibration_execution_path) if str(calibration_execution_path) else None
    stage101 = _load_json(stage101_results_path)
    stage103 = _load_json(stage103_results_path)
    packet_records = [_packet_record(packet, packet_output_dir) for packet in packet_step.get("packet_templates", [])]

    missing: list[str] = []
    if not isinstance(calibration_execution, dict):
        missing.append("calibration_execution_json")
    if not _stage101_ready(stage101):
        missing.append("stage101_results_json")
    if any(not record["ready"] for record in packet_records):
        missing.append("packet_execution_json")
    if not _stage103_ready(stage103):
        missing.append("stage103_results_json")

    return {
        "window_id": plan.get("window_id"),
        "provider": plan.get("provider"),
        "window_index": plan.get("window_index"),
        "calibration_execution_path": str(calibration_execution_path.as_posix()),
        "stage101_results_path": str(stage101_results_path.as_posix()),
        "packet_execution_dir": str(packet_output_dir.as_posix()),
        "stage103_results_path": str(stage103_results_path.as_posix()),
        "expected_packet_count": int(packet_step.get("packet_template_count", len(packet_records)) or 0),
        "ready_packet_count": sum(1 for record in packet_records if record["ready"]),
        "packet_records": packet_records,
        "missing_evidence": sorted(set(missing)),
        "status": "ready_for_aggregation" if not missing else "missing_evidence",
        "ready": not missing,
    }


def run_stage109_intake_validator(
    *,
    stage107_window_plans_path: Path = DEFAULT_STAGE107_WINDOW_PLANS,
) -> dict[str, Any]:
    plans = _load_json(stage107_window_plans_path)
    missing_sources = [] if isinstance(plans, list) else [str(stage107_window_plans_path.as_posix())]
    window_plans = plans if isinstance(plans, list) else []
    window_records = [_window_record(plan) for plan in window_plans]
    ready_window_count = sum(1 for record in window_records if record["ready"])
    missing_evidence_count = sum(len(record["missing_evidence"]) for record in window_records)
    all_ready = bool(window_records) and ready_window_count == len(window_records) and not missing_sources
    return {
        "schema_version": STAGE109_SCHEMA_VERSION,
        "stage": "stage109_window_evidence_intake_validator",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": (
            "WINDOW_EVIDENCE_INTAKE_READY_FOR_STAGE105_AGGREGATION"
            if all_ready
            else "WINDOW_EVIDENCE_INTAKE_BLOCKED_EVIDENCE_MISSING"
        ),
        "source_artifacts": [str(stage107_window_plans_path.as_posix())],
        "missing_source_artifacts": missing_sources,
        "window_count": len(window_records),
        "ready_window_count": ready_window_count,
        "missing_evidence_count": missing_evidence_count,
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "window_records": window_records,
        "claim_boundary": {
            "supported": [
                "a deterministic intake check for filled Stage 107 independent-window evidence",
                "per-window verification that calibration, packet counts, and Stage 103 metric readiness are present",
                "a no-submission guard before any Stage 105 aggregation claim",
            ],
            "excluded": [
                "real hardware submission",
                "provider credential validation",
                "a noisy-hardware robustness result",
                "a replicated PhaseWrap-RoPE advantage claim",
            ],
        },
        "next_gate": (
            "Fill each Stage 107 window with real calibration evidence, Stage 101 pass results, packet execution counts, "
            "and Stage 103 metric outputs; rerun this validator before Stage 105 aggregation."
        ),
    }


def write_stage109_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "window_count": result["window_count"],
        "ready_window_count": result["ready_window_count"],
        "missing_evidence_count": result["missing_evidence_count"],
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
            fieldnames=(
                "window_id",
                "provider",
                "window_index",
                "status",
                "expected_packet_count",
                "ready_packet_count",
                "missing_evidence",
            ),
        )
        writer.writeheader()
        for record in result["window_records"]:
            writer.writerow(
                {
                    "window_id": record["window_id"],
                    "provider": record["provider"],
                    "window_index": record["window_index"],
                    "status": record["status"],
                    "expected_packet_count": record["expected_packet_count"],
                    "ready_packet_count": record["ready_packet_count"],
                    "missing_evidence": "; ".join(record["missing_evidence"]),
                }
            )
    return paths


def print_stage109_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"window_count: {result['window_count']}")
    print(f"ready_window_count: {result['ready_window_count']}")
    print(f"missing_evidence_count: {result['missing_evidence_count']}")
    print(f"next_gate: {result['next_gate']}")
