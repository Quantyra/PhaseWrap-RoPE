from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from typing import Any

from qrope.stage198_reduced_scope_preregistration import DEFAULT_OUTPUT_DIR as STAGE198_OUTPUT_DIR
from qrope.stage207_reduced_scope_result_collector import DEFAULT_OUTPUT_DIR as STAGE207_OUTPUT_DIR
from qrope.stage208_reduced_scope_calibration_validation import DEFAULT_OUTPUT_DIR as STAGE208_OUTPUT_DIR
from qrope.stage99_matched_fixed_width_encoding_packet_freezer import OBJECTIVE, _round_float


STAGE209_SCHEMA_VERSION = "qrope_stage209_reduced_scope_hardware_metric_interpreter_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE198_RESULTS = STAGE198_OUTPUT_DIR / "results.json"
DEFAULT_STAGE207_RESULTS = STAGE207_OUTPUT_DIR / "results.json"
DEFAULT_STAGE208_RESULTS = STAGE208_OUTPUT_DIR / "results.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage209_reduced_scope_hardware_metric_interpreter_100usd"
STAGE207_READY = "REDUCED_SCOPE_RESULT_COUNTS_COLLECTED_READY_FOR_CALIBRATION"
STAGE208_READY = "REDUCED_SCOPE_CALIBRATION_VALIDATED_READY_FOR_METRICS"
PRODUCT_TEMPLATE = "two_ry_product_state_z_readout_v1"
CX_TEMPLATE = "two_ry_cx_parity_z_readout_v1"
ENCODING_FAMILIES: tuple[str, ...] = (
    "phasewrap",
    "rope_like",
    "sinusoidal_like",
    "alibi_like",
    "matched_nonzero_null_control",
)
POSITIONAL_FAMILIES: tuple[str, ...] = ("rope_like", "sinusoidal_like", "alibi_like")
SOURCE_LANE_RE = re.compile(r"^ibm_(?P<template>product|cx)_seed(?P<seed>\d+)_")


def _load_json(path: Path) -> Any | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _logical_key(reported_key: str, bitstring_order: str) -> str:
    if bitstring_order == "q0q1":
        return reported_key
    if bitstring_order == "q1q0":
        return reported_key[::-1]
    raise ValueError(f"unknown bitstring order: {bitstring_order}")


def _logical_counts(counts: dict[str, Any], bitstring_order: str) -> dict[str, int]:
    logical = {"00": 0, "01": 0, "10": 0, "11": 0}
    for key, value in counts.items():
        logical[_logical_key(str(key), bitstring_order)] = logical.get(_logical_key(str(key), bitstring_order), 0) + int(value)
    return logical


def _expectation_z(bit: int, logical_counts: dict[str, int]) -> float:
    total = sum(logical_counts.values())
    if total <= 0:
        return 0.0
    plus = sum(count for key, count in logical_counts.items() if key[bit] == "0")
    minus = total - plus
    return (plus - minus) / total


def _expectation_zz(logical_counts: dict[str, int]) -> float:
    total = sum(logical_counts.values())
    if total <= 0:
        return 0.0
    plus = logical_counts.get("00", 0) + logical_counts.get("11", 0)
    minus = total - plus
    return (plus - minus) / total


def _observed_score(circuit_template: str, counts: dict[str, Any], bitstring_order: str) -> tuple[float, dict[str, int]]:
    logical = _logical_counts(counts, bitstring_order)
    z0 = _expectation_z(0, logical)
    if circuit_template == PRODUCT_TEMPLATE:
        z1 = _expectation_z(1, logical)
        return 0.5 + 0.25 * (z0 + z1), logical
    if circuit_template == CX_TEMPLATE:
        zz = _expectation_zz(logical)
        return 0.5 + 0.25 * (z0 + zz), logical
    raise ValueError(f"unknown circuit template: {circuit_template}")


def _slope_retention(ideal: list[float], observed: list[float]) -> float:
    ideal_span = max(ideal) - min(ideal) if ideal else 0.0
    observed_span = max(observed) - min(observed) if observed else 0.0
    return observed_span / ideal_span if ideal_span > 0.0 else 1.0


def _rank_retention(ideal: list[float], observed: list[float]) -> float:
    if len(ideal) < 2:
        return 1.0
    return 1.0 if ideal.index(max(ideal)) == observed.index(max(observed)) else 0.0


def _lane_parts(source_lane_id: str) -> dict[str, str]:
    match = SOURCE_LANE_RE.match(source_lane_id)
    if not match:
        return {"provider_family": "ibm", "template_kind": "", "seed": ""}
    return {"provider_family": "ibm", "template_kind": match.group("template"), "seed": match.group("seed")}


def _metric_record(template: dict[str, Any], bitstring_order: str) -> dict[str, Any]:
    template_name = str(template["circuit_template"])
    row_records = []
    errors: list[float] = []
    normalized: list[float] = []
    ideal_scores: list[float] = []
    observed_scores: list[float] = []
    for row in template.get("raw_counts_by_row", []):
        ideal = float(row["ideal_score"])
        observed, logical = _observed_score(template_name, row.get("counts", {}), bitstring_order)
        exposure = max(1.0e-9, float(row.get("component_exposure", 1.0e-9)))
        error = abs(observed - ideal)
        errors.append(error)
        normalized.append(error / exposure)
        ideal_scores.append(ideal)
        observed_scores.append(observed)
        row_records.append(
            {
                "row_id": row.get("row_id"),
                "ideal_score": _round_float(ideal),
                "observed_score": _round_float(observed),
                "mean_absolute_score_error": _round_float(error),
                "normalized_noise_sensitivity_delta": _round_float(error / exposure),
                "component_exposure": _round_float(exposure),
                "reported_counts": row.get("counts", {}),
                "logical_counts": logical,
            }
        )
    return {
        "packet_id": template.get("packet_id"),
        "provider": template.get("provider"),
        "backend": template.get("backend"),
        "source_lane_id": template.get("source_lane_id"),
        "encoding_family": template.get("encoding_family"),
        "circuit_template": template_name,
        "job_or_task_ids": template.get("job_or_task_ids", []),
        "row_count": len(row_records),
        "shot_counts": [int(template.get("shot_count") or 0)],
        "mean_absolute_score_error": _round_float(sum(errors) / len(errors) if errors else 0.0),
        "normalized_noise_sensitivity_delta": _round_float(sum(normalized) / len(normalized) if normalized else 0.0),
        "slope_retention": _round_float(_slope_retention(ideal_scores, observed_scores)),
        "rank_retention": _round_float(_rank_retention(ideal_scores, observed_scores)),
        "row_records": row_records,
    }


def _packet_templates(stage207: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        template
        for template in stage207.get("collected_templates", [])
        if template.get("template_type") == "reduced_scope_packet_execution_counts"
    ]


def _comparison_summary(metric_records: list[dict[str, Any]], pass_policy: dict[str, Any]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], dict[str, dict[str, Any]]] = {}
    for record in metric_records:
        key = (str(record.get("source_lane_id")), str(record.get("circuit_template")))
        grouped.setdefault(key, {})[str(record.get("encoding_family"))] = record
    summaries = []
    for (source_lane_id, circuit_template), by_family in sorted(grouped.items()):
        phasewrap = by_family.get("phasewrap")
        phase_metric = phasewrap.get("normalized_noise_sensitivity_delta") if phasewrap else None
        positional_metrics = [
            by_family[family]["normalized_noise_sensitivity_delta"]
            for family in POSITIONAL_FAMILIES
            if family in by_family
        ]
        control_metric = by_family.get("matched_nonzero_null_control", {}).get("normalized_noise_sensitivity_delta")
        shot_quantum = 1.0 / min(phasewrap.get("shot_counts", [2048])) if phasewrap else None
        best_positional = min(positional_metrics) if positional_metrics else None
        positional_margin = best_positional - phase_metric if best_positional is not None and phase_metric is not None else None
        control_margin = control_metric - phase_metric if control_metric is not None and phase_metric is not None else None
        positional_quanta = positional_margin / shot_quantum if positional_margin is not None and shot_quantum else None
        control_quanta = control_margin / shot_quantum if control_margin is not None and shot_quantum else None
        stable = bool(
            all(family in by_family for family in ENCODING_FAMILIES)
            and positional_quanta is not None
            and control_quanta is not None
            and positional_quanta >= float(pass_policy["minimum_scaled_best_positional_margin_shot_quanta"])
            and control_quanta >= float(pass_policy["minimum_scaled_matched_null_margin_shot_quanta"])
        )
        lane = _lane_parts(source_lane_id)
        summaries.append(
            {
                "provider_family": lane["provider_family"],
                "seed": lane["seed"],
                "template_kind": lane["template_kind"],
                "source_lane_id": source_lane_id,
                "circuit_template": circuit_template,
                "all_families_present": all(family in by_family for family in ENCODING_FAMILIES),
                "phasewrap_normalized_noise_sensitivity_delta": phase_metric,
                "best_positional_normalized_noise_sensitivity_delta": best_positional,
                "matched_null_control_normalized_noise_sensitivity_delta": control_metric,
                "positional_margin": _round_float(positional_margin) if positional_margin is not None else None,
                "matched_null_control_margin": _round_float(control_margin) if control_margin is not None else None,
                "positional_margin_shot_quanta": round(positional_quanta, 6) if positional_quanta is not None else None,
                "matched_null_control_margin_shot_quanta": round(control_quanta, 6) if control_quanta is not None else None,
                "stable_reduced_scope_hardware_target": stable,
            }
        )
    return summaries


def _candidate_records(summary: list[dict[str, Any]], pass_policy: dict[str, Any]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for record in summary:
        grouped.setdefault(f"{record.get('provider_family')}:{record.get('seed')}", []).append(record)
    records = []
    for seed_pair, group in sorted(grouped.items()):
        stable = [record for record in group if record.get("stable_reduced_scope_hardware_target") is True]
        stable_templates = sorted({str(record.get("circuit_template")) for record in stable})
        records.append(
            {
                "seed_pair": seed_pair,
                "comparison_group_count": len(group),
                "stable_target_count": len(stable),
                "stable_template_count": len(stable_templates),
                "stable_templates": stable_templates,
                "min_positional_margin_shot_quanta": min((float(r["positional_margin_shot_quanta"]) for r in group if r.get("positional_margin_shot_quanta") is not None), default=None),
                "min_matched_null_margin_shot_quanta": min((float(r["matched_null_control_margin_shot_quanta"]) for r in group if r.get("matched_null_control_margin_shot_quanta") is not None), default=None),
                "reduced_scope_hardware_positive": len(stable_templates) >= int(pass_policy["minimum_stable_templates_per_seed_pair"]),
            }
        )
    return records


def run_stage209_reduced_scope_hardware_metric_interpreter(
    *,
    stage198_results_path: Path = DEFAULT_STAGE198_RESULTS,
    stage207_results_path: Path = DEFAULT_STAGE207_RESULTS,
    stage208_results_path: Path = DEFAULT_STAGE208_RESULTS,
) -> dict[str, Any]:
    stage198 = _load_json(stage198_results_path)
    stage207 = _load_json(stage207_results_path)
    stage208 = _load_json(stage208_results_path)
    sources = [(stage198_results_path, stage198), (stage207_results_path, stage207), (stage208_results_path, stage208)]
    missing_sources = [str(path.as_posix()) for path, payload in sources if not isinstance(payload, dict)]
    blockers: list[str] = []
    if missing_sources:
        blockers.append("missing_source_artifacts")
    if isinstance(stage207, dict) and stage207.get("decision") != STAGE207_READY:
        blockers.append("stage207_counts_not_ready")
    if isinstance(stage208, dict) and stage208.get("decision") != STAGE208_READY:
        blockers.append("stage208_calibration_not_ready")
    bitstring_order = stage208.get("inferred_bitstring_order") if isinstance(stage208, dict) else None
    if bitstring_order not in {"q0q1", "q1q0"}:
        blockers.append("bitstring_order_missing")
    boundary = stage198.get("interpretation_boundary", {}) if isinstance(stage198, dict) else {}
    pass_policy = boundary.get("pass_fail_policy", {})
    if not pass_policy:
        blockers.append("pass_policy_missing")
    packet_templates = _packet_templates(stage207) if isinstance(stage207, dict) else []
    if len(packet_templates) != 20:
        blockers.append("packet_template_count_mismatch")
    present_families = sorted({str(template.get("encoding_family")) for template in packet_templates})
    if set(present_families) != set(ENCODING_FAMILIES):
        blockers.append("required_family_set_mismatch")

    metric_records: list[dict[str, Any]] = []
    comparison_summary: list[dict[str, Any]] = []
    candidate_records: list[dict[str, Any]] = []
    reduced_scope_positive = False
    if not blockers:
        metric_records = [_metric_record(template, str(bitstring_order)) for template in packet_templates]
        comparison_summary = _comparison_summary(metric_records, pass_policy)
        candidate_records = _candidate_records(comparison_summary, pass_policy)
        positive_seed_pairs = [record for record in candidate_records if record.get("reduced_scope_hardware_positive") is True]
        reduced_scope_positive = len(positive_seed_pairs) >= int(pass_policy["minimum_stable_seed_pairs"])

    if missing_sources:
        decision = "REDUCED_SCOPE_HARDWARE_METRIC_INTERPRETATION_INCOMPLETE"
    elif blockers:
        decision = "REDUCED_SCOPE_HARDWARE_METRIC_INTERPRETATION_BLOCKED"
    elif reduced_scope_positive:
        decision = "REDUCED_SCOPE_HARDWARE_POSITIVE_PHASEWRAP_ADVANTAGE"
    else:
        decision = "REDUCED_SCOPE_HARDWARE_DOES_NOT_SUPPORT_PHASEWRAP_ADVANTAGE"

    return {
        "schema_version": STAGE209_SCHEMA_VERSION,
        "stage": "stage209_reduced_scope_hardware_metric_interpreter",
        "status": "completed" if not missing_sources else "incomplete",
        "objective": OBJECTIVE,
        "decision": decision,
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "blockers": sorted(set(blockers)),
        "bitstring_order": bitstring_order,
        "hardware_scope_label": boundary.get("hardware_scope_label"),
        "pass_fail_policy": pass_policy,
        "packet_template_count": len(packet_templates),
        "metric_record_count": len(metric_records),
        "comparison_group_count": len(comparison_summary),
        "candidate_group_count": len(candidate_records),
        "reduced_scope_positive_seed_pair_count": sum(1 for record in candidate_records if record.get("reduced_scope_hardware_positive") is True),
        "candidate_records": candidate_records,
        "comparison_summary": comparison_summary,
        "metric_records": metric_records,
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "secret_values_recorded": False,
        "runnable_commands_recorded": False,
        "claim_boundary": {
            "supported": [
                "real IBM ibm_fez reduced-scope hardware metric interpretation under preregistered Stage198 thresholds",
                "calibration-applied bitstring ordering before score computation",
                "2048-shot reduced-precision hardware conclusion only",
            ],
            "excluded": [
                "full 4096-shot evidentiary-run conclusion",
                "post-hoc metric or threshold changes",
                "readout mitigation beyond the preregistered calibration order check",
                "new hardware submission",
            ],
        },
        "next_gate": "Summarize the reduced-scope hardware conclusion and decide whether a full 4096-shot evidentiary run is justified.",
    }


def write_stage209_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_keys = (
        "schema_version", "stage", "status", "objective", "decision", "source_artifacts",
        "missing_source_artifacts", "blockers", "bitstring_order", "hardware_scope_label",
        "pass_fail_policy", "packet_template_count", "metric_record_count", "comparison_group_count",
        "candidate_group_count", "reduced_scope_positive_seed_pair_count", "no_hardware_submission",
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
                "stable_reduced_scope_hardware_target",
            ),
        )
        writer.writeheader()
        for record in result["comparison_summary"]:
            writer.writerow({field: record.get(field) for field in writer.fieldnames})
    return paths


def print_stage209_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"bitstring_order: {result['bitstring_order']}")
    print(f"blockers: {', '.join(result['blockers'])}")
    print(f"comparison_group_count: {result['comparison_group_count']}")
    print(f"reduced_scope_positive_seed_pair_count: {result['reduced_scope_positive_seed_pair_count']}")
    print(f"next_gate: {result['next_gate']}")
