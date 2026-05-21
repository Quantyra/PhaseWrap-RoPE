from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from .stage10_small_decoder_transformer import DEFAULT_SEEDS, TASK_NAMES, TEXT_TOKEN_IDS, VOCAB_SIZE, Stage10Example, make_stage10_splits, positional_bias
from .stage45_matched_decoder_only_gate import METHOD_NAMES, _stage10_method_name
from .stage52_two_block_decoder_feasibility_audit import GENERALIZATION_TOP1_THRESHOLD, RETRIEVAL_TASKS, TINY_TEXT_TASK
from .stage55_row_metadata_cue_copy_upper_bound_audit import (
    DEFAULT_CUE_SCALES,
    DEFAULT_DISTANCE_SCALES,
    DEFAULT_POSITION_SCALES,
    _aggregate,
    _best_row,
    _ranked_indices,
    _softmax,
)
from .stage56_standard_input_cue_copy_audit import DEFAULT_EXAMPLES_PER_LENGTH, write_stage56_outputs
from .stage57_support_aware_query_cue_audit import print_stage57_summary


STAGE59_SCHEMA_VERSION = "qrope_stage59_seed_local_query_support_audit_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage59_seed_local_query_support_audit"
DEFAULT_AUDIT_SEEDS = DEFAULT_SEEDS


def _claim_boundary() -> dict[str, list[str]]:
    return {
        "supported": [
            "A seed-local query-token support-map diagnostic over the Stage 52-58 row family.",
            "Evidence about whether the Stage 58 pooled support lookup survives per-seed train-only recovery.",
            "Fair reporting across the same RoPE/ALiBI/sinusoidal/no-position/PhaseWrap method set, with failed-run retention.",
        ],
        "excluded": [
            "production transformer superiority",
            "full transformer-scale validation",
            "a claim that PhaseWrap-RoPE replaces RoPE",
            "a claim that a seed-local lookup map is a matched decoder-only transformer",
            "a claim that this deterministic cue-copy diagnostic is positional-method promotion evidence",
            "broad quantum advantage",
        ],
    }


def build_blocked_result(*, reason: str = "unexpected_preflight_block") -> dict[str, Any]:
    return {
        "schema_version": STAGE59_SCHEMA_VERSION,
        "stage": "stage59_seed_local_query_support_audit",
        "status": "blocked",
        "blocked_reason": reason,
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "method_names": list(METHOD_NAMES),
        "tasks": list(TASK_NAMES),
        "seeds": list(DEFAULT_AUDIT_SEEDS),
        "claim_boundary": _claim_boundary(),
    }


def _query_mod(row: Stage10Example) -> int:
    return int((VOCAB_SIZE - 1 - row.tokens[row.query_pos]) % 16)


def learn_query_support_map(train_rows: list[Stage10Example]) -> dict[int, int]:
    learned: dict[int, int] = {}
    for row in train_rows:
        if row.task == "phase_cued_retrieval":
            learned[_query_mod(row)] = int(row.reference_delta)
    return dict(sorted(learned.items()))


def _cue_logits(row: Stage10Example, *, learned_support: dict[int, int], cue_scale: float, distance_scale: float) -> np.ndarray:
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
    reference_delta = learned_support.get(_query_mod(row), _query_mod(row))
    exact_distance = (distances == float(reference_delta)).astype(float)
    phase_congruent = (((distances - float(reference_delta)) % 24.0) == 0.0).astype(float)
    farthest_prior = distances / max(1.0, float(row.query_pos))
    return cue_scale * (exact_distance + phase_congruent) + distance_scale * farthest_prior


def evaluate_seed_local_query_support(
    rows: list[Stage10Example],
    method_name: str,
    *,
    learned_support: dict[int, int],
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
        logits = position_scale * np.asarray(positional_bias(row, _stage10_method_name(method_name)), dtype=float)
        logits = logits + _cue_logits(row, learned_support=learned_support, cue_scale=cue_scale, distance_scale=distance_scale)
        attention = _softmax(logits)
        values = np.zeros(VOCAB_SIZE, dtype=float)
        np.add.at(values, np.array(row.tokens[: row.query_pos], dtype=int), attention)
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
    learned_support: dict[int, int],
    position_scales: tuple[float, ...],
    cue_scales: tuple[float, ...],
    distance_scales: tuple[float, ...],
) -> dict[str, Any]:
    scored: list[dict[str, Any]] = []
    for position_scale in position_scales:
        for cue_scale in cue_scales:
            for distance_scale in distance_scales:
                metrics = evaluate_seed_local_query_support(
                    validation_rows,
                    method_name,
                    learned_support=learned_support,
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


def _mean_phase_cued_test_coverage(phase_cued_coverage: dict[str, dict[str, dict[str, Any]]]) -> float:
    fractions = [float(seed_coverage["test"]["known_fraction"]) for seed_coverage in phase_cued_coverage.values()]
    return round(float(np.mean(fractions)), 6) if fractions else 0.0


def _decision(aggregate_table: list[dict[str, Any]], phase_cued_coverage: dict[str, dict[str, dict[str, Any]]]) -> dict[str, Any]:
    retrieval_best = {task: _best_row(aggregate_table, task_name=task) for task in RETRIEVAL_TASKS}
    retrieval_solved = [task for task, row in retrieval_best.items() if row["test_top1_accuracy_mean"] >= GENERALIZATION_TOP1_THRESHOLD]
    phase_cued_test_support_known_fraction = _mean_phase_cued_test_coverage(phase_cued_coverage)
    no_position_solved = [
        task
        for task in RETRIEVAL_TASKS
        for row in aggregate_table
        if row["task"] == task and row["method"] == "no_position" and row["test_top1_accuracy_mean"] >= GENERALIZATION_TOP1_THRESHOLD
    ]
    phasewrap_best = [task for task, row in retrieval_best.items() if row["method"].startswith("phasewrap")]
    if (
        len(retrieval_solved) == len(RETRIEVAL_TASKS)
        and "phase_cued_retrieval" in no_position_solved
        and phase_cued_test_support_known_fraction < 1.0
    ):
        decision = "SEED_LOCAL_QUERY_SUPPORT_PARTIAL_COVERAGE_SOLVES_NOT_PROMOTION"
        boundary = "Seed-local train lookup leaves held-out phase-cued support gaps, yet fallback cue decoding crosses the threshold and no-position solves too; this is not positional-method promotion."
    elif len(retrieval_solved) == len(RETRIEVAL_TASKS) and "phase_cued_retrieval" in no_position_solved:
        decision = "SEED_LOCAL_QUERY_SUPPORT_SOLVES_PHASE_CUED_NOT_PROMOTION"
        boundary = "A seed-local train lookup covers the support-aware query cue and solves phase-cued retrieval for no-position too; this is not positional-method promotion."
    elif retrieval_solved:
        decision = "SEED_LOCAL_QUERY_SUPPORT_PARTIAL_RETRIEVAL"
        boundary = "A seed-local train lookup solves at least one retrieval lane but not the full retrieval set."
    else:
        decision = "SEED_LOCAL_QUERY_SUPPORT_RETRIEVAL_FAILED"
        boundary = "A seed-local train lookup does not solve retrieval."
    tiny_best = _best_row(aggregate_table, task_name=TINY_TEXT_TASK)
    return {
        "decision": decision,
        "generalization_top1_threshold": GENERALIZATION_TOP1_THRESHOLD,
        "retrieval_solved_tasks": retrieval_solved,
        "no_position_solved_retrieval_tasks": no_position_solved,
        "phasewrap_best_retrieval_tasks": phasewrap_best,
        "phase_cued_test_support_known_fraction": phase_cued_test_support_known_fraction,
        "retrieval_best_methods": {task: row["method"] for task, row in retrieval_best.items()},
        "retrieval_best_top1": {task: row["test_top1_accuracy_mean"] for task, row in retrieval_best.items()},
        "retrieval_best_target_probability": {task: row["test_mean_target_probability_mean"] for task, row in retrieval_best.items()},
        "tiny_text_best_method": tiny_best["method"],
        "tiny_text_best_top1": tiny_best["test_top1_accuracy_mean"],
        "claim_boundary": boundary,
    }


def _support_coverage(rows: list[Stage10Example], learned_support: dict[int, int]) -> dict[str, Any]:
    query_mods = [_query_mod(row) for row in rows if row.task == "phase_cued_retrieval"]
    known = [query_mod for query_mod in query_mods if query_mod in learned_support]
    missing = sorted({query_mod for query_mod in query_mods if query_mod not in learned_support})
    total = len(query_mods)
    return {
        "known_count": len(known),
        "total_count": total,
        "known_fraction": round(float(len(known) / total), 6) if total else 1.0,
        "missing_query_mods": missing,
    }


def run_stage59_audit(
    *,
    seeds: tuple[int, ...] = DEFAULT_AUDIT_SEEDS,
    examples_per_length: int = DEFAULT_EXAMPLES_PER_LENGTH,
    method_names: tuple[str, ...] = METHOD_NAMES,
    position_scales: tuple[float, ...] = DEFAULT_POSITION_SCALES,
    cue_scales: tuple[float, ...] = DEFAULT_CUE_SCALES,
    distance_scales: tuple[float, ...] = DEFAULT_DISTANCE_SCALES,
) -> dict[str, Any]:
    splits_by_task = make_stage10_splits(seeds=seeds, examples_per_length=examples_per_length)
    learned_support_by_seed = {
        seed: learn_query_support_map([row for row in splits_by_task["phase_cued_retrieval"]["train"] if row.seed == seed])
        for seed in seeds
    }
    phase_cued_coverage = {
        str(seed): {
            split_name: _support_coverage([row for row in split_rows if row.seed == seed], learned_support_by_seed[seed])
            for split_name, split_rows in splits_by_task["phase_cued_retrieval"].items()
        }
        for seed in seeds
    }
    run_table: list[dict[str, Any]] = []
    failed_runs: list[dict[str, Any]] = []
    for task_name, splits in splits_by_task.items():
        for seed in seeds:
            learned_support = learned_support_by_seed[seed]
            train_rows = [row for row in splits["train"] if row.seed == seed]
            validation_rows = [row for row in splits["validation"] if row.seed == seed]
            test_rows = [row for row in splits["test"] if row.seed == seed]
            coverage = _support_coverage(test_rows, learned_support)
            for method_name in method_names:
                try:
                    selected = _select_scales(
                        validation_rows,
                        method_name,
                        learned_support=learned_support,
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
                        "test_support_known_fraction": coverage["known_fraction"],
                        "test_support_missing_mod_count": len(coverage["missing_query_mods"]),
                        **selected,
                    }
                    for split_name, split_rows in (("train", train_rows), ("validation", validation_rows), ("test", test_rows)):
                        metrics = evaluate_seed_local_query_support(
                            split_rows,
                            method_name,
                            learned_support=learned_support,
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
        "schema_version": STAGE59_SCHEMA_VERSION,
        "stage": "stage59_seed_local_query_support_audit",
        "status": "completed",
        "dataset": "synthetic_small_decoder_train_short_test_long_v1",
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "source_stage": "stage58_pooled_train_query_support_audit",
        "method_names": list(method_names),
        "tasks": list(TASK_NAMES),
        "seeds": list(seeds),
        "examples_per_length": examples_per_length,
        "learned_query_support_maps_by_seed": {
            str(seed): {str(key): value for key, value in learned_support.items()}
            for seed, learned_support in learned_support_by_seed.items()
        },
        "phase_cued_support_coverage": phase_cued_coverage,
        "model": {
            "type": "seed_local_query_token_support_lookup_copy_diagnostic",
            "value_output_mode": "deterministic copied prefix-token mass",
            "metadata_excluded": ["row.reference_delta exact value at evaluation", "row.target_pos", "row.target_delta"],
        },
        "claim_boundary": _claim_boundary(),
        "failed_runs": failed_runs,
        "run_table": run_table,
        "aggregate_table": aggregate_table,
        "ranking_table": ranking_table,
        "decision": _decision(aggregate_table, phase_cued_coverage),
    }


def write_stage59_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    return write_stage56_outputs(result, output_dir)


def print_stage59_summary(result: dict[str, Any]) -> None:
    print_stage57_summary(result)
