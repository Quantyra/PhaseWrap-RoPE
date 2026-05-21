from __future__ import annotations

import csv
import json
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
from .stage52_two_block_decoder_feasibility_audit import GENERALIZATION_TOP1_THRESHOLD, RETRIEVAL_TASKS, TINY_TEXT_TASK
from .stage55_row_metadata_cue_copy_upper_bound_audit import (
    DEFAULT_CUE_SCALES,
    DEFAULT_DISTANCE_SCALES,
    DEFAULT_POSITION_SCALES,
    _aggregate,
    _best_row,
    _claim_boundary as _stage55_claim_boundary,
    _ranked_indices,
    _softmax,
)


STAGE56_SCHEMA_VERSION = "qrope_stage56_standard_input_cue_copy_audit_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage56_standard_input_cue_copy_audit"
DEFAULT_AUDIT_SEEDS = DEFAULT_SEEDS
DEFAULT_EXAMPLES_PER_LENGTH = 2


def _claim_boundary() -> dict[str, list[str]]:
    return {
        "supported": [
            "A standard-input cue-copy diagnostic over the Stage 52-55 row family.",
            "Evidence about how much of the Stage 55 metadata upper bound survives when cues are decoded only from visible tokens.",
            "Fair reporting across the same RoPE/ALiBI/sinusoidal/no-position/PhaseWrap method set, with failed-run retention.",
        ],
        "excluded": [
            "production transformer superiority",
            "full transformer-scale validation",
            "a claim that PhaseWrap-RoPE replaces RoPE",
            "a claim that visible query-token cue decoding is a learned decoder-only transformer result",
            "a claim that this deterministic cue-copy diagnostic is positional-method promotion evidence",
            "broad quantum advantage",
        ],
    }


def build_blocked_result(*, reason: str = "unexpected_preflight_block") -> dict[str, Any]:
    return {
        "schema_version": STAGE56_SCHEMA_VERSION,
        "stage": "stage56_standard_input_cue_copy_audit",
        "status": "blocked",
        "blocked_reason": reason,
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "method_names": list(METHOD_NAMES),
        "tasks": list(TASK_NAMES),
        "seeds": list(DEFAULT_AUDIT_SEEDS),
        "claim_boundary": _claim_boundary(),
    }


def _standard_input_cue_logits(row: Stage10Example, *, cue_scale: float, distance_scale: float) -> np.ndarray:
    distances = np.array([row.query_pos - index for index in range(row.query_pos)], dtype=float)
    logits = np.zeros(row.query_pos, dtype=float)
    if row.task == TINY_TEXT_TASK:
        query_tokens = row.tokens[max(0, row.query_pos - 4) : row.query_pos + 1]
        entity_ids = [token for token in query_tokens if 87 <= token < 96]
        if not entity_ids:
            return logits
        entity_id = int(entity_ids[0])
        for index in range(3, row.query_pos):
            if (
                row.tokens[index - 3] == TEXT_TOKEN_IDS["fact"]
                and row.tokens[index - 2] == entity_id
                and row.tokens[index - 1] == TEXT_TOKEN_IDS["is"]
            ):
                logits[index] += cue_scale
        return logits
    reference_delta_mod16 = (VOCAB_SIZE - 1 - row.tokens[row.query_pos]) % 16
    exact_mod16 = (distances == float(reference_delta_mod16)).astype(float)
    congruent_mod16 = (((distances - float(reference_delta_mod16)) % 16.0) == 0.0).astype(float)
    farthest_prior = distances / max(1.0, float(row.query_pos))
    return cue_scale * (exact_mod16 + congruent_mod16) + distance_scale * farthest_prior


def _copy_distribution(
    row: Stage10Example,
    method_name: str,
    *,
    position_scale: float,
    cue_scale: float,
    distance_scale: float,
) -> np.ndarray:
    logits = position_scale * np.asarray(positional_bias(row, _stage10_method_name(method_name)), dtype=float)
    logits = logits + _standard_input_cue_logits(row, cue_scale=cue_scale, distance_scale=distance_scale)
    attention = _softmax(logits)
    values = np.zeros(VOCAB_SIZE, dtype=float)
    np.add.at(values, np.array(row.tokens[: row.query_pos], dtype=int), attention)
    return values


def evaluate_standard_input_cue_copy(
    rows: list[Stage10Example],
    method_name: str,
    *,
    position_scale: float,
    cue_scale: float,
    distance_scale: float,
) -> dict[str, float]:
    from .stage49_copy_decoder_retrieval_repair_audit import _expected_calibration_error

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
        losses.append(-np.log(max(target_probability, 1e-12)))
        reciprocal_ranks.append(1.0 / float(rank))
        top1_hits.append(top1_correct)
        target_probs.append(target_probability)
        top1_confidences.append(float(values[top1_token]))
    mean_loss = float(np.mean(losses))
    return {
        "row_count": float(len(rows)),
        "loss": round(mean_loss, 6),
        "perplexity": round(float(np.exp(mean_loss)), 6),
        "top1_accuracy": round(float(np.mean(top1_hits)), 6),
        "mrr": round(float(np.mean(reciprocal_ranks)), 6),
        "mean_target_probability": round(float(np.mean(target_probs)), 6),
        "mean_top1_confidence": round(float(np.mean(top1_confidences)), 6),
        "expected_calibration_error": round(_expected_calibration_error(top1_confidences, top1_hits), 6),
    }


def _select_scales(
    validation_rows: list[Stage10Example],
    method_name: str,
    *,
    position_scales: tuple[float, ...],
    cue_scales: tuple[float, ...],
    distance_scales: tuple[float, ...],
) -> dict[str, Any]:
    scored: list[dict[str, Any]] = []
    for position_scale in position_scales:
        for cue_scale in cue_scales:
            for distance_scale in distance_scales:
                metrics = evaluate_standard_input_cue_copy(
                    validation_rows,
                    method_name,
                    position_scale=position_scale,
                    cue_scale=cue_scale,
                    distance_scale=distance_scale,
                )
                scored.append({"position_scale": position_scale, "cue_scale": cue_scale, "distance_scale": distance_scale, "metrics": metrics})
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
        "validation_selection_metrics": selected["metrics"],
    }


def _decision(aggregate_table: list[dict[str, Any]]) -> dict[str, Any]:
    retrieval_best = {task: _best_row(aggregate_table, task_name=task) for task in RETRIEVAL_TASKS}
    retrieval_solved = [task for task, row in retrieval_best.items() if row["test_top1_accuracy_mean"] >= GENERALIZATION_TOP1_THRESHOLD]
    phasewrap_best = [task for task, row in retrieval_best.items() if row["method"].startswith("phasewrap")]
    if len(retrieval_solved) == len(RETRIEVAL_TASKS):
        decision = "STANDARD_INPUT_CUE_COPY_SOLVES_RETRIEVAL_REVIEW_REQUIRED"
        boundary = "Visible-token cue-copy features solve all retrieval lanes; review method ordering before any next gate."
    elif retrieval_solved:
        decision = "STANDARD_INPUT_CUE_COPY_PARTIAL_RETRIEVAL"
        boundary = "Visible-token cue-copy features solve at least one retrieval lane but not the full retrieval set."
    else:
        decision = "STANDARD_INPUT_CUE_COPY_RETRIEVAL_FAILED"
        boundary = "Visible-token cue-copy features do not preserve the Stage 55 metadata upper-bound retrieval repair."
    tiny_best = _best_row(aggregate_table, task_name=TINY_TEXT_TASK)
    return {
        "decision": decision,
        "generalization_top1_threshold": GENERALIZATION_TOP1_THRESHOLD,
        "retrieval_solved_tasks": retrieval_solved,
        "phasewrap_best_retrieval_tasks": phasewrap_best,
        "retrieval_best_methods": {task: row["method"] for task, row in retrieval_best.items()},
        "retrieval_best_top1": {task: row["test_top1_accuracy_mean"] for task, row in retrieval_best.items()},
        "retrieval_best_target_probability": {task: row["test_mean_target_probability_mean"] for task, row in retrieval_best.items()},
        "tiny_text_best_method": tiny_best["method"],
        "tiny_text_best_top1": tiny_best["test_top1_accuracy_mean"],
        "claim_boundary": boundary,
    }


def run_stage56_audit(
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
                    selected = _select_scales(validation_rows, method_name, position_scales=position_scales, cue_scales=cue_scales, distance_scales=distance_scales)
                    row: dict[str, Any] = {
                        "task": task_name,
                        "seed": seed,
                        "method": method_name,
                        "stage10_method_alias": _stage10_method_name(method_name),
                        "train_row_count": len(train_rows),
                        "validation_row_count": len(validation_rows),
                        "test_row_count": len(test_rows),
                        **selected,
                    }
                    for split_name, split_rows in (("train", train_rows), ("validation", validation_rows), ("test", test_rows)):
                        metrics = evaluate_standard_input_cue_copy(
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
                except Exception as exc:  # pragma: no cover
                    failed_runs.append({"task": task_name, "seed": seed, "method": method_name, "error": str(exc)})
    aggregate_table = _aggregate(run_table, failed_runs)
    ranking_table = sorted(
        aggregate_table,
        key=lambda row: (row["task"], row["test_top1_accuracy_mean"], row["test_mrr_mean"], row["test_mean_target_probability_mean"], row["method"]),
        reverse=True,
    )
    return {
        "schema_version": STAGE56_SCHEMA_VERSION,
        "stage": "stage56_standard_input_cue_copy_audit",
        "status": "completed",
        "dataset": "synthetic_small_decoder_train_short_test_long_v1",
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "source_rows": "stage10/stage45 matched decoder-only rows",
        "source_stage": "stage55_row_metadata_cue_copy_upper_bound_audit",
        "method_names": list(method_names),
        "tasks": list(TASK_NAMES),
        "seeds": list(seeds),
        "train_lengths": list(TRAIN_LENGTHS),
        "validation_lengths": list(VALIDATION_LENGTHS),
        "test_lengths": list(TEST_LENGTHS),
        "examples_per_length": examples_per_length,
        "model": {
            "type": "standard_input_cue_copy_diagnostic",
            "value_output_mode": "deterministic copied prefix-token mass",
            "visible_cues": ["query token reference_delta modulo 16 for retrieval rows", "query entity tokens for tiny_text_fact_qa"],
            "metadata_excluded": ["row.reference_delta exact value", "row.target_pos", "row.target_delta"],
        },
        "claim_boundary": _claim_boundary(),
        "stage55_upper_bound_boundary": _stage55_claim_boundary(),
        "failed_runs": failed_runs,
        "run_table": run_table,
        "aggregate_table": aggregate_table,
        "ranking_table": ranking_table,
        "decision": _decision(aggregate_table),
    }


def write_stage56_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
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
        "failed_runs_path": str((output_dir / "failed_runs.json").as_posix()),
        "decision": result.get("decision"),
        "claim_boundary": result.get("claim_boundary", {}),
    }
    paths = {"manifest": str(output_dir / "manifest.json"), "result": str(output_dir / "results.json"), "summary_csv": str(output_dir / "summary.csv")}
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
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


def print_stage56_summary(result: dict[str, Any]) -> None:
    columns = ("task", "method", "seed_count", "failed_run_count", "test_top1_accuracy_mean", "test_mean_target_probability_mean")
    print(" | ".join(columns))
    print(" | ".join("---" for _ in columns))
    for row in result["ranking_table"]:
        print(" | ".join(str(row[column]) for column in columns))
    print(f"decision: {result['decision']['decision']}")
    print(f"claim_boundary: {result['decision']['claim_boundary']}")
