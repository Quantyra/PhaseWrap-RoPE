from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

from .stage10_small_decoder_transformer import (
    TEST_LENGTHS,
    TRAIN_LENGTHS,
    VALIDATION_LENGTHS,
    VOCAB_SIZE,
    Stage10Example,
    _expected_calibration_error,
    make_stage10_splits,
    positional_bias,
)
from .stage45_matched_decoder_only_gate import METHOD_NAMES, _stage10_method_name
from .stage52_two_block_decoder_feasibility_audit import GENERALIZATION_TOP1_THRESHOLD
from .stage61_support_complete_two_block_audit import DEFAULT_AUDIT_SEEDS, DEFAULT_EXAMPLES_PER_LENGTH


STAGE72_SCHEMA_VERSION = "qrope_stage72_phase_cued_bias_tie_support_audit_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage72_phase_cued_bias_tie_support_audit"
TASK_NAME = "phase_cued_retrieval"
TIE_TOLERANCE = 1e-12


def _claim_boundary() -> dict[str, list[str]]:
    return {
        "supported": [
            "A no-credential tie-aware positional-bias support audit on original phase-cued rows.",
            "Evidence about whether the target position appears in each method's maximum-bias candidate set.",
            "Fair RoPE/ALiBI/sinusoidal/no-position/PhaseWrap comparisons without row metadata, learned parameters, or fallback lookup.",
        ],
        "excluded": [
            "production transformer superiority",
            "full transformer-scale validation",
            "a claim that PhaseWrap-RoPE replaces RoPE",
            "a claim that tie-aware support is learned decoder-only transformer behavior",
            "a claim that no-position all-support ambiguity is positional-method evidence",
            "broad quantum advantage",
        ],
    }


def _tie_prediction(row: Stage10Example, method_name: str) -> dict[str, Any]:
    bias = np.asarray(positional_bias(row, method_name), dtype=float)
    max_bias = float(np.max(bias))
    tie_positions = [int(index) for index, value in enumerate(bias) if abs(float(value) - max_bias) <= TIE_TOLERANCE]
    probabilities = np.zeros(VOCAB_SIZE, dtype=float)
    for position in tie_positions:
        probabilities[int(row.tokens[position])] += 1.0 / float(len(tie_positions))
    sorted_tokens = sorted(range(VOCAB_SIZE), key=lambda token: (-float(probabilities[token]), token))
    target_rank = int(sorted_tokens.index(row.label_token) + 1)
    bias_order = sorted(range(len(bias)), key=lambda index: (-float(bias[index]), index))
    target_bias_rank = int(bias_order.index(row.target_pos) + 1)
    target_in_max_tie = row.target_pos in tie_positions
    return {
        "target_probability": round(float(probabilities[row.label_token]), 6),
        "target_rank": target_rank,
        "top1_hit": 1.0 if target_rank == 1 else 0.0,
        "top1_confidence": round(float(probabilities[sorted_tokens[0]]), 6),
        "target_in_max_tie": bool(target_in_max_tie),
        "max_tie_count": len(tie_positions),
        "target_bias_rank": target_bias_rank,
        "best_bias": round(max_bias, 6),
        "target_bias": round(float(bias[row.target_pos]), 6),
        "best_deltas": [int(row.query_pos - position) for position in tie_positions[:8]],
    }


def evaluate_tie_support(rows: list[Stage10Example], method_name: str) -> dict[str, float]:
    predictions = [_tie_prediction(row, method_name) for row in rows]
    target_probs = [float(prediction["target_probability"]) for prediction in predictions]
    top1_hits = [float(prediction["top1_hit"]) for prediction in predictions]
    reciprocal_ranks = [1.0 / float(prediction["target_rank"]) for prediction in predictions]
    top1_confidences = [float(prediction["top1_confidence"]) for prediction in predictions]
    losses = [-math.log(max(value, 1e-12)) for value in target_probs]
    mean_loss = float(np.mean(losses))
    return {
        "row_count": len(rows),
        "loss": round(mean_loss, 6),
        "perplexity": round(float(math.exp(mean_loss)), 6),
        "top1_accuracy": round(float(np.mean(top1_hits)), 6),
        "mrr": round(float(np.mean(reciprocal_ranks)), 6),
        "mean_target_probability": round(float(np.mean(target_probs)), 6),
        "mean_top1_confidence": round(float(np.mean(top1_confidences)), 6),
        "expected_calibration_error": round(_expected_calibration_error(top1_confidences, top1_hits), 6),
        "target_in_max_tie_rate": round(float(np.mean([float(prediction["target_in_max_tie"]) for prediction in predictions])), 6),
        "mean_max_tie_count": round(float(np.mean([float(prediction["max_tie_count"]) for prediction in predictions])), 6),
        "mean_target_bias_rank": round(float(np.mean([float(prediction["target_bias_rank"]) for prediction in predictions])), 6),
    }


def _aggregate(run_table: list[dict[str, Any]], method_names: tuple[str, ...]) -> list[dict[str, Any]]:
    aggregate_table: list[dict[str, Any]] = []
    for method_name in method_names:
        rows = [row for row in run_table if row["method"] == method_name]
        if not rows:
            continue
        record: dict[str, Any] = {
            "task": TASK_NAME,
            "method": method_name,
            "seed_count": len(rows),
            "failed_run_count": 0,
        }
        for metric_name in (
            "train_top1_accuracy",
            "train_mrr",
            "train_mean_target_probability",
            "train_target_in_max_tie_rate",
            "train_mean_max_tie_count",
            "train_mean_target_bias_rank",
            "validation_top1_accuracy",
            "validation_mrr",
            "validation_mean_target_probability",
            "validation_target_in_max_tie_rate",
            "validation_mean_max_tie_count",
            "validation_mean_target_bias_rank",
            "test_top1_accuracy",
            "test_mrr",
            "test_mean_target_probability",
            "test_target_in_max_tie_rate",
            "test_mean_max_tie_count",
            "test_mean_target_bias_rank",
        ):
            record[f"{metric_name}_mean"] = round(float(np.mean([row[metric_name] for row in rows])), 6)
        aggregate_table.append(record)
    return aggregate_table


def _decision(aggregate_table: list[dict[str, Any]]) -> dict[str, Any]:
    best_top1 = sorted(
        aggregate_table,
        key=lambda row: (
            row["test_top1_accuracy_mean"],
            row["test_mrr_mean"],
            row["test_mean_target_probability_mean"],
            row["test_target_in_max_tie_rate_mean"],
            row["method"],
        ),
        reverse=True,
    )[0]
    phasewrap_rows = [row for row in aggregate_table if row["method"].startswith("phasewrap")]
    phasewrap_support = max((row["test_target_in_max_tie_rate_mean"] for row in phasewrap_rows), default=0.0)
    if best_top1["test_top1_accuracy_mean"] >= GENERALIZATION_TOP1_THRESHOLD:
        decision = "PHASE_CUED_TIE_SUPPORT_SOLVES_REVIEW_REQUIRED"
        boundary = "Tie-aware positional-bias support crosses the phase-cued retrieval threshold; review method ordering before any claim update."
    elif phasewrap_support >= GENERALIZATION_TOP1_THRESHOLD:
        decision = "PHASE_CUED_PHASEWRAP_TIE_SUPPORT_WITH_AMBIGUITY"
        boundary = "A PhaseWrap method includes the phase-cued target in its max-bias support often enough, but ambiguity prevents top-1 success."
    else:
        decision = "PHASE_CUED_TARGET_NOT_IN_PHASEWRAP_MAX_BIAS_SUPPORT"
        boundary = "PhaseWrap max-bias support does not include the original held-out phase-cued target often enough to explain the blocker as argmax tie-breaking."
    return {
        "decision": decision,
        "claim_boundary": boundary,
        "generalization_top1_threshold": GENERALIZATION_TOP1_THRESHOLD,
        "best_top1_method": best_top1["method"],
        "best_top1": best_top1["test_top1_accuracy_mean"],
        "best_target_in_max_tie_method": max(
            aggregate_table,
            key=lambda row: (row["test_target_in_max_tie_rate_mean"], -row["test_mean_max_tie_count_mean"], row["method"]),
        )["method"],
        "target_in_max_tie_rate_by_method": {
            row["method"]: row["test_target_in_max_tie_rate_mean"] for row in aggregate_table
        },
        "mean_max_tie_count_by_method": {
            row["method"]: row["test_mean_max_tie_count_mean"] for row in aggregate_table
        },
        "phasewrap_best_target_in_max_tie_rate": phasewrap_support,
    }


def run_stage72_audit(
    *,
    seeds: tuple[int, ...] = DEFAULT_AUDIT_SEEDS,
    examples_per_length: int = DEFAULT_EXAMPLES_PER_LENGTH,
    method_names: tuple[str, ...] = METHOD_NAMES,
) -> dict[str, Any]:
    splits = make_stage10_splits(seeds=seeds, examples_per_length=examples_per_length)[TASK_NAME]
    run_table: list[dict[str, Any]] = []
    per_example_table: list[dict[str, Any]] = []
    for seed in seeds:
        split_rows = {split_name: [row for row in rows if row.seed == seed] for split_name, rows in splits.items()}
        for method_name in method_names:
            stage10_method = _stage10_method_name(method_name)
            row: dict[str, Any] = {
                "task": TASK_NAME,
                "seed": seed,
                "method": method_name,
                "stage10_method_alias": stage10_method,
                "train_row_count": len(split_rows["train"]),
                "validation_row_count": len(split_rows["validation"]),
                "test_row_count": len(split_rows["test"]),
            }
            for split_name, rows in split_rows.items():
                metrics = evaluate_tie_support(rows, stage10_method)
                for metric_name, value in metrics.items():
                    if metric_name != "row_count":
                        row[f"{split_name}_{metric_name}"] = value
                for example in rows:
                    prediction = _tie_prediction(example, stage10_method)
                    per_example_table.append(
                        {
                            "task": TASK_NAME,
                            "split": split_name,
                            "seed": seed,
                            "method": method_name,
                            "example_id": example.example_id,
                            "sequence_length": example.sequence_length,
                            "query_pos": example.query_pos,
                            "reference_delta": example.reference_delta,
                            "target_delta": example.target_delta,
                            "target_pos": example.target_pos,
                            "label_token": example.label_token,
                            **{key: value for key, value in prediction.items() if key != "best_deltas"},
                            "best_deltas": " ".join(str(delta) for delta in prediction["best_deltas"]),
                        }
                    )
            run_table.append(row)
    aggregate_table = _aggregate(run_table, method_names)
    ranking_table = sorted(
        aggregate_table,
        key=lambda row: (
            row["test_top1_accuracy_mean"],
            row["test_mrr_mean"],
            row["test_mean_target_probability_mean"],
            row["test_target_in_max_tie_rate_mean"],
            row["method"],
        ),
        reverse=True,
    )
    return {
        "schema_version": STAGE72_SCHEMA_VERSION,
        "stage": "stage72_phase_cued_bias_tie_support_audit",
        "status": "completed",
        "dataset": "synthetic_stage10_phase_cued_rows_bias_tie_support_v1",
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "source_stage": "stage71_positional_bias_copy_upper_bound_audit",
        "source_rows": "stage10 original phase_cued_retrieval rows",
        "method_names": list(method_names),
        "tasks": [TASK_NAME],
        "seeds": list(seeds),
        "train_lengths": list(TRAIN_LENGTHS),
        "validation_lengths": list(VALIDATION_LENGTHS),
        "test_lengths": list(TEST_LENGTHS),
        "examples_per_length": examples_per_length,
        "tie_tolerance": TIE_TOLERANCE,
        "model": {
            "type": "deterministic_phase_cued_bias_tie_support_audit",
            "trained_parameters": "none",
            "row_policy": "collect every prefix position tied for maximum positional bias, then copy uniformly over those positions",
            "value_output_mode": "uniform mass over max-bias tied copied tokens",
        },
        "claim_boundary": _claim_boundary(),
        "failed_runs": [],
        "run_table": run_table,
        "per_example_table": per_example_table,
        "aggregate_table": aggregate_table,
        "ranking_table": ranking_table,
        "decision": _decision(aggregate_table),
    }


def write_stage72_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "no_hardware_submission": result["no_hardware_submission"],
        "provider_credentials_required": result["provider_credentials_required"],
        "method_names": result["method_names"],
        "tasks": result["tasks"],
        "result_path": str((output_dir / "results.json").as_posix()),
        "summary_csv_path": str((output_dir / "summary.csv").as_posix()),
        "per_run_csv_path": str((output_dir / "per_run_results.csv").as_posix()),
        "per_example_csv_path": str((output_dir / "per_example_results.csv").as_posix()),
        "failed_runs_path": str((output_dir / "failed_runs.json").as_posix()),
        "decision": result["decision"],
        "claim_boundary": result["claim_boundary"],
    }
    paths = {
        "manifest": str(output_dir / "manifest.json"),
        "result": str(output_dir / "results.json"),
        "summary_csv": str(output_dir / "summary.csv"),
        "per_run_csv": str(output_dir / "per_run_results.csv"),
        "per_example_csv": str(output_dir / "per_example_results.csv"),
        "failed_runs": str(output_dir / "failed_runs.json"),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    for filename, rows in (
        ("summary.csv", result["aggregate_table"]),
        ("per_run_results.csv", result["run_table"]),
        ("per_example_results.csv", result["per_example_table"]),
    ):
        with (output_dir / filename).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
    (output_dir / "failed_runs.json").write_text(json.dumps(result["failed_runs"], indent=2, sort_keys=True), encoding="utf-8")
    return paths


def print_stage72_summary(result: dict[str, Any]) -> None:
    columns = (
        "method",
        "seed_count",
        "test_top1_accuracy_mean",
        "test_mrr_mean",
        "test_mean_target_probability_mean",
        "test_target_in_max_tie_rate_mean",
        "test_mean_max_tie_count_mean",
        "test_mean_target_bias_rank_mean",
    )
    print(" | ".join(columns))
    print(" | ".join("---" for _ in columns))
    for row in result["ranking_table"]:
        print(" | ".join(str(row[column]) for column in columns))
    print(f"decision: {result['decision']['decision']}")
    print(f"claim_boundary: {result['decision']['claim_boundary']}")
