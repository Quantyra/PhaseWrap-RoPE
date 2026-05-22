from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Any

from qrope.stage207_reduced_scope_result_collector import DEFAULT_OUTPUT_DIR as STAGE207_OUTPUT_DIR
from qrope.stage99_matched_fixed_width_encoding_packet_freezer import OBJECTIVE


STAGE208_SCHEMA_VERSION = "qrope_stage208_reduced_scope_calibration_validation_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE207_RESULTS = STAGE207_OUTPUT_DIR / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage208_reduced_scope_calibration_validation_100usd"
STAGE207_READY = "REDUCED_SCOPE_RESULT_COUNTS_COLLECTED_READY_FOR_CALIBRATION"
STATES: tuple[str, ...] = ("00", "01", "10", "11")
BITSTRING_ORDERS: tuple[str, ...] = ("q0q1", "q1q0")
MIN_DOMINANT_FRACTION = 0.80
Z_95 = 1.96


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _wilson_lower_bound(successes: int, total: int, z: float = Z_95) -> float:
    if total <= 0:
        return 0.0
    phat = float(successes) / float(total)
    z2 = z * z
    denominator = 1.0 + z2 / total
    center = phat + z2 / (2.0 * total)
    spread = z * math.sqrt((phat * (1.0 - phat) / total) + (z2 / (4.0 * total * total)))
    return (center - spread) / denominator


def _expected_key(state: str, order: str) -> str:
    if order == "q0q1":
        return state
    if order == "q1q0":
        return state[::-1]
    raise ValueError(f"unknown bitstring order: {order}")


def _calibration_template(stage207: dict[str, Any]) -> dict[str, Any] | None:
    for template in stage207.get("collected_templates", []):
        if template.get("template_type") == "reduced_scope_known_state_calibration_counts":
            return template
    return None


def _dominant_count(counts: dict[str, Any], expected_key: str) -> tuple[int, int, float, float]:
    total = sum(int(value) for value in counts.values())
    successes = int(counts.get(expected_key, 0))
    fraction = float(successes) / float(total) if total else 0.0
    return successes, total, fraction, _wilson_lower_bound(successes, total)


def run_stage208_reduced_scope_calibration_validation(
    *,
    stage207_results_path: Path = DEFAULT_STAGE207_RESULTS,
    min_dominant_fraction: float = MIN_DOMINANT_FRACTION,
) -> dict[str, Any]:
    stage207 = _load_json(stage207_results_path)
    missing_sources = [] if isinstance(stage207, dict) else [str(stage207_results_path.as_posix())]
    blockers: list[str] = []
    if missing_sources:
        blockers.append("source_artifacts_missing")
    stage207_ready = bool(isinstance(stage207, dict) and stage207.get("decision") == STAGE207_READY)
    if not stage207_ready:
        blockers.append("stage207_counts_not_ready")
    calibration = _calibration_template(stage207) if isinstance(stage207, dict) else None
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
        decision = "REDUCED_SCOPE_CALIBRATION_VALIDATION_INCOMPLETE"
    elif not blockers:
        decision = "REDUCED_SCOPE_CALIBRATION_VALIDATED_READY_FOR_METRICS"
    else:
        decision = "REDUCED_SCOPE_CALIBRATION_VALIDATION_BLOCKED"
    return {
        "schema_version": STAGE208_SCHEMA_VERSION,
        "stage": "stage208_reduced_scope_calibration_validation",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": decision,
        "source_artifacts": [str(stage207_results_path.as_posix())],
        "missing_source_artifacts": missing_sources,
        "blockers": sorted(set(blockers)),
        "stage207_decision": stage207.get("decision") if isinstance(stage207, dict) else None,
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
                "real reduced-scope known-state calibration counts validate bitstring order before metric interpretation",
                "Wilson 95% lower-bound guard applied to each calibration state",
            ],
            "excluded": [
                "readout mitigation",
                "robustness or auditability metric interpretation",
                "a noisy-hardware robustness or auditability conclusion",
            ],
        },
        "next_gate": "Apply the inferred bitstring order to packet counts and compute reduced-scope hardware robustness and auditability metrics.",
    }


def write_stage208_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_keys = (
        "schema_version", "stage", "status", "objective", "decision", "source_artifacts",
        "missing_source_artifacts", "blockers", "stage207_decision",
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


def print_stage208_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"inferred_bitstring_order: {result['inferred_bitstring_order']}")
    print(f"blockers: {', '.join(result['blockers'])}")
    print(f"next_gate: {result['next_gate']}")
