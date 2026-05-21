from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

from .stage10_small_decoder_transformer import TEST_LENGTHS, TRAIN_LENGTHS, VALIDATION_LENGTHS, VOCAB_SIZE, Stage10Example, _expected_calibration_error, make_stage10_splits
from .stage11_phasewrap_theory import PERIOD_PAIR_GRID, lcm, phasewrap_score
from .stage52_two_block_decoder_feasibility_audit import GENERALIZATION_TOP1_THRESHOLD
from .stage61_support_complete_two_block_audit import DEFAULT_AUDIT_SEEDS, DEFAULT_EXAMPLES_PER_LENGTH


STAGE73_SCHEMA_VERSION = "qrope_stage73_phase_cued_period_pair_support_audit_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage73_phase_cued_period_pair_support_audit"
TASK_NAME = "phase_cued_retrieval"
TIE_TOLERANCE = 1e-12


def _claim_boundary() -> dict[str, list[str]]:
    return {
        "supported": [
            "A no-credential fixed period-pair sweep over original Stage10 phase-cued rows.",
            "Evidence about whether alternate PhaseWrap period pairs put the held-out phase-cued target in max-score support.",
            "A fair no-training comparison among predeclared PhaseWrap period pairs without row metadata or fallback lookup.",
        ],
        "excluded": [
            "production transformer superiority",
            "full transformer-scale validation",
            "a claim that PhaseWrap-RoPE replaces RoPE",
            "a claim that period-pair selection after seeing held-out rows is promotion evidence",
            "a claim that fixed-score support is learned decoder-only transformer behavior",
            "broad quantum advantage",
        ],
    }


def _scores(row: Stage10Example, period_pair: tuple[int, int]) -> np.ndarray:
    candidate_deltas = row.query_pos - np.arange(row.query_pos, dtype=int)
    return np.asarray([phasewrap_score(row.reference_delta, int(delta), period_pair) for delta in candidate_deltas], dtype=float)


def _prediction(row: Stage10Example, period_pair: tuple[int, int]) -> dict[str, Any]:
    scores = _scores(row, period_pair)
    max_score = float(np.max(scores))
    max_positions = [int(index) for index, value in enumerate(scores) if abs(float(value) - max_score) <= TIE_TOLERANCE]
    probabilities = np.zeros(VOCAB_SIZE, dtype=float)
    for position in max_positions:
        probabilities[int(row.tokens[position])] += 1.0 / float(len(max_positions))
    sorted_tokens = sorted(range(VOCAB_SIZE), key=lambda token: (-float(probabilities[token]), token))
    score_order = sorted(range(len(scores)), key=lambda index: (-float(scores[index]), index))
    target_in_max_support = row.target_pos in max_positions
    return {
        "target_probability": round(float(probabilities[row.label_token]), 6),
        "target_rank": int(sorted_tokens.index(row.label_token) + 1),
        "top1_hit": 1.0 if sorted_tokens[0] == row.label_token else 0.0,
        "top1_confidence": round(float(probabilities[sorted_tokens[0]]), 6),
        "target_in_max_support": bool(target_in_max_support),
        "max_support_count": len(max_positions),
        "target_score_rank": int(score_order.index(row.target_pos) + 1),
        "max_score": round(max_score, 12),
        "target_score": round(float(scores[row.target_pos]), 12),
        "score_gap": round(max_score - float(scores[row.target_pos]), 12),
        "max_deltas": [int(row.query_pos - position) for position in max_positions[:8]],
    }


def evaluate_period_pair_support(rows: list[Stage10Example], period_pair: tuple[int, int]) -> dict[str, float]:
    predictions = [_prediction(row, period_pair) for row in rows]
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
        "target_in_max_support_rate": round(float(np.mean([float(prediction["target_in_max_support"]) for prediction in predictions])), 6),
        "mean_max_support_count": round(float(np.mean([float(prediction["max_support_count"]) for prediction in predictions])), 6),
        "mean_target_score_rank": round(float(np.mean([float(prediction["target_score_rank"]) for prediction in predictions])), 6),
        "mean_score_gap": round(float(np.mean([float(prediction["score_gap"]) for prediction in predictions])), 6),
    }


def _period_pair_label(period_pair: tuple[int, int]) -> str:
    return f"{period_pair[0]}/{period_pair[1]}"


def _aggregate(run_table: list[dict[str, Any]], period_pairs: tuple[tuple[int, int], ...]) -> list[dict[str, Any]]:
    aggregate_table: list[dict[str, Any]] = []
    for period_pair in period_pairs:
        label = _period_pair_label(period_pair)
        rows = [row for row in run_table if row["period_pair"] == label]
        record: dict[str, Any] = {
            "task": TASK_NAME,
            "period_pair": label,
            "period_a": period_pair[0],
            "period_b": period_pair[1],
            "gcd": math.gcd(*period_pair),
            "fundamental_period": lcm(*period_pair),
            "seed_count": len(rows),
            "failed_run_count": 0,
        }
        for metric_name in (
            "train_top1_accuracy",
            "train_mrr",
            "train_mean_target_probability",
            "train_target_in_max_support_rate",
            "train_mean_max_support_count",
            "train_mean_target_score_rank",
            "train_mean_score_gap",
            "validation_top1_accuracy",
            "validation_mrr",
            "validation_mean_target_probability",
            "validation_target_in_max_support_rate",
            "validation_mean_max_support_count",
            "validation_mean_target_score_rank",
            "validation_mean_score_gap",
            "test_top1_accuracy",
            "test_mrr",
            "test_mean_target_probability",
            "test_target_in_max_support_rate",
            "test_mean_max_support_count",
            "test_mean_target_score_rank",
            "test_mean_score_gap",
        ):
            record[f"{metric_name}_mean"] = round(float(np.mean([row[metric_name] for row in rows])), 6)
        aggregate_table.append(record)
    return aggregate_table


def _decision(aggregate_table: list[dict[str, Any]]) -> dict[str, Any]:
    best_support = sorted(
        aggregate_table,
        key=lambda row: (
            row["test_target_in_max_support_rate_mean"],
            row["test_top1_accuracy_mean"],
            row["test_mrr_mean"],
            -row["test_mean_max_support_count_mean"],
            row["period_pair"],
        ),
        reverse=True,
    )[0]
    best_top1 = sorted(
        aggregate_table,
        key=lambda row: (
            row["test_top1_accuracy_mean"],
            row["test_mrr_mean"],
            row["test_mean_target_probability_mean"],
            row["period_pair"],
        ),
        reverse=True,
    )[0]
    default_row = next(row for row in aggregate_table if row["period_pair"] == "8/12")
    if best_top1["test_top1_accuracy_mean"] >= GENERALIZATION_TOP1_THRESHOLD:
        decision = "PHASE_CUED_PERIOD_PAIR_SOLVES_REVIEW_REQUIRED"
        boundary = "At least one fixed period pair crosses the phase-cued top-1 threshold; review held-out selection before any claim update."
    elif best_support["test_target_in_max_support_rate_mean"] >= GENERALIZATION_TOP1_THRESHOLD:
        decision = "PHASE_CUED_PERIOD_PAIR_SUPPORT_WITH_AMBIGUITY"
        boundary = "At least one fixed period pair puts the phase-cued target in max-score support often enough, but top-1 remains below threshold."
    else:
        decision = "PHASE_CUED_PERIOD_PAIR_SWEEP_DOES_NOT_REPAIR_SUPPORT"
        boundary = "The tested fixed PhaseWrap period pairs do not put the original held-out phase-cued target in max-score support often enough."
    return {
        "decision": decision,
        "claim_boundary": boundary,
        "generalization_top1_threshold": GENERALIZATION_TOP1_THRESHOLD,
        "best_support_period_pair": best_support["period_pair"],
        "best_support_rate": best_support["test_target_in_max_support_rate_mean"],
        "best_top1_period_pair": best_top1["period_pair"],
        "best_top1": best_top1["test_top1_accuracy_mean"],
        "default_8_12_support_rate": default_row["test_target_in_max_support_rate_mean"],
        "default_8_12_top1": default_row["test_top1_accuracy_mean"],
        "support_rate_by_period_pair": {
            row["period_pair"]: row["test_target_in_max_support_rate_mean"] for row in aggregate_table
        },
    }


def run_stage73_audit(
    *,
    seeds: tuple[int, ...] = DEFAULT_AUDIT_SEEDS,
    examples_per_length: int = DEFAULT_EXAMPLES_PER_LENGTH,
    period_pairs: tuple[tuple[int, int], ...] = PERIOD_PAIR_GRID,
) -> dict[str, Any]:
    splits = make_stage10_splits(seeds=seeds, examples_per_length=examples_per_length)[TASK_NAME]
    run_table: list[dict[str, Any]] = []
    per_example_table: list[dict[str, Any]] = []
    for seed in seeds:
        split_rows = {split_name: [row for row in rows if row.seed == seed] for split_name, rows in splits.items()}
        for period_pair in period_pairs:
            label = _period_pair_label(period_pair)
            row: dict[str, Any] = {
                "task": TASK_NAME,
                "seed": seed,
                "period_pair": label,
                "period_a": period_pair[0],
                "period_b": period_pair[1],
                "train_row_count": len(split_rows["train"]),
                "validation_row_count": len(split_rows["validation"]),
                "test_row_count": len(split_rows["test"]),
            }
            for split_name, rows in split_rows.items():
                metrics = evaluate_period_pair_support(rows, period_pair)
                for metric_name, value in metrics.items():
                    if metric_name != "row_count":
                        row[f"{split_name}_{metric_name}"] = value
                for example in rows:
                    prediction = _prediction(example, period_pair)
                    per_example_table.append(
                        {
                            "task": TASK_NAME,
                            "split": split_name,
                            "seed": seed,
                            "period_pair": label,
                            "sequence_length": example.sequence_length,
                            "query_pos": example.query_pos,
                            "reference_delta": example.reference_delta,
                            "target_delta": example.target_delta,
                            "target_pos": example.target_pos,
                            "label_token": example.label_token,
                            **{key: value for key, value in prediction.items() if key != "max_deltas"},
                            "max_deltas": " ".join(str(delta) for delta in prediction["max_deltas"]),
                        }
                    )
            run_table.append(row)
    aggregate_table = _aggregate(run_table, period_pairs)
    ranking_table = sorted(
        aggregate_table,
        key=lambda row: (
            row["test_target_in_max_support_rate_mean"],
            row["test_top1_accuracy_mean"],
            row["test_mrr_mean"],
            -row["test_mean_max_support_count_mean"],
            row["period_pair"],
        ),
        reverse=True,
    )
    return {
        "schema_version": STAGE73_SCHEMA_VERSION,
        "stage": "stage73_phase_cued_period_pair_support_audit",
        "status": "completed",
        "dataset": "synthetic_stage10_phase_cued_rows_period_pair_support_v1",
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "source_stage": "stage72_phase_cued_bias_tie_support_audit",
        "source_rows": "stage10 original phase_cued_retrieval rows",
        "tasks": [TASK_NAME],
        "seeds": list(seeds),
        "train_lengths": list(TRAIN_LENGTHS),
        "validation_lengths": list(VALIDATION_LENGTHS),
        "test_lengths": list(TEST_LENGTHS),
        "examples_per_length": examples_per_length,
        "period_pairs": [list(pair) for pair in period_pairs],
        "tie_tolerance": TIE_TOLERANCE,
        "model": {
            "type": "deterministic_phasewrap_period_pair_max_support_sweep",
            "trained_parameters": "none",
            "row_policy": "score every prefix position with a fixed PhaseWrap period pair, copy uniformly over max-score positions",
            "value_output_mode": "uniform mass over max-score copied tokens",
        },
        "claim_boundary": _claim_boundary(),
        "failed_runs": [],
        "run_table": run_table,
        "per_example_table": per_example_table,
        "aggregate_table": aggregate_table,
        "ranking_table": ranking_table,
        "decision": _decision(aggregate_table),
    }


def write_stage73_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "no_hardware_submission": result["no_hardware_submission"],
        "provider_credentials_required": result["provider_credentials_required"],
        "tasks": result["tasks"],
        "period_pairs": result["period_pairs"],
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


def print_stage73_summary(result: dict[str, Any]) -> None:
    columns = (
        "period_pair",
        "fundamental_period",
        "test_top1_accuracy_mean",
        "test_mrr_mean",
        "test_target_in_max_support_rate_mean",
        "test_mean_max_support_count_mean",
        "test_mean_score_gap_mean",
    )
    print(" | ".join(columns))
    print(" | ".join("---" for _ in columns))
    for row in result["ranking_table"]:
        print(" | ".join(str(row[column]) for column in columns))
    print(f"decision: {result['decision']['decision']}")
    print(f"claim_boundary: {result['decision']['claim_boundary']}")
