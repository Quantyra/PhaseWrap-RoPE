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
    TRAIN_LENGTHS,
    VALIDATION_LENGTHS,
    VOCAB_SIZE,
    Stage10Example,
    _expected_calibration_error,
    make_stage10_splits,
    positional_bias,
)
from .stage45_matched_decoder_only_gate import METHOD_NAMES, _stage10_method_name
from .stage52_two_block_decoder_feasibility_audit import GENERALIZATION_TOP1_THRESHOLD, RETRIEVAL_TASKS, TINY_TEXT_TASK


STAGE55_SCHEMA_VERSION = "qrope_stage55_row_metadata_cue_copy_upper_bound_audit_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage55_row_metadata_cue_copy_upper_bound_audit"
DEFAULT_AUDIT_SEEDS = DEFAULT_SEEDS
DEFAULT_EXAMPLES_PER_LENGTH = 2
DEFAULT_POSITION_SCALES = (0.0, 0.5, 1.0, 2.0, 4.0, 8.0, 12.0)
DEFAULT_CUE_SCALES = (0.0, 1.0, 2.0, 4.0, 8.0, 12.0, 16.0, 24.0)
DEFAULT_DISTANCE_SCALES = (-8.0, -4.0, -2.0, -1.0, 0.0, 1.0, 2.0, 4.0, 8.0)


def _claim_boundary() -> dict[str, list[str]]:
    return {
        "supported": [
            "A transparent row-metadata cue-copy upper-bound audit over the Stage 52-54 row family.",
            "Evidence about whether the retrieval rows are solvable when the target-distance/congruence cue is explicitly exposed.",
            "Fair reporting across the same RoPE/ALiBI/sinusoidal/no-position/PhaseWrap method set, with failed-run retention.",
        ],
        "excluded": [
            "production transformer superiority",
            "full transformer-scale validation",
            "a claim that PhaseWrap-RoPE replaces RoPE",
            "a claim that explicit row metadata is a standard decoder-only input feature",
            "a claim that this upper bound is positional-method promotion evidence",
            "broad quantum advantage",
        ],
    }


def _softmax(values: np.ndarray) -> np.ndarray:
    shifted = values - np.max(values)
    exp_values = np.exp(shifted)
    return exp_values / np.sum(exp_values)


def build_blocked_result(*, reason: str = "unexpected_preflight_block") -> dict[str, Any]:
    return {
        "schema_version": STAGE55_SCHEMA_VERSION,
        "stage": "stage55_row_metadata_cue_copy_upper_bound_audit",
        "status": "blocked",
        "blocked_reason": reason,
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "method_names": list(METHOD_NAMES),
        "tasks": list(TASK_NAMES),
        "seeds": list(DEFAULT_AUDIT_SEEDS),
        "claim_boundary": _claim_boundary(),
    }


def _cue_logits(row: Stage10Example, *, cue_scale: float, distance_scale: float) -> np.ndarray:
    distances = np.array([row.query_pos - index for index in range(row.query_pos)], dtype=float)
    exact_distance = (distances == float(row.reference_delta)).astype(float)
    phase_congruent = (((distances - float(row.reference_delta)) % 24.0) == 0.0).astype(float)
    farthest_prior = distances / max(1.0, float(row.query_pos))
    return cue_scale * (exact_distance + phase_congruent) + distance_scale * farthest_prior


def _copy_distribution(
    row: Stage10Example,
    method_name: str,
    *,
    position_scale: float,
    cue_scale: float,
    distance_scale: float,
) -> np.ndarray:
    stage10_method = _stage10_method_name(method_name)
    logits = position_scale * np.asarray(positional_bias(row, stage10_method), dtype=float)
    logits = logits + _cue_logits(row, cue_scale=cue_scale, distance_scale=distance_scale)
    attention = _softmax(logits)
    values = np.zeros(VOCAB_SIZE, dtype=float)
    np.add.at(values, np.array(row.tokens[: row.query_pos], dtype=int), attention)
    return values


def _ranked_indices(values: np.ndarray) -> list[int]:
    return sorted(range(len(values)), key=lambda index: (-float(values[index]), index))


def evaluate_cue_copy_decoder(
    rows: list[Stage10Example],
    method_name: str,
    *,
    position_scale: float,
    cue_scale: float,
    distance_scale: float,
) -> dict[str, float]:
    losses: list[float] = []
    reciprocal_ranks: list[float] = []
    top1_hits: list[float] = []
    target_probs: list[float] = []
    top1_confidences: list[float] = []
    for row in rows:
        values = _copy_distribution(
            row,
            method_name,
            position_scale=position_scale,
            cue_scale=cue_scale,
            distance_scale=distance_scale,
        )
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


def select_cue_copy_scales(
    validation_rows: list[Stage10Example],
    method_name: str,
    *,
    position_scales: tuple[float, ...] = DEFAULT_POSITION_SCALES,
    cue_scales: tuple[float, ...] = DEFAULT_CUE_SCALES,
    distance_scales: tuple[float, ...] = DEFAULT_DISTANCE_SCALES,
) -> dict[str, Any]:
    scored: list[dict[str, Any]] = []
    for position_scale in position_scales:
        for cue_scale in cue_scales:
            for distance_scale in distance_scales:
                metrics = evaluate_cue_copy_decoder(
                    validation_rows,
                    method_name,
                    position_scale=position_scale,
                    cue_scale=cue_scale,
                    distance_scale=distance_scale,
                )
                scored.append(
                    {
                        "position_scale": position_scale,
                        "cue_scale": cue_scale,
                        "distance_scale": distance_scale,
                        "metrics": metrics,
                    }
                )
    selected = sorted(
        scored,
        key=lambda item: (
            item["metrics"]["top1_accuracy"],
            item["metrics"]["mrr"],
            item["metrics"]["mean_target_probability"],
            -item["metrics"]["loss"],
            -abs(item["position_scale"]),
            -abs(item["cue_scale"]),
            -abs(item["distance_scale"]),
        ),
        reverse=True,
    )[0]
    return {
        "selected_position_scale": selected["position_scale"],
        "selected_cue_scale": selected["cue_scale"],
        "selected_distance_scale": selected["distance_scale"],
        "candidate_position_scales": list(position_scales),
        "candidate_cue_scales": list(cue_scales),
        "candidate_distance_scales": list(distance_scales),
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
                "selected_cue_scale_mean": round(float(np.mean([row["selected_cue_scale"] for row in rows])), 6),
                "selected_distance_scale_mean": round(float(np.mean([row["selected_distance_scale"] for row in rows])), 6),
            }
            for metric_name in _metric_names("train") + _metric_names("validation") + _metric_names("test"):
                values = [float(row[metric_name]) for row in rows]
                ci = _bootstrap_ci(values, seed_text=f"stage55:{task_name}:{method_name}:{metric_name}")
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
    retrieval_best = {task: _best_row(aggregate_table, task_name=task) for task in RETRIEVAL_TASKS}
    retrieval_solved = [
        task for task, row in retrieval_best.items() if row["test_top1_accuracy_mean"] >= GENERALIZATION_TOP1_THRESHOLD
    ]
    no_position_solved = [
        task
        for task in RETRIEVAL_TASKS
        for row in aggregate_table
        if row["task"] == task and row["method"] == "no_position" and row["test_top1_accuracy_mean"] >= GENERALIZATION_TOP1_THRESHOLD
    ]
    phasewrap_best = [task for task, row in retrieval_best.items() if row["method"].startswith("phasewrap")]
    if len(retrieval_solved) == len(RETRIEVAL_TASKS) and len(no_position_solved) == len(RETRIEVAL_TASKS):
        decision = "ROW_METADATA_CUE_COPY_UPPER_BOUND_SOLVES_RETRIEVAL_NOT_PROMOTION"
        boundary = "Explicit row-metadata cue-copy features solve retrieval, including no-position; this proves row-family solvability but is not positional-method promotion evidence."
    elif retrieval_solved:
        decision = "ROW_METADATA_CUE_COPY_PARTIAL_RETRIEVAL_UPPER_BOUND"
        boundary = "Explicit row-metadata cue-copy features solve at least one retrieval lane, but not the full retrieval set."
    else:
        decision = "ROW_METADATA_CUE_COPY_UPPER_BOUND_FAILED"
        boundary = "Even explicit row-metadata cue-copy features do not solve retrieval."
    tiny_best = _best_row(aggregate_table, task_name=TINY_TEXT_TASK)
    return {
        "decision": decision,
        "generalization_top1_threshold": GENERALIZATION_TOP1_THRESHOLD,
        "retrieval_solved_tasks": retrieval_solved,
        "no_position_solved_retrieval_tasks": no_position_solved,
        "phasewrap_best_retrieval_tasks": phasewrap_best,
        "retrieval_best_methods": {task: row["method"] for task, row in retrieval_best.items()},
        "retrieval_best_top1": {task: row["test_top1_accuracy_mean"] for task, row in retrieval_best.items()},
        "retrieval_best_target_probability": {task: row["test_mean_target_probability_mean"] for task, row in retrieval_best.items()},
        "tiny_text_best_method": tiny_best["method"],
        "tiny_text_best_top1": tiny_best["test_top1_accuracy_mean"],
        "claim_boundary": boundary,
    }


def run_stage55_audit(
    *,
    seeds: tuple[int, ...] = DEFAULT_AUDIT_SEEDS,
    examples_per_length: int = DEFAULT_EXAMPLES_PER_LENGTH,
    method_names: tuple[str, ...] = METHOD_NAMES,
    position_scales: tuple[float, ...] = DEFAULT_POSITION_SCALES,
    cue_scales: tuple[float, ...] = DEFAULT_CUE_SCALES,
    distance_scales: tuple[float, ...] = DEFAULT_DISTANCE_SCALES,
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
                    selected = select_cue_copy_scales(
                        validation_rows,
                        method_name,
                        position_scales=position_scales,
                        cue_scales=cue_scales,
                        distance_scales=distance_scales,
                    )
                    row: dict[str, Any] = {
                        "task": task_name,
                        "seed": seed,
                        "method": method_name,
                        "stage10_method_alias": _stage10_method_name(method_name),
                        "train_row_count": len(train_rows),
                        "validation_row_count": len(validation_rows),
                        "test_row_count": len(test_rows),
                        "selected_position_scale": selected["selected_position_scale"],
                        "selected_cue_scale": selected["selected_cue_scale"],
                        "selected_distance_scale": selected["selected_distance_scale"],
                        "validation_selection_metrics": selected["validation_selection_metrics"],
                    }
                    for split_name, split_rows in (("train", train_rows), ("validation", validation_rows), ("test", test_rows)):
                        metrics = evaluate_cue_copy_decoder(
                            split_rows,
                            method_name,
                            position_scale=selected["selected_position_scale"],
                            cue_scale=selected["selected_cue_scale"],
                            distance_scale=selected["selected_distance_scale"],
                        )
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
            row["method"],
        ),
        reverse=True,
    )
    return {
        "schema_version": STAGE55_SCHEMA_VERSION,
        "stage": "stage55_row_metadata_cue_copy_upper_bound_audit",
        "status": "completed",
        "dataset": "synthetic_small_decoder_train_short_test_long_v1",
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "source_rows": "stage10/stage45 matched decoder-only rows",
        "source_stage": "stage54_attention_supervised_two_block_audit",
        "method_names": list(method_names),
        "tasks": list(TASK_NAMES),
        "seeds": list(seeds),
        "train_lengths": list(TRAIN_LENGTHS),
        "validation_lengths": list(VALIDATION_LENGTHS),
        "test_lengths": list(TEST_LENGTHS),
        "examples_per_length": examples_per_length,
        "model": {
            "type": "row_metadata_cue_copy_upper_bound",
            "value_output_mode": "deterministic copied prefix-token mass",
            "explicit_nonstandard_features": [
                "row.reference_delta exact-distance match",
                "row.reference_delta modulo-24 congruence",
                "normalized distance/farthest-position prior",
            ],
            "promotion_status": "diagnostic upper bound only",
        },
        "candidate_position_scales": list(position_scales),
        "candidate_cue_scales": list(cue_scales),
        "candidate_distance_scales": list(distance_scales),
        "claim_boundary": _claim_boundary(),
        "failed_runs": failed_runs,
        "run_table": run_table,
        "aggregate_table": aggregate_table,
        "ranking_table": ranking_table,
        "decision": _decision(aggregate_table),
    }


def write_stage55_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    result_name = "results.json" if result["status"] == "completed" else "preflight.json"
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "status": result["status"],
        "no_hardware_submission": result["no_hardware_submission"],
        "provider_credentials_required": result["provider_credentials_required"],
        "method_names": result["method_names"],
        "tasks": result["tasks"],
        "result_path": str((output_dir / result_name).as_posix()),
        "summary_csv_path": str((output_dir / "summary.csv").as_posix()),
        "per_run_csv_path": str((output_dir / "per_run_results.csv").as_posix()) if result["status"] == "completed" else None,
        "failed_runs_path": str((output_dir / "failed_runs.json").as_posix()) if result["status"] == "completed" else None,
        "decision": result.get("decision"),
        "claim_boundary": result.get("claim_boundary", {}),
    }
    paths = {"manifest": str(output_dir / "manifest.json"), "result": str(output_dir / result_name), "summary_csv": str(output_dir / "summary.csv")}
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / result_name).write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    if result["status"] != "completed":
        with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=("stage", "status", "blocked_reason"))
            writer.writeheader()
            writer.writerow({"stage": result["stage"], "status": result["status"], "blocked_reason": result.get("blocked_reason", "")})
        return paths
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(result["aggregate_table"][0].keys()))
        writer.writeheader()
        writer.writerows(result["aggregate_table"])
    with (output_dir / "per_run_results.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(result["run_table"][0].keys()))
        writer.writeheader()
        writer.writerows(result["run_table"])
    (output_dir / "failed_runs.json").write_text(json.dumps(result["failed_runs"], indent=2, sort_keys=True), encoding="utf-8")
    paths["per_run_csv"] = str(output_dir / "per_run_results.csv")
    paths["failed_runs"] = str(output_dir / "failed_runs.json")
    return paths


def print_stage55_summary(result: dict[str, Any]) -> None:
    if result["status"] != "completed":
        print("stage | status | blocked_reason")
        print("--- | --- | ---")
        print(" | ".join((result["stage"], result["status"], result.get("blocked_reason", ""))))
        return
    columns = (
        "task",
        "method",
        "seed_count",
        "failed_run_count",
        "selected_cue_scale_mean",
        "selected_distance_scale_mean",
        "test_top1_accuracy_mean",
        "test_mean_target_probability_mean",
    )
    print(" | ".join(columns))
    print(" | ".join("---" for _ in columns))
    for row in result["ranking_table"]:
        print(" | ".join(str(row[column]) for column in columns))
    print(f"decision: {result['decision']['decision']}")
    print(f"claim_boundary: {result['decision']['claim_boundary']}")
