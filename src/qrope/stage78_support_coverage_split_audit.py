from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from .stage10_small_decoder_transformer import DEFAULT_SEEDS, TASK_NAMES, Stage10Example, make_stage10_splits
from .stage45_matched_decoder_only_gate import METHOD_NAMES
from .stage56_standard_input_cue_copy_audit import DEFAULT_EXAMPLES_PER_LENGTH, write_stage56_outputs
from .stage58_pooled_train_query_support_audit import _query_mod


STAGE78_SCHEMA_VERSION = "qrope_stage78_support_coverage_split_audit_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage78_support_coverage_split_audit"
DEFAULT_AUDIT_SEEDS = DEFAULT_SEEDS
SUPPORT_STRATEGIES = ("same_seed_train", "same_seed_train_validation", "cross_seed_train", "pooled_train")


def _claim_boundary() -> dict[str, list[str]]:
    return {
        "supported": [
            "A no-credential split-coverage audit for original Stage10 phase-cued query-support rows.",
            "Evidence about whether the Stage76/77 same-seed support heads have held-out support classes available.",
            "Fair preservation of support-coverage failure modes before further decoder promotion work.",
        ],
        "excluded": [
            "production transformer superiority",
            "full transformer-scale validation",
            "a claim that PhaseWrap-RoPE replaces RoPE",
            "a claim that support coverage alone validates a matched decoder-only transformer",
            "a claim that cross-seed support availability is positional-method promotion evidence",
            "broad quantum advantage",
        ],
    }


def _phase_rows(splits_by_task: dict[str, dict[str, list[Stage10Example]]], split: str, *, seed: int | None = None) -> list[Stage10Example]:
    rows = splits_by_task["phase_cued_retrieval"][split]
    if seed is None:
        return list(rows)
    return [row for row in rows if row.seed == seed]


def _support_map(rows: list[Stage10Example]) -> dict[int, set[int]]:
    mapping: dict[int, set[int]] = {}
    for row in rows:
        mapping.setdefault(_query_mod(row), set()).add(int(row.reference_delta))
    return mapping


def _support_rows_for_strategy(
    splits_by_task: dict[str, dict[str, list[Stage10Example]]],
    *,
    held_out_seed: int,
    strategy: str,
) -> list[Stage10Example]:
    if strategy == "same_seed_train":
        return _phase_rows(splits_by_task, "train", seed=held_out_seed)
    if strategy == "same_seed_train_validation":
        return _phase_rows(splits_by_task, "train", seed=held_out_seed) + _phase_rows(splits_by_task, "validation", seed=held_out_seed)
    if strategy == "cross_seed_train":
        return [row for row in _phase_rows(splits_by_task, "train") if row.seed != held_out_seed]
    if strategy == "pooled_train":
        return _phase_rows(splits_by_task, "train")
    raise ValueError(f"unknown support strategy: {strategy}")


def _coverage_record(
    *,
    seed: int,
    strategy: str,
    support_rows: list[Stage10Example],
    test_rows: list[Stage10Example],
) -> dict[str, Any]:
    mapping = _support_map(support_rows)
    support_classes = sorted({int(row.reference_delta) for row in support_rows})
    test_query_mods = [_query_mod(row) for row in test_rows]
    known_query_mod_hits = [query_mod in mapping for query_mod in test_query_mods]
    class_hits = [int(row.reference_delta) in support_classes for row in test_rows]
    exact_hits = [int(row.reference_delta) in mapping.get(_query_mod(row), set()) for row in test_rows]
    return {
        "task": "phase_cued_retrieval",
        "seed": seed,
        "support_strategy": strategy,
        "support_row_count": len(support_rows),
        "test_row_count": len(test_rows),
        "support_class_count": len(support_classes),
        "support_query_mod_count": len(mapping),
        "known_query_mod_fraction": round(float(np.mean(known_query_mod_hits)), 6) if test_rows else 0.0,
        "support_class_fraction": round(float(np.mean(class_hits)), 6) if test_rows else 0.0,
        "exact_query_support_fraction": round(float(np.mean(exact_hits)), 6) if test_rows else 0.0,
        "support_classes": support_classes,
        "support_query_mods": sorted(mapping),
        "test_classes": sorted({int(row.reference_delta) for row in test_rows}),
        "test_query_mods": sorted(set(test_query_mods)),
        "missing_query_mods": sorted(set(test_query_mods) - set(mapping)),
        "missing_classes": sorted({int(row.reference_delta) for row in test_rows} - set(support_classes)),
        "support_map": {str(query_mod): sorted(values) for query_mod, values in sorted(mapping.items())},
    }


def _aggregate(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for strategy in SUPPORT_STRATEGIES:
        selected = [row for row in records if row["support_strategy"] == strategy]
        rows.append(
            {
                "task": "phase_cued_retrieval",
                "support_strategy": strategy,
                "seed_count": len(selected),
                "support_row_count_mean": round(float(np.mean([row["support_row_count"] for row in selected])), 6),
                "test_row_count_mean": round(float(np.mean([row["test_row_count"] for row in selected])), 6),
                "support_class_count_mean": round(float(np.mean([row["support_class_count"] for row in selected])), 6),
                "support_query_mod_count_mean": round(float(np.mean([row["support_query_mod_count"] for row in selected])), 6),
                "known_query_mod_fraction_mean": round(float(np.mean([row["known_query_mod_fraction"] for row in selected])), 6),
                "support_class_fraction_mean": round(float(np.mean([row["support_class_fraction"] for row in selected])), 6),
                "exact_query_support_fraction_mean": round(float(np.mean([row["exact_query_support_fraction"] for row in selected])), 6),
            }
        )
    return rows


def _decision(aggregate_table: list[dict[str, Any]]) -> dict[str, Any]:
    by_strategy = {row["support_strategy"]: row for row in aggregate_table}
    same_seed_exact = by_strategy["same_seed_train"]["exact_query_support_fraction_mean"]
    cross_seed_exact = by_strategy["cross_seed_train"]["exact_query_support_fraction_mean"]
    pooled_exact = by_strategy["pooled_train"]["exact_query_support_fraction_mean"]
    if same_seed_exact == 0.0 and cross_seed_exact == 1.0 and pooled_exact == 1.0:
        decision = "SAME_SEED_SUPPORT_COVERAGE_SPLIT_EXPLAINS_STAGE77_FAILURE"
        boundary = "Default same-seed train rows provide zero held-out phase-cued query-support coverage, while cross-seed and pooled train rows provide full coverage."
    elif same_seed_exact < cross_seed_exact:
        decision = "SAME_SEED_SUPPORT_COVERAGE_WEAKER_THAN_CROSS_SEED"
        boundary = "Same-seed train support coverage is weaker than cross-seed support coverage."
    else:
        decision = "SUPPORT_COVERAGE_DOES_NOT_EXPLAIN_STAGE77_FAILURE"
        boundary = "The split-coverage audit does not by itself explain the Stage77 support failure."
    return {
        "decision": decision,
        "same_seed_train_exact_query_support_fraction_mean": same_seed_exact,
        "cross_seed_train_exact_query_support_fraction_mean": cross_seed_exact,
        "pooled_train_exact_query_support_fraction_mean": pooled_exact,
        "claim_boundary": boundary,
    }


def run_stage78_audit(
    *,
    seeds: tuple[int, ...] = DEFAULT_AUDIT_SEEDS,
    examples_per_length: int = DEFAULT_EXAMPLES_PER_LENGTH,
) -> dict[str, Any]:
    splits_by_task = make_stage10_splits(seeds=seeds, examples_per_length=examples_per_length)
    run_table: list[dict[str, Any]] = []
    for seed in seeds:
        test_rows = _phase_rows(splits_by_task, "test", seed=seed)
        for strategy in SUPPORT_STRATEGIES:
            support_rows = _support_rows_for_strategy(splits_by_task, held_out_seed=seed, strategy=strategy)
            run_table.append(_coverage_record(seed=seed, strategy=strategy, support_rows=support_rows, test_rows=test_rows))
    aggregate_table = _aggregate(run_table)
    ranking_table = sorted(aggregate_table, key=lambda row: row["exact_query_support_fraction_mean"], reverse=True)
    return {
        "schema_version": STAGE78_SCHEMA_VERSION,
        "stage": "stage78_support_coverage_split_audit",
        "status": "completed",
        "dataset": "synthetic_stage10_original_phase_cued_support_coverage_v1",
        "no_hardware_submission": True,
        "provider_credentials_required": False,
        "source_stage": "stage77_auxiliary_support_copy_head_audit",
        "method_names": list(METHOD_NAMES),
        "tasks": list(TASK_NAMES),
        "seeds": list(seeds),
        "examples_per_length": examples_per_length,
        "support_strategies": list(SUPPORT_STRATEGIES),
        "claim_boundary": _claim_boundary(),
        "failed_runs": [],
        "run_table": run_table,
        "aggregate_table": aggregate_table,
        "ranking_table": ranking_table,
        "decision": _decision(aggregate_table),
    }


def write_stage78_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    return write_stage56_outputs(result, output_dir)


def print_stage78_summary(result: dict[str, Any]) -> None:
    columns = (
        "support_strategy",
        "seed_count",
        "known_query_mod_fraction_mean",
        "support_class_fraction_mean",
        "exact_query_support_fraction_mean",
    )
    print(" | ".join(columns))
    print(" | ".join("---" for _ in columns))
    for row in result["ranking_table"]:
        print(" | ".join(str(row[column]) for column in columns))
    print(f"decision: {result['decision']['decision']}")
    print(f"claim_boundary: {result['decision']['claim_boundary']}")
