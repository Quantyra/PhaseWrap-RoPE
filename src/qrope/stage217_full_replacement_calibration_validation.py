from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from qrope.stage208_reduced_scope_calibration_validation import (
    BITSTRING_ORDERS,
    MIN_DOMINANT_FRACTION,
    STATES,
    _dominant_count,
    _expected_key,
)
from qrope.stage99_matched_fixed_width_encoding_packet_freezer import OBJECTIVE


STAGE217_SCHEMA_VERSION = "qrope_stage217_full_replacement_calibration_validation_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE216_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage216_full_replacement_merged_result_counts_250usd" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage217_full_replacement_calibration_validation_250usd"
STAGE216_READY = "FULL_REPLACEMENT_ALL_RESULT_COUNTS_MERGED_READY_FOR_CALIBRATION"


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _calibration_template(stage216: dict[str, Any]) -> dict[str, Any] | None:
    for template in stage216.get("collected_templates", []):
        if template.get("template_type") == "replacement_known_state_calibration_counts":
            return template
    return None


def run_stage217_full_replacement_calibration_validation(
    *,
    stage216_results_path: Path = DEFAULT_STAGE216_RESULTS,
    min_dominant_fraction: float = MIN_DOMINANT_FRACTION,
) -> dict[str, Any]:
    stage216 = _load_json(stage216_results_path)
    missing_sources = [] if isinstance(stage216, dict) else [str(stage216_results_path.as_posix())]
    blockers: list[str] = []
    if missing_sources:
        blockers.append("source_artifacts_missing")
    if not (isinstance(stage216, dict) and stage216.get("decision") == STAGE216_READY):
        blockers.append("stage216_counts_not_ready")
    calibration = _calibration_template(stage216) if isinstance(stage216, dict) else None
    if not calibration:
        blockers.append("calibration_template_missing")
    rows = calibration.get("raw_counts_by_state", []) if isinstance(calibration, dict) else []
    if len(rows) != 4:
        blockers.append("calibration_state_count_mismatch")

    order_records = []
    for order in BITSTRING_ORDERS:
        state_records = []
        for row in rows:
            state = str(row.get("state"))
            expected_key = _expected_key(state, order)
            successes, total, fraction, wilson = _dominant_count(row.get("counts", {}), expected_key)
            state_records.append(
                {
                    "order": order,
                    "state": state,
                    "expected_key": expected_key,
                    "dominant_count": successes,
                    "total_count": total,
                    "dominant_fraction": fraction,
                    "wilson95_lower_bound": wilson,
                    "pass": state in STATES and wilson >= min_dominant_fraction,
                }
            )
        order_records.append(
            {
                "order": order,
                "pass": bool(state_records) and all(record["pass"] for record in state_records),
                "pass_count": sum(1 for record in state_records if record["pass"]),
                "minimum_wilson95_lower_bound": min((record["wilson95_lower_bound"] for record in state_records), default=0.0),
                "state_records": state_records,
            }
        )
    passing_orders = [record for record in order_records if record["pass"]]
    inferred_order = passing_orders[0]["order"] if len(passing_orders) == 1 else None
    if not inferred_order:
        blockers.append("unique_bitstring_order_not_validated")
    flat_state_records = [state for order in order_records for state in order["state_records"]]
    if missing_sources:
        decision = "FULL_REPLACEMENT_CALIBRATION_VALIDATION_INCOMPLETE"
    elif not blockers:
        decision = "FULL_REPLACEMENT_CALIBRATION_VALIDATED_READY_FOR_METRICS"
    else:
        decision = "FULL_REPLACEMENT_CALIBRATION_VALIDATION_BLOCKED"
    return {
        "schema_version": STAGE217_SCHEMA_VERSION,
        "stage": "stage217_full_replacement_calibration_validation",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": decision,
        "source_artifacts": [str(stage216_results_path.as_posix())],
        "missing_source_artifacts": missing_sources,
        "blockers": sorted(set(blockers)),
        "stage216_decision": stage216.get("decision") if isinstance(stage216, dict) else None,
        "min_required_wilson95_dominant_fraction": min_dominant_fraction,
        "inferred_bitstring_order": inferred_order,
        "order_records": order_records,
        "state_records": flat_state_records,
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "runnable_commands_recorded": False,
        "claim_boundary": {
            "supported": [
                "full 4096-shot known-state calibration counts validate bitstring order before metric interpretation",
                "Wilson 95% lower-bound guard applied to each calibration state",
            ],
            "excluded": [
                "readout mitigation",
                "robustness or auditability metric interpretation",
                "a noisy-hardware robustness or auditability conclusion",
            ],
        },
        "next_gate": "Apply the inferred bitstring order to full 4096-shot packet counts and compute hardware metrics.",
    }


def write_stage217_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_keys = (
        "schema_version", "stage", "status", "objective", "decision", "source_artifacts",
        "missing_source_artifacts", "blockers", "stage216_decision",
        "min_required_wilson95_dominant_fraction", "inferred_bitstring_order",
        "no_hardware_submission", "provider_credentials_required", "secret_values_recorded",
        "runnable_commands_recorded", "claim_boundary", "next_gate",
    )
    manifest = {key: result[key] for key in manifest_keys}
    manifest["result_path"] = str((output_dir / "results.json").as_posix())
    manifest["summary_csv_path"] = str((output_dir / "summary.csv").as_posix())
    paths = {"manifest": str(output_dir / "manifest.json"), "result": str(output_dir / "results.json"), "summary_csv": str(output_dir / "summary.csv")}
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=("order", "state", "expected_key", "dominant_count", "total_count", "dominant_fraction", "wilson95_lower_bound", "pass"),
        )
        writer.writeheader()
        for record in result["state_records"]:
            writer.writerow({field: record.get(field) for field in writer.fieldnames})
    return paths


def print_stage217_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"inferred_bitstring_order: {result['inferred_bitstring_order']}")
    print(f"blockers: {', '.join(result['blockers'])}")
    print(f"next_gate: {result['next_gate']}")
