from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


STAGE44_SCHEMA_VERSION = "qrope_stage44_compact_diagnostic_plateau_audit_v1"
DEFAULT_INPUT_ROOT = Path("logs") / "automated_stage_gates"
DEFAULT_OUTPUT_DIR = DEFAULT_INPUT_ROOT / "stage44_compact_diagnostic_plateau_audit"

PRIMARY_METRICS = (
    "top1_accuracy_mean",
    "mrr_mean",
    "mean_target_value_probability_mean",
    "expected_calibration_error_mean",
)


@dataclass(frozen=True)
class StageInput:
    stage_number: int
    stage_name: str
    summary_path: Path
    diagnostic_class: str


STAGE_INPUTS = (
    StageInput(
        stage_number=39,
        stage_name="stage39_sequence_decoder_retrieval",
        summary_path=Path("stage39_sequence_decoder_retrieval") / "summary.csv",
        diagnostic_class="compact_all_prefix_sequence_decoder",
    ),
    StageInput(
        stage_number=40,
        stage_name="stage40_sequence_length_curriculum",
        summary_path=Path("stage40_sequence_length_curriculum") / "summary.csv",
        diagnostic_class="compact_all_prefix_sequence_decoder_curriculum",
    ),
    StageInput(
        stage_number=41,
        stage_name="stage41_pointer_copy_sequence",
        summary_path=Path("stage41_pointer_copy_sequence") / "summary.csv",
        diagnostic_class="compact_pointer_copy_diagnostic",
    ),
    StageInput(
        stage_number=42,
        stage_name="stage42_trainable_pointer_generator_sequence",
        summary_path=Path("stage42_trainable_pointer_generator_sequence") / "summary.csv",
        diagnostic_class="compact_trainable_pointer_generator",
    ),
    StageInput(
        stage_number=43,
        stage_name="stage43_generator_hardened_pointer_sequence",
        summary_path=Path("stage43_generator_hardened_pointer_sequence") / "summary.csv",
        diagnostic_class="compact_generator_hardened_pointer_generator",
    ),
)


def _read_summary(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"missing summary file: {path}")
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError(f"summary file has no rows: {path}")
    missing = [metric for metric in PRIMARY_METRICS if metric not in rows[0]]
    if missing:
        raise ValueError(f"summary file {path} is missing required metrics: {missing}")
    if "method" not in rows[0]:
        raise ValueError(f"summary file {path} is missing method column")
    return rows


def _as_float(row: dict[str, str], metric: str) -> float:
    return float(row[metric])


def _best_row(rows: list[dict[str, str]], metric: str, *, larger_is_better: bool) -> dict[str, str]:
    return sorted(rows, key=lambda row: (_as_float(row, metric), row["method"]), reverse=larger_is_better)[0]


def _phasewrap_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [row for row in rows if row["method"].startswith("phasewrap")]


def _metric_record(rows: list[dict[str, str]], metric: str, *, larger_is_better: bool) -> dict[str, Any]:
    best = _best_row(rows, metric, larger_is_better=larger_is_better)
    phase_rows = _phasewrap_rows(rows)
    best_phasewrap = _best_row(phase_rows, metric, larger_is_better=larger_is_better) if phase_rows else None
    record: dict[str, Any] = {
        "metric": metric,
        "larger_is_better": larger_is_better,
        "best_method": best["method"],
        "best_value": round(_as_float(best, metric), 6),
    }
    if best_phasewrap is not None:
        record["best_phasewrap_method"] = best_phasewrap["method"]
        record["best_phasewrap_value"] = round(_as_float(best_phasewrap, metric), 6)
        record["phasewrap_matches_best"] = best_phasewrap["method"] == best["method"]
    else:
        record["best_phasewrap_method"] = None
        record["best_phasewrap_value"] = None
        record["phasewrap_matches_best"] = False
    return record


def _stage_record(stage_input: StageInput, rows: list[dict[str, str]]) -> dict[str, Any]:
    metric_records = [
        _metric_record(rows, "top1_accuracy_mean", larger_is_better=True),
        _metric_record(rows, "mrr_mean", larger_is_better=True),
        _metric_record(rows, "mean_target_value_probability_mean", larger_is_better=True),
        _metric_record(rows, "expected_calibration_error_mean", larger_is_better=False),
    ]
    best_by_metric = {record["metric"]: record["best_method"] for record in metric_records}
    phasewrap_wins = [record["metric"] for record in metric_records if record["phasewrap_matches_best"]]
    return {
        "stage_number": stage_input.stage_number,
        "stage_name": stage_input.stage_name,
        "diagnostic_class": stage_input.diagnostic_class,
        "method_count": len(rows),
        "row_count_per_method": int(float(rows[0].get("row_count", "0"))) if rows[0].get("row_count") else None,
        "run_count_per_method": int(float(rows[0].get("run_count", "0"))) if rows[0].get("run_count") else None,
        "parameter_count": int(float(rows[0].get("parameter_count", "0"))) if rows[0].get("parameter_count") else None,
        "best_by_metric": best_by_metric,
        "metric_records": metric_records,
        "phasewrap_win_metrics": phasewrap_wins,
        "phasewrap_wins_all_primary_metrics": len(phasewrap_wins) == len(PRIMARY_METRICS),
    }


def _decision(stage_records: list[dict[str, Any]]) -> dict[str, Any]:
    compact_only = all(record["diagnostic_class"].startswith("compact_") for record in stage_records)
    phasewrap_sweeps = [record["stage_name"] for record in stage_records if record["phasewrap_wins_all_primary_metrics"]]
    final_stage = stage_records[-1]
    final_best = final_stage["best_by_metric"]
    final_rope_strongest = all(
        final_best[metric] == "rope_relative"
        for metric in ("top1_accuracy_mean", "mrr_mean", "mean_target_value_probability_mean")
    )
    final_phasewrap_calibration_best = final_best["expected_calibration_error_mean"].startswith("phasewrap")
    plateau = compact_only and not phasewrap_sweeps and final_rope_strongest and not final_phasewrap_calibration_best
    return {
        "decision": "BOUND_COMPACT_DIAGNOSTIC_PLATEAU" if plateau else "CONTINUE_COMPACT_DIAGNOSTICS",
        "compact_only": compact_only,
        "phasewrap_sweep_stage_names": phasewrap_sweeps,
        "final_stage_name": final_stage["stage_name"],
        "final_stage_rope_strongest_on_ranking_and_probability": final_rope_strongest,
        "final_stage_phasewrap_best_calibration": final_phasewrap_calibration_best,
        "claim_boundary": (
            "Stages 39-43 should be treated as a compact-diagnostic plateau: useful bounded mechanism evidence, "
            "not RoPE-replacement or production-transformer evidence."
            if plateau
            else "The compact-diagnostic record is not yet sufficient to declare a plateau."
        ),
        "next_gate": (
            "Move the fair RoPE/ALiBI/sinusoidal/no-position/PhaseWrap comparison into a stronger matched "
            "decoder-only transformer benchmark before expanding claims."
            if plateau
            else "Continue only with compact diagnostics that directly close a named evidence gap."
        ),
    }


def run_stage44_audit(
    *,
    input_root: Path = DEFAULT_INPUT_ROOT,
    stage_inputs: tuple[StageInput, ...] = STAGE_INPUTS,
) -> dict[str, Any]:
    stage_records: list[dict[str, Any]] = []
    for stage_input in stage_inputs:
        rows = _read_summary(input_root / stage_input.summary_path)
        stage_records.append(_stage_record(stage_input, rows))
    decision = _decision(stage_records)
    return {
        "schema_version": STAGE44_SCHEMA_VERSION,
        "stage": "stage44_compact_diagnostic_plateau_audit",
        "source_stages": [record["stage_name"] for record in stage_records],
        "primary_metrics": list(PRIMARY_METRICS),
        "stage_records": stage_records,
        "decision": decision,
        "claim_boundary": {
            "supported": [
                "A reproducible plateau audit over the sealed compact sequence and pointer-generator diagnostics.",
                "A bounded claim that PhaseWrap-derived methods can be ranking-competitive in compact diagnostics.",
                "A negative claim that Stages 39-43 do not justify RoPE-replacement or production-transformer claims.",
            ],
            "excluded": [
                "production transformer superiority",
                "full transformer-scale validation",
                "a claim that PhaseWrap-RoPE replaces RoPE",
                "broad quantum advantage",
                "a claim that additional compact copy-path diagnostics should expand the claim boundary",
            ],
        },
    }


def write_stage44_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "source_stages": result["source_stages"],
        "primary_metrics": result["primary_metrics"],
        "decision": result["decision"],
        "result_path": str((output_dir / "results.json").as_posix()),
        "summary_csv_path": str((output_dir / "summary.csv").as_posix()),
    }
    paths = {
        "manifest": str(output_dir / "manifest.json"),
        "results": str(output_dir / "results.json"),
        "summary_csv": str(output_dir / "summary.csv"),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    rows = []
    for record in result["stage_records"]:
        rows.append(
            {
                "stage_number": record["stage_number"],
                "stage_name": record["stage_name"],
                "diagnostic_class": record["diagnostic_class"],
                "phasewrap_win_metrics": ";".join(record["phasewrap_win_metrics"]),
                "phasewrap_wins_all_primary_metrics": record["phasewrap_wins_all_primary_metrics"],
                "best_top1": record["best_by_metric"]["top1_accuracy_mean"],
                "best_mrr": record["best_by_metric"]["mrr_mean"],
                "best_target_probability": record["best_by_metric"]["mean_target_value_probability_mean"],
                "best_ece": record["best_by_metric"]["expected_calibration_error_mean"],
            }
        )
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return paths


def print_stage44_table(result: dict[str, Any]) -> None:
    columns = (
        "stage_name",
        "best_top1",
        "best_mrr",
        "best_target_probability",
        "best_ece",
        "phasewrap_win_metrics",
    )
    print(" | ".join(columns))
    print(" | ".join("---" for _ in columns))
    for record in result["stage_records"]:
        row = {
            "stage_name": record["stage_name"],
            "best_top1": record["best_by_metric"]["top1_accuracy_mean"],
            "best_mrr": record["best_by_metric"]["mrr_mean"],
            "best_target_probability": record["best_by_metric"]["mean_target_value_probability_mean"],
            "best_ece": record["best_by_metric"]["expected_calibration_error_mean"],
            "phasewrap_win_metrics": ",".join(record["phasewrap_win_metrics"]) or "none",
        }
        print(" | ".join(str(row[column]) for column in columns))
    print(f"decision: {result['decision']['decision']}")
    print(f"claim_boundary: {result['decision']['claim_boundary']}")
