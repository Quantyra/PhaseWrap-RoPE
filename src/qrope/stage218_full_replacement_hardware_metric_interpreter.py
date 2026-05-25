from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from qrope.stage209_reduced_scope_hardware_metric_interpreter import (
    ENCODING_FAMILIES,
    _candidate_records,
    _comparison_summary,
    _metric_record,
)
from qrope.stage99_matched_fixed_width_encoding_packet_freezer import OBJECTIVE


STAGE218_SCHEMA_VERSION = "qrope_stage218_full_replacement_hardware_metric_interpreter_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE216_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage216_full_replacement_merged_result_counts_250usd" / "results.json"
DEFAULT_STAGE217_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage217_full_replacement_calibration_validation_250usd" / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage218_full_replacement_hardware_metric_interpreter_250usd"
STAGE216_READY = "FULL_REPLACEMENT_ALL_RESULT_COUNTS_MERGED_READY_FOR_CALIBRATION"
STAGE217_READY = "FULL_REPLACEMENT_CALIBRATION_VALIDATED_READY_FOR_METRICS"
FULL_REPLACEMENT_PASS_POLICY = {
    "minimum_stable_seed_pairs": 2,
    "minimum_stable_templates_per_seed_pair": 2,
    "minimum_scaled_best_positional_margin_shot_quanta": 2.0,
    "minimum_scaled_matched_null_margin_shot_quanta": 2.0,
    "scope_note": "Full 4096-shot Stage188 replacement run uses the same predeclared margin thresholds as the reduced-scope run, with 4096-shot shot-quanta scaling.",
}


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _packet_templates(stage216: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        template
        for template in stage216.get("collected_templates", [])
        if template.get("template_type") == "replacement_packet_execution_counts"
    ]


def _full_comparison_summary(metric_records: list[dict[str, Any]], policy: dict[str, Any]) -> list[dict[str, Any]]:
    records = _comparison_summary(metric_records, policy)
    for record in records:
        record["stable_full_replacement_hardware_target"] = record.pop("stable_reduced_scope_hardware_target")
    return records


def _full_candidate_records(comparison_summary: list[dict[str, Any]], policy: dict[str, Any]) -> list[dict[str, Any]]:
    reduced_shape_records = []
    for record in comparison_summary:
        normalized = dict(record)
        normalized["stable_reduced_scope_hardware_target"] = normalized["stable_full_replacement_hardware_target"]
        reduced_shape_records.append(normalized)
    candidates = _candidate_records(reduced_shape_records, policy)
    for record in candidates:
        record["full_replacement_hardware_positive"] = record.pop("reduced_scope_hardware_positive")
    return candidates


def run_stage218_full_replacement_hardware_metric_interpreter(
    *,
    stage216_results_path: Path = DEFAULT_STAGE216_RESULTS,
    stage217_results_path: Path = DEFAULT_STAGE217_RESULTS,
    pass_policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    stage216 = _load_json(stage216_results_path)
    stage217 = _load_json(stage217_results_path)
    policy = pass_policy or FULL_REPLACEMENT_PASS_POLICY
    sources = [(stage216_results_path, stage216), (stage217_results_path, stage217)]
    missing_sources = [str(path.as_posix()) for path, payload in sources if not isinstance(payload, dict)]
    blockers: list[str] = []
    if missing_sources:
        blockers.append("missing_source_artifacts")
    if isinstance(stage216, dict) and stage216.get("decision") != STAGE216_READY:
        blockers.append("stage216_counts_not_ready")
    if isinstance(stage217, dict) and stage217.get("decision") != STAGE217_READY:
        blockers.append("stage217_calibration_not_ready")
    bitstring_order = stage217.get("inferred_bitstring_order") if isinstance(stage217, dict) else None
    if bitstring_order not in {"q0q1", "q1q0"}:
        blockers.append("bitstring_order_missing")
    packet_templates = _packet_templates(stage216) if isinstance(stage216, dict) else []
    if len(packet_templates) != 20:
        blockers.append("packet_template_count_mismatch")
    present_families = sorted({str(template.get("encoding_family")) for template in packet_templates})
    if set(present_families) != set(ENCODING_FAMILIES):
        blockers.append("required_family_set_mismatch")

    metric_records: list[dict[str, Any]] = []
    comparison_summary: list[dict[str, Any]] = []
    candidate_records: list[dict[str, Any]] = []
    full_replacement_positive = False
    if not blockers:
        metric_records = [_metric_record(template, str(bitstring_order)) for template in packet_templates]
        comparison_summary = _full_comparison_summary(metric_records, policy)
        candidate_records = _full_candidate_records(comparison_summary, policy)
        positive_seed_pairs = [record for record in candidate_records if record.get("full_replacement_hardware_positive") is True]
        full_replacement_positive = len(positive_seed_pairs) >= int(policy["minimum_stable_seed_pairs"])

    if missing_sources:
        decision = "FULL_REPLACEMENT_HARDWARE_METRIC_INTERPRETATION_INCOMPLETE"
    elif blockers:
        decision = "FULL_REPLACEMENT_HARDWARE_METRIC_INTERPRETATION_BLOCKED"
    elif full_replacement_positive:
        decision = "FULL_REPLACEMENT_HARDWARE_POSITIVE_PHASEWRAP_ADVANTAGE"
    else:
        decision = "FULL_REPLACEMENT_HARDWARE_DOES_NOT_SUPPORT_PHASEWRAP_ADVANTAGE"

    return {
        "schema_version": STAGE218_SCHEMA_VERSION,
        "stage": "stage218_full_replacement_hardware_metric_interpreter",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": decision,
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "blockers": sorted(set(blockers)),
        "bitstring_order": bitstring_order,
        "hardware_scope_label": "full_replacement_all_lanes_4096_shots_v1",
        "pass_fail_policy": policy,
        "packet_template_count": len(packet_templates),
        "metric_record_count": len(metric_records),
        "comparison_group_count": len(comparison_summary),
        "candidate_group_count": len(candidate_records),
        "full_replacement_positive_seed_pair_count": sum(1 for record in candidate_records if record.get("full_replacement_hardware_positive") is True),
        "candidate_records": candidate_records,
        "comparison_summary": comparison_summary,
        "metric_records": metric_records,
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "runnable_commands_recorded": False,
        "claim_boundary": {
            "supported": [
                "real IBM ibm_fez full 4096-shot replacement hardware metric interpretation under fixed margin thresholds",
                "calibration-applied bitstring ordering before score computation",
                "full packet evidence across product-state and CX templates, two seeds, and five encoding families",
            ],
            "excluded": [
                "post-hoc threshold changes",
                "readout mitigation beyond the calibration order check",
                "production transformer performance",
                "general cross-backend hardware robustness",
                "quantum advantage",
            ],
        },
        "next_gate": "Update the manuscript with the full-run calibration, metric interpretation, and bounded claim conclusion.",
    }


def write_stage218_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_keys = (
        "schema_version", "stage", "status", "objective", "decision", "source_artifacts",
        "missing_source_artifacts", "blockers", "bitstring_order", "hardware_scope_label",
        "pass_fail_policy", "packet_template_count", "metric_record_count", "comparison_group_count",
        "candidate_group_count", "full_replacement_positive_seed_pair_count", "no_hardware_submission",
        "provider_credentials_required", "secret_values_recorded", "runnable_commands_recorded",
        "claim_boundary", "next_gate",
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
            fieldnames=(
                "source_lane_id",
                "circuit_template",
                "phasewrap_normalized_noise_sensitivity_delta",
                "best_positional_normalized_noise_sensitivity_delta",
                "matched_null_control_normalized_noise_sensitivity_delta",
                "positional_margin_shot_quanta",
                "matched_null_control_margin_shot_quanta",
                "stable_full_replacement_hardware_target",
            ),
        )
        writer.writeheader()
        for record in result["comparison_summary"]:
            writer.writerow({field: record.get(field) for field in writer.fieldnames})
    return paths


def print_stage218_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"bitstring_order: {result['bitstring_order']}")
    print(f"blockers: {', '.join(result['blockers'])}")
    print(f"comparison_group_count: {result['comparison_group_count']}")
    print(f"full_replacement_positive_seed_pair_count: {result['full_replacement_positive_seed_pair_count']}")
    print(f"next_gate: {result['next_gate']}")
