from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Any


STAGE103_SCHEMA_VERSION = "qrope_stage103_robustness_metric_preregistration_v1"
DEFAULT_ARTIFACT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_STAGE99_MANIFEST = DEFAULT_ARTIFACT_ROOT / "stage99_matched_fixed_width_encoding_packets" / "manifest.json"
DEFAULT_STAGE100_MANIFEST = DEFAULT_ARTIFACT_ROOT / "stage100_matched_cx_encoding_packets" / "manifest.json"
DEFAULT_STAGE101_RESULTS = DEFAULT_ARTIFACT_ROOT / "stage101_known_state_calibration_gate" / "results.json"
DEFAULT_STAGE102_MANIFEST = DEFAULT_ARTIFACT_ROOT / "stage102_calibration_execution_package" / "manifest.json"
DEFAULT_OUTPUT_DIR = DEFAULT_ARTIFACT_ROOT / "stage103_robustness_metric_preregistration"
OBJECTIVE = (
    "Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or "
    "auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, "
    "under fixed circuit width."
)
ENCODING_FAMILIES: tuple[str, ...] = (
    "phasewrap",
    "rope_like",
    "sinusoidal_like",
    "alibi_like",
    "no_position_control",
)
COMPARATOR_FAMILIES: tuple[str, ...] = (
    "rope_like",
    "sinusoidal_like",
    "alibi_like",
    "no_position_control",
)
REQUIRED_EXECUTION_FIELDS: tuple[str, ...] = (
    "job_or_task_ids",
    "backend_metadata",
    "submitted_at_utc",
    "completed_at_utc",
    "raw_counts_by_row",
)


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _bit_value(bit: str) -> int:
    return 1 if bit == "0" else -1


def expectation_from_counts(counts: dict[str, int], observable: str) -> float:
    total = sum(int(value) for value in counts.values())
    if total <= 0:
        raise ValueError("counts must contain at least one shot")
    observed = 0.0
    for key, value in counts.items():
        bits = str(key)
        if len(bits) != 2:
            raise ValueError(f"expected two-bit canonical q0q1 key, got {bits!r}")
        z0 = _bit_value(bits[0])
        z1 = _bit_value(bits[1])
        if observable == "z0":
            term = z0
        elif observable == "z1":
            term = z1
        elif observable == "z0z1":
            term = z0 * z1
        else:
            raise ValueError(f"unknown observable: {observable}")
        observed += float(term * int(value))
    return observed / float(total)


def score_from_counts(counts: dict[str, int], circuit_template: str) -> float:
    z0 = expectation_from_counts(counts, "z0")
    if circuit_template == "two_ry_product_state_z_readout_v1":
        z1_or_parity = expectation_from_counts(counts, "z1")
    elif circuit_template == "two_ry_cx_parity_z_readout_v1":
        z1_or_parity = expectation_from_counts(counts, "z0z1")
    else:
        raise ValueError(f"unsupported circuit template: {circuit_template}")
    return 0.5 + 0.25 * (z0 + z1_or_parity)


def _spearman(xs: list[float], ys: list[float]) -> float | None:
    if len(xs) != len(ys) or len(xs) < 2:
        return None
    rx = _average_ranks(xs)
    ry = _average_ranks(ys)
    return _pearson(rx, ry)


def _average_ranks(values: list[float]) -> list[float]:
    indexed = sorted(enumerate(values), key=lambda item: item[1])
    ranks = [0.0] * len(values)
    index = 0
    while index < len(indexed):
        end = index + 1
        while end < len(indexed) and indexed[end][1] == indexed[index][1]:
            end += 1
        rank = (index + 1 + end) / 2.0
        for original_index, _ in indexed[index:end]:
            ranks[original_index] = rank
        index = end
    return ranks


def _pearson(xs: list[float], ys: list[float]) -> float | None:
    mean_x = sum(xs) / len(xs)
    mean_y = sum(ys) / len(ys)
    dx = [value - mean_x for value in xs]
    dy = [value - mean_y for value in ys]
    denom = math.sqrt(sum(value * value for value in dx) * sum(value * value for value in dy))
    if denom == 0.0:
        return None
    return sum(left * right for left, right in zip(dx, dy)) / denom


def _round(value: float | None) -> float | None:
    if value is None:
        return None
    return round(float(value), 12)


def packet_metrics(packet: dict[str, Any], execution: dict[str, Any]) -> dict[str, Any]:
    counts_by_row = {
        str(item.get("row_id")): {str(key): int(value) for key, value in item.get("counts", {}).items()}
        for item in execution.get("raw_counts_by_row", [])
    }
    template = str(packet["fixed_width"]["circuit_template"])
    rows = packet.get("rows", [])
    observed: list[float] = []
    ideal: list[float] = []
    missing_rows: list[str] = []
    total_shots: list[int] = []
    for row in rows:
        row_id = str(row["row_id"])
        counts = counts_by_row.get(row_id)
        if counts is None:
            missing_rows.append(row_id)
            continue
        observed_score = score_from_counts(counts, template)
        ideal_score = float(row["ideal_predictions"]["score"])
        observed.append(observed_score)
        ideal.append(ideal_score)
        total_shots.append(sum(int(value) for value in counts.values()))
    errors = [abs(left - right) for left, right in zip(observed, ideal)]
    squared = [(left - right) ** 2 for left, right in zip(observed, ideal)]
    top1_match = None
    if observed and ideal:
        top1_match = observed.index(max(observed)) == ideal.index(max(ideal))
    return {
        "packet_id": packet["packet_id"],
        "provider": packet.get("provider"),
        "source_lane_id": packet.get("source_lane_id"),
        "encoding_family": packet.get("encoding_family"),
        "circuit_template": template,
        "row_count": len(rows),
        "observed_row_count": len(observed),
        "missing_rows": missing_rows,
        "coverage_fraction": _round(len(observed) / len(rows) if rows else 0.0),
        "mean_absolute_score_error": _round(sum(errors) / len(errors) if errors else None),
        "root_mean_squared_score_error": _round(math.sqrt(sum(squared) / len(squared)) if squared else None),
        "spearman_rank_correlation": _round(_spearman(ideal, observed)),
        "top1_match": top1_match,
        "shot_counts": sorted(set(total_shots)),
    }


def _packet_paths_from_manifest(manifest: dict[str, Any] | None) -> list[Path]:
    if not manifest:
        return []
    return [Path(str(path)) for path in manifest.get("packet_paths", [])]


def _execution_for_packet(execution_dir: Path | None, packet_id: str) -> dict[str, Any] | None:
    if execution_dir is None:
        return None
    return _load_json(execution_dir / f"{packet_id}.json")


def _assembled_from_stage113(execution: dict[str, Any]) -> bool:
    return execution.get("status") == "assembled_from_stage113_results" and execution.get("no_hardware_submission") is False


def _metrics_records(packet_paths: list[Path], execution_dir: Path | None) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    records: list[dict[str, Any]] = []
    missing_execution: list[dict[str, Any]] = []
    for packet_path in packet_paths:
        packet = _load_json(packet_path)
        if packet is None:
            missing_execution.append({"packet_path": str(packet_path.as_posix()), "reason": "missing_packet"})
            continue
        execution = _execution_for_packet(execution_dir, str(packet["packet_id"]))
        if execution is None:
            missing_execution.append(
                {
                    "packet_id": packet["packet_id"],
                    "provider": packet.get("provider"),
                    "encoding_family": packet.get("encoding_family"),
                    "reason": "missing_packet_execution_counts",
                }
            )
            continue
        if not _assembled_from_stage113(execution):
            missing_execution.append(
                {
                    "packet_id": packet["packet_id"],
                    "provider": packet.get("provider"),
                    "encoding_family": packet.get("encoding_family"),
                    "reason": "stage113_assembled_status_missing",
                }
            )
            continue
        missing_fields = [
            field for field in REQUIRED_EXECUTION_FIELDS if field not in execution or execution.get(field) in (None, "", [])
        ]
        if missing_fields:
            missing_execution.append(
                {
                    "packet_id": packet["packet_id"],
                    "provider": packet.get("provider"),
                    "encoding_family": packet.get("encoding_family"),
                    "reason": "result_lineage_metadata_missing",
                    "missing_fields": missing_fields,
                }
            )
            continue
        record = packet_metrics(packet, execution)
        if record["coverage_fraction"] != 1.0 or record["missing_rows"]:
            missing_execution.append(
                {
                    "packet_id": packet["packet_id"],
                    "provider": packet.get("provider"),
                    "encoding_family": packet.get("encoding_family"),
                    "reason": "packet_row_counts_incomplete",
                    "missing_rows": record["missing_rows"],
                }
            )
            continue
        records.append(record)
    return records, missing_execution


def _comparison_summary(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_lane: dict[tuple[str, str], dict[str, dict[str, Any]]] = {}
    for record in records:
        key = (str(record["source_lane_id"]), str(record["circuit_template"]))
        by_lane.setdefault(key, {})[str(record["encoding_family"])] = record
    summaries = []
    for (lane_id, template), family_records in sorted(by_lane.items()):
        phasewrap = family_records.get("phasewrap")
        if phasewrap is None:
            continue
        phasewrap_mae = phasewrap.get("mean_absolute_score_error")
        comparator_maes = [
            family_records[family].get("mean_absolute_score_error")
            for family in COMPARATOR_FAMILIES
            if family in family_records and family_records[family].get("mean_absolute_score_error") is not None
        ]
        better_than = [
            family
            for family in COMPARATOR_FAMILIES
            if family in family_records
            and phasewrap_mae is not None
            and family_records[family].get("mean_absolute_score_error") is not None
            and phasewrap_mae < family_records[family]["mean_absolute_score_error"]
        ]
        summaries.append(
            {
                "source_lane_id": lane_id,
                "circuit_template": template,
                "phasewrap_mean_absolute_score_error": phasewrap_mae,
                "best_comparator_mean_absolute_score_error": min(comparator_maes) if comparator_maes else None,
                "phasewrap_lower_error_than": better_than,
                "all_families_present": all(family in family_records for family in ENCODING_FAMILIES),
            }
        )
    return summaries


def _comparison_groups_complete(records: list[dict[str, Any]], summaries: list[dict[str, Any]]) -> bool:
    expected_groups = {
        (str(record["source_lane_id"]), str(record["circuit_template"]))
        for record in records
    }
    return bool(expected_groups) and len(summaries) == len(expected_groups) and all(
        record.get("all_families_present") is True
        and record.get("phasewrap_mean_absolute_score_error") is not None
        and record.get("best_comparator_mean_absolute_score_error") is not None
        for record in summaries
    )


def run_stage103_preregistration(
    *,
    stage99_manifest_path: Path = DEFAULT_STAGE99_MANIFEST,
    stage100_manifest_path: Path = DEFAULT_STAGE100_MANIFEST,
    stage101_results_path: Path = DEFAULT_STAGE101_RESULTS,
    stage102_manifest_path: Path = DEFAULT_STAGE102_MANIFEST,
    execution_dir: Path | None = None,
) -> dict[str, Any]:
    stage99 = _load_json(stage99_manifest_path)
    stage100 = _load_json(stage100_manifest_path)
    stage101 = _load_json(stage101_results_path)
    stage102 = _load_json(stage102_manifest_path)
    sources = [
        (stage99_manifest_path, stage99),
        (stage100_manifest_path, stage100),
        (stage101_results_path, stage101),
        (stage102_manifest_path, stage102),
    ]
    missing_sources = [str(path.as_posix()) for path, payload in sources if payload is None]
    packet_paths = _packet_paths_from_manifest(stage99) + _packet_paths_from_manifest(stage100)
    metric_records, missing_execution = _metrics_records(packet_paths, execution_dir)
    comparison_summary = _comparison_summary(metric_records)
    calibration_pass = bool(
        stage101
        and stage101.get("known_state_calibration_pass") is True
        and stage101.get("decision") == "KNOWN_STATE_CALIBRATION_VERIFIED_READY_FOR_MATCHED_HARDWARE_EXECUTION"
    )
    all_packet_counts_present = bool(packet_paths) and not missing_execution and len(metric_records) == len(packet_paths)
    complete_comparison_groups = _comparison_groups_complete(metric_records, comparison_summary)
    ready_to_interpret = calibration_pass and all_packet_counts_present and complete_comparison_groups
    decision = (
        "ROBUSTNESS_METRICS_READY_FOR_INTERPRETATION"
        if ready_to_interpret
        else "ROBUSTNESS_METRICS_PREREGISTERED_HARDWARE_COUNTS_REQUIRED"
    )
    return {
        "schema_version": STAGE103_SCHEMA_VERSION,
        "stage": "stage103_robustness_metric_preregistration",
        "status": "completed",
        "objective": OBJECTIVE,
        "decision": decision,
        "source_artifacts": [str(path.as_posix()) for path, _ in sources],
        "missing_source_artifacts": missing_sources,
        "packet_count": len(packet_paths),
        "metric_record_count": len(metric_records),
        "missing_execution_count": len(missing_execution),
        "known_state_calibration_pass": calibration_pass,
        "ready_to_interpret_hardware_metrics": ready_to_interpret,
        "complete_comparison_group_count": sum(1 for record in comparison_summary if record.get("all_families_present") is True),
        "comparison_groups_complete": complete_comparison_groups,
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "metric_specification": {
            "primary_robustness_metric": "mean_absolute_score_error between calibrated measured score and ideal packet score",
            "secondary_metrics": [
                "root_mean_squared_score_error",
                "spearman_rank_correlation",
                "top1_match",
                "coverage_fraction",
                "shot_counts",
            ],
            "advantage_rule": (
                "PhaseWrap may be described as lower-error on a lane only if its mean absolute score error is lower "
                "than each named comparator family on the same source lane and circuit template after Stage 101 calibration passes."
            ),
            "count_key_policy": "packet execution counts must be canonical q0q1 decoded after Stage 101 calibration",
        },
        "metric_records": metric_records,
        "comparison_summary": comparison_summary,
        "missing_execution": missing_execution,
        "claim_boundary": {
            "supported": [
                "predeclared robustness and auditability metrics for future calibrated Stage 99 and Stage 100 packet executions",
                "fixed score reconstruction formulas for product-state and CX/parity packet families",
                "metric interpretation requires Stage 113-assembled packet evidence",
                "metric interpretation requires Stage 113 hardware-result lineage metadata",
                "metric interpretation requires complete row coverage and complete matched-family comparison groups",
                "a hard separation between metric preregistration and any future hardware advantage claim",
            ],
            "excluded": [
                "a noisy-hardware robustness result without calibrated packet counts",
                "a PhaseWrap advantage claim before Stage 101 passes and all matched packet counts are present",
                "production transformer superiority",
                "broad quantum advantage",
            ],
        },
        "next_gate": (
            "After Stage 101 calibration passes, execute Stage 99 and Stage 100 matched packets, provide canonical q0q1 "
            "raw_counts_by_row files per packet, and rerun Stage 103 for metric interpretation."
        ),
    }


def write_stage103_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "objective": result["objective"],
        "decision": result["decision"],
        "source_artifacts": result["source_artifacts"],
        "missing_source_artifacts": result["missing_source_artifacts"],
        "packet_count": result["packet_count"],
        "metric_record_count": result["metric_record_count"],
        "missing_execution_count": result["missing_execution_count"],
        "known_state_calibration_pass": result["known_state_calibration_pass"],
        "ready_to_interpret_hardware_metrics": result["ready_to_interpret_hardware_metrics"],
        "complete_comparison_group_count": result["complete_comparison_group_count"],
        "comparison_groups_complete": result["comparison_groups_complete"],
        "no_hardware_submission": result["no_hardware_submission"],
        "provider_credentials_required": result["provider_credentials_required"],
        "metric_specification": result["metric_specification"],
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
                "packet_id",
                "provider",
                "source_lane_id",
                "encoding_family",
                "circuit_template",
                "coverage_fraction",
                "mean_absolute_score_error",
                "root_mean_squared_score_error",
                "spearman_rank_correlation",
                "top1_match",
            ),
        )
        writer.writeheader()
        for record in result["metric_records"]:
            writer.writerow({field: record.get(field) for field in writer.fieldnames})
    return paths


def print_stage103_summary(result: dict[str, Any]) -> None:
    print(f"stage: {result['stage']}")
    print(f"status: {result['status']}")
    print(f"decision: {result['decision']}")
    print(f"packet_count: {result['packet_count']}")
    print(f"metric_record_count: {result['metric_record_count']}")
    print(f"known_state_calibration_pass: {result['known_state_calibration_pass']}")
    print(f"next_gate: {result['next_gate']}")
