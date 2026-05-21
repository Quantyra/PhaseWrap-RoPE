from __future__ import annotations

import csv
import hashlib
import json
import math
import random
from pathlib import Path
from typing import Any

import numpy as np

from .stage10_small_decoder_transformer import (
    DEFAULT_SEEDS,
    TASK_NAMES,
    TEST_LENGTHS,
    TEXT_TOKEN_IDS,
    TRAIN_LENGTHS,
    VALIDATION_LENGTHS,
    VOCAB_SIZE,
    Stage10Example,
    make_stage10_splits,
    positional_bias,
)
from .stage45_matched_decoder_only_gate import METHOD_NAMES, _stage10_method_name


STAGE49_SCHEMA_VERSION = "qrope_stage49_copy_decoder_retrieval_repair_audit_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage49_copy_decoder_retrieval_repair_audit"
DEFAULT_AUDIT_SEEDS = DEFAULT_SEEDS
DEFAULT_EXAMPLES_PER_LENGTH = 2
DEFAULT_POSITION_SCALES = (0.0, 0.5, 1.0, 2.0, 4.0, 8.0, 12.0)
CONTENT_MATCH_BOOST = 6.0
TINY_TEXT_TASK = "tiny_text_fact_qa"
RETRIEVAL_TASKS = tuple(task for task in TASK_NAMES if task != TINY_TEXT_TASK)
RETRIEVAL_REPAIR_TOP1_THRESHOLD = 0.50


def _softmax(values: np.ndarray) -> np.ndarray:
    shifted = values - np.max(values)
    exp_values = np.exp(shifted)
    return exp_values / np.sum(exp_values)


def _content_logits(row: Stage10Example) -> np.ndarray:
    logits = np.zeros(row.query_pos, dtype=float)
    if row.task != TINY_TEXT_TASK:
        return logits
    query_tokens = row.tokens[max(0, row.query_pos - 4) : row.query_pos + 1]
    entity_ids = [token for token in query_tokens if 87 <= token < 96]
    if not entity_ids:
        return logits
    entity_id = int(entity_ids[0])
    fact_id = TEXT_TOKEN_IDS["fact"]
    is_id = TEXT_TOKEN_IDS["is"]
    for index in range(3, row.query_pos):
        if row.tokens[index - 3] == fact_id and row.tokens[index - 2] == entity_id and row.tokens[index - 1] == is_id:
            logits[index] += CONTENT_MATCH_BOOST
    return logits


def _copy_distribution(row: Stage10Example, method_name: str, position_scale: float) -> np.ndarray:
    stage10_method = _stage10_method_name(method_name)
    logits = _content_logits(row) + position_scale * positional_bias(row, stage10_method)
    attention = _softmax(logits)
    values = np.zeros(VOCAB_SIZE, dtype=float)
    np.add.at(values, np.array(row.tokens[: row.query_pos], dtype=int), attention)
    return values


def _ranked_indices(values: np.ndarray) -> list[int]:
    return sorted(range(len(values)), key=lambda index: (-float(values[index]), index))


def evaluate_copy_decoder(rows: list[Stage10Example], method_name: str, position_scale: float) -> dict[str, float]:
    losses: list[float] = []
    reciprocal_ranks: list[float] = []
    top1_hits: list[float] = []
    target_probs: list[float] = []
    top1_confidences: list[float] = []
    for row in rows:
        values = _copy_distribution(row, method_name, position_scale)
        ranked = _ranked_indices(values)
        rank = ranked.index(row.label_token) + 1
        target_probability = float(values[row.label_token])
        top1_token = ranked[0]
        top1_correct = 1.0 if top1_token == row.label_token else 0.0
        losses.append(-math.log(max(target_probability, 1e-12)))
        reciprocal_ranks.append(1.0 / float(rank))
        top1_hits.append(top1_correct)
        target_probs.append(target_probability)
        top1_confidences.append(float(values[top1_token]))
    mean_loss = float(np.mean(losses))
    return {
        "row_count": float(len(rows)),
        "loss": round(mean_loss, 6),
        "perplexity": round(float(math.exp(mean_loss)), 6),
        "top1_accuracy": round(float(np.mean(top1_hits)), 6),
        "mrr": round(float(np.mean(reciprocal_ranks)), 6),
        "mean_target_probability": round(float(np.mean(target_probs)), 6),
        "mean_top1_confidence": round(float(np.mean(top1_confidences)), 6),
        "expected_calibration_error": round(_expected_calibration_error(top1_confidences, top1_hits), 6),
    }


def _expected_calibration_error(confidences: list[float], correctness: list[float], *, bins: int = 10) -> float:
    total = float(len(confidences))
    ece = 0.0
    for bin_index in range(bins):
        low = bin_index / float(bins)
        high = (bin_index + 1) / float(bins)
        if bin_index == bins - 1:
            indices = [index for index, value in enumerate(confidences) if low <= value <= high]
        else:
            indices = [index for index, value in enumerate(confidences) if low <= value < high]
        if not indices:
            continue
        avg_confidence = float(np.mean([confidences[index] for index in indices]))
        avg_accuracy = float(np.mean([correctness[index] for index in indices]))
        ece += (len(indices) / total) * abs(avg_confidence - avg_accuracy)
    return float(ece)


def select_position_scale(
    validation_rows: list[Stage10Example],
    method_name: str,
    *,
    candidate_scales: tuple[float, ...] = DEFAULT_POSITION_SCALES,
) -> dict[str, Any]:
    scored = []
    for scale in candidate_scales:
        metrics = evaluate_copy_decoder(validation_rows, method_name, scale)
        scored.append({"position_scale": scale, "metrics": metrics})
    selected = sorted(
        scored,
        key=lambda item: (
            item["metrics"]["top1_accuracy"],
            item["metrics"]["mrr"],
            item["metrics"]["mean_target_probability"],
            -item["metrics"]["loss"],
            -item["position_scale"],
        ),
        reverse=True,
    )[0]
    return {
        "selected_position_scale": selected["position_scale"],
        "candidate_scales": list(candidate_scales),
        "validation_selection_metrics": selected["metrics"],
    }


def _metric_names(split: str) -> tuple[str, ...]:
    return (
        f"{split}_loss",
        f"{split}_perplexity",
        f"{split}_top1_accuracy",
        f"{split}_mrr",
        f"{split}_mean_target_probability",
        f"{split}_mean_top1_confidence",
        f"{split}_expected_calibration_error",
    )


def _bootstrap_ci(values: list[float], *, seed_text: str, iterations: int = 400) -> dict[str, float]:
    rng = random.Random(int(hashlib.sha256(seed_text.encode("utf-8")).hexdigest()[:16], 16))
    means: list[float] = []
    for _ in range(iterations):
        sample = [values[rng.randrange(len(values))] for _ in range(len(values))]
        means.append(float(sum(sample) / len(sample)))
    means.sort()
    return {"low": round(means[int(0.025 * (iterations - 1))], 6), "high": round(means[int(0.975 * (iterations - 1))], 6)}


def _aggregate(run_table: list[dict[str, Any]], failed_runs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    aggregate_table: list[dict[str, Any]] = []
    for task_name in TASK_NAMES:
        for method_name in METHOD_NAMES:
            rows = [row for row in run_table if row["task"] == task_name and row["method"] == method_name]
            if not rows:
                continue
            record: dict[str, Any] = {
                "task": task_name,
                "method": method_name,
                "seed_count": len(rows),
                "failed_run_count": len([run for run in failed_runs if run["task"] == task_name and run["method"] == method_name]),
                "selected_position_scale_mean": round(float(np.mean([row["selected_position_scale"] for row in rows])), 6),
            }
            for metric_name in _metric_names("train") + _metric_names("validation") + _metric_names("test"):
                values = [float(row[metric_name]) for row in rows]
                ci = _bootstrap_ci(values, seed_text=f"stage49:{task_name}:{method_name}:{metric_name}")
                record[f"{metric_name}_mean"] = round(float(np.mean(values)), 6)
                record[f"{metric_name}_ci_low"] = ci["low"]
                record[f"{metric_name}_ci_high"] = ci["high"]
            aggregate_table.append(record)
    return aggregate_table


def _best_row(rows: list[dict[str, Any]], *, task_name: str, split: str = "test") -> dict[str, Any]:
    return sorted(
        [row for row in rows if row["task"] == task_name],
        key=lambda row: (
            row[f"{split}_top1_accuracy_mean"],
            row[f"{split}_mrr_mean"],
            row[f"{split}_mean_target_probability_mean"],
            -row[f"{split}_loss_mean"],
            row["method"],
        ),
        reverse=True,
    )[0]


def _decision(aggregate_table: list[dict[str, Any]]) -> dict[str, Any]:
    best_by_retrieval_task = {task: _best_row(aggregate_table, task_name=task) for task in RETRIEVAL_TASKS}
    retrieval_repaired_tasks = [
        task for task, row in best_by_retrieval_task.items() if row["test_top1_accuracy_mean"] >= RETRIEVAL_REPAIR_TOP1_THRESHOLD
    ]
    phasewrap_repaired_tasks = [
        task for task in retrieval_repaired_tasks if best_by_retrieval_task[task]["method"].startswith("phasewrap")
    ]
    tiny_best = _best_row(aggregate_table, task_name=TINY_TEXT_TASK)
    if len(retrieval_repaired_tasks) == len(RETRIEVAL_TASKS):
        decision = "COPY_DECODER_REPAIRS_RETRIEVAL_REVIEW_METHOD_ORDERING"
        boundary = "Copy-output repair makes retrieval generalize, so the one-block learned-vocab failure was partly an output bottleneck; this is still not production transformer evidence."
    elif retrieval_repaired_tasks:
        decision = "COPY_DECODER_PARTIALLY_REPAIRS_RETRIEVAL"
        boundary = "Copy-output repair helps at least one retrieval lane but does not solve the full retrieval set."
    else:
        decision = "COPY_DECODER_RETRIEVAL_REPAIR_FAILED"
        boundary = "Even with a copy-output repair, retrieval generalization is not established."
    return {
        "decision": decision,
        "retrieval_repair_top1_threshold": RETRIEVAL_REPAIR_TOP1_THRESHOLD,
        "retrieval_repaired_tasks": retrieval_repaired_tasks,
        "phasewrap_repaired_tasks": phasewrap_repaired_tasks,
        "retrieval_best_methods": {task: row["method"] for task, row in best_by_retrieval_task.items()},
        "retrieval_best_top1": {task: row["test_top1_accuracy_mean"] for task, row in best_by_retrieval_task.items()},
        "retrieval_best_target_probability": {task: row["test_mean_target_probability_mean"] for task, row in best_by_retrieval_task.items()},
        "tiny_text_best_method": tiny_best["method"],
        "tiny_text_best_top1": tiny_best["test_top1_accuracy_mean"],
        "tiny_text_best_target_probability": tiny_best["test_mean_target_probability_mean"],
        "claim_boundary": boundary,
    }


def _claim_boundary() -> dict[str, list[str]]:
    return {
        "supported": [
            "A matched copy-decoder repair audit over the Stage 45-48 train-short/test-long rows.",
            "Evidence about whether retrieval failure persists after replacing the learned vocab output with copied prefix-token mass.",
            "Validation-selected positional scale, five-seed aggregation, calibration metrics, and failed-run retention across the fair method set.",
        ],
        "excluded": [
            "production transformer superiority",
            "full transformer-scale validation",
            "a claim that PhaseWrap-RoPE replaces RoPE",
            "a claim that a copy-output repair is equivalent to free learned value generation",
            "broad quantum advantage",
        ],
    }


def run_stage49_audit(
    *,
    seeds: tuple[int, ...] = DEFAULT_AUDIT_SEEDS,
    examples_per_length: int = DEFAULT_EXAMPLES_PER_LENGTH,
    method_names: tuple[str, ...] = METHOD_NAMES,
    candidate_scales: tuple[float, ...] = DEFAULT_POSITION_SCALES,
) -> dict[str, Any]:
    splits_by_task = make_stage10_splits(seeds=seeds, examples_per_length=examples_per_length)
    run_table: list[dict[str, Any]] = []
    failed_runs: list[dict[str, Any]] = []
    for task_name, splits in splits_by_task.items():
        for seed in seeds:
            train_rows = [row for row in splits["train"] if row.seed == seed]
            validation_rows = [row for row in splits["validation"] if row.seed == seed]
            test_rows = [row for row in splits["test"] if row.seed == seed]
            for method_name in method_names:
                try:
                    selection = select_position_scale(validation_rows, method_name, candidate_scales=candidate_scales)
                    scale = float(selection["selected_position_scale"])
                    row: dict[str, Any] = {
                        "task": task_name,
                        "seed": seed,
                        "method": method_name,
                        "stage10_method_alias": _stage10_method_name(method_name),
                        "selected_position_scale": scale,
                        "candidate_scales": list(candidate_scales),
                        "selection_split": "validation",
                        "train_row_count": len(train_rows),
                        "validation_row_count": len(validation_rows),
                        "test_row_count": len(test_rows),
                    }
                    for split_name, split_rows in (("train", train_rows), ("validation", validation_rows), ("test", test_rows)):
                        metrics = evaluate_copy_decoder(split_rows, method_name, scale)
                        for metric_name, value in metrics.items():
                            if metric_name != "row_count":
                                row[f"{split_name}_{metric_name}"] = value
                    run_table.append(row)
                except Exception as exc:  # pragma: no cover - retained for artifact completeness.
                    failed_runs.append({"task": task_name, "seed": seed, "method": method_name, "error": str(exc)})
    aggregate_table = _aggregate(run_table, failed_runs)
    ranking_table = sorted(
        aggregate_table,
        key=lambda row: (
            row["task"],
            row["test_top1_accuracy_mean"],
            row["test_mrr_mean"],
            row["test_mean_target_probability_mean"],
            -row["test_loss_mean"],
            row["method"],
        ),
        reverse=True,
    )
    return {
        "schema_version": STAGE49_SCHEMA_VERSION,
        "stage": "stage49_copy_decoder_retrieval_repair_audit",
        "status": "completed",
        "dataset": "synthetic_small_decoder_train_short_test_long_v1",
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "source_rows": "stage10/stage45 matched decoder-only rows",
        "source_failure": "stages45_48_one_block_learned_vocab_output_failed_retrieval_generalization",
        "method_names": list(method_names),
        "tasks": list(TASK_NAMES),
        "seeds": list(seeds),
        "train_lengths": list(TRAIN_LENGTHS),
        "validation_lengths": list(VALIDATION_LENGTHS),
        "test_lengths": list(TEST_LENGTHS),
        "examples_per_length": examples_per_length,
        "candidate_position_scales": list(candidate_scales),
        "model": {
            "type": "single_query_copy_decoder_retrieval_repair",
            "value_output_mode": "copy_attention_mass_to_observed_prefix_token_ids",
            "content_signal": "tiny_text_fact_qa uses query entity to score matching fact spans; retrieval lanes use positional mechanism only",
            "trained_parameters": "none; positional scale selected on validation split",
        },
        "claim_boundary": _claim_boundary(),
        "failed_runs": failed_runs,
        "run_table": run_table,
        "aggregate_table": aggregate_table,
        "ranking_table": ranking_table,
        "decision": _decision(aggregate_table),
    }


def write_stage49_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "dataset": result["dataset"],
        "no_hardware_submission": result["no_hardware_submission"],
        "provider_credentials_required": result["provider_credentials_required"],
        "method_names": result["method_names"],
        "tasks": result["tasks"],
        "result_path": str((output_dir / "results.json").as_posix()),
        "summary_csv_path": str((output_dir / "summary.csv").as_posix()),
        "per_run_csv_path": str((output_dir / "per_run_results.csv").as_posix()),
        "failed_runs_path": str((output_dir / "failed_runs.json").as_posix()),
        "decision": result["decision"],
        "claim_boundary": result["claim_boundary"],
    }
    paths = {
        "manifest": str(output_dir / "manifest.json"),
        "result": str(output_dir / "results.json"),
        "summary_csv": str(output_dir / "summary.csv"),
        "per_run_csv": str(output_dir / "per_run_results.csv"),
        "failed_runs": str(output_dir / "failed_runs.json"),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "failed_runs.json").write_text(json.dumps(result["failed_runs"], indent=2, sort_keys=True), encoding="utf-8")
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(result["aggregate_table"][0].keys()))
        writer.writeheader()
        writer.writerows(result["aggregate_table"])
    with (output_dir / "per_run_results.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(result["run_table"][0].keys()))
        writer.writeheader()
        writer.writerows(result["run_table"])
    return paths


def print_stage49_summary(result: dict[str, Any]) -> None:
    columns = (
        "task",
        "method",
        "seed_count",
        "failed_run_count",
        "selected_position_scale_mean",
        "test_top1_accuracy_mean",
        "test_mrr_mean",
        "test_mean_target_probability_mean",
        "test_expected_calibration_error_mean",
    )
    print(" | ".join(columns))
    print(" | ".join("---" for _ in columns))
    for row in result["ranking_table"]:
        print(" | ".join(str(row[column]) for column in columns))
    print(f"decision: {result['decision']['decision']}")
    print(f"claim_boundary: {result['decision']['claim_boundary']}")
