from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from typing import Any

import numpy as np

from .stage11_phasewrap_theory import PERIOD_PAIR_GRID, lcm, phasewrap_score
from .stage12_ruler_retrieval import DEFAULT_EXAMPLES_PER_TASK_LENGTH, DEFAULT_SEEDS, TASK_NAMES, Stage12Example, make_stage12_examples
from .stage22_long_context_retrieval import DEFAULT_CONTEXT_LENGTHS as LONG_CONTEXT_LENGTHS


STAGE29_SCHEMA_VERSION = "qrope_stage29_period_pair_task_audit_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage29_period_pair_task_audit"
LOCAL_CONTEXT_LENGTHS = (128, 256, 512, 1024)
ROUND_DIGITS = 12


def _softmax(values: np.ndarray) -> np.ndarray:
    shifted = values - np.max(values)
    exp_values = np.exp(shifted)
    return exp_values / np.sum(exp_values)


def _ranked_indices(scores: np.ndarray) -> list[int]:
    return sorted(range(len(scores)), key=lambda index: (-float(scores[index]), index))


def _target_indices(row: Stage12Example) -> tuple[int, ...]:
    candidate_positions = tuple(row.key_positions)
    return tuple(candidate_positions.index(position) for position in row.target_positions)


def evaluate_period_pair(rows: list[Stage12Example], period_pair: tuple[int, int]) -> dict[str, Any]:
    losses: list[float] = []
    top1_hits: list[float] = []
    reciprocal_ranks: list[float] = []
    target_masses: list[float] = []
    ranks: list[int] = []
    target_score_gaps: list[float] = []
    top_score_tie_counts: list[int] = []
    target_score_tie_counts: list[int] = []
    target_top_tie_hits: list[float] = []
    fundamental_period = lcm(*period_pair)
    for row in rows:
        target_indices = _target_indices(row)
        target_set = set(target_indices)
        candidate_deltas = [row.query_pos - position for position in row.key_positions]
        scores = np.array([phasewrap_score(row.reference_delta, int(delta), period_pair) for delta in candidate_deltas], dtype=float)
        probabilities = _softmax(scores)
        ranked = _ranked_indices(scores)
        rank = min(ranked.index(index) + 1 for index in target_indices)
        top_index = ranked[0]
        top_score = round(float(scores[top_index]), ROUND_DIGITS)
        target_best_score = round(max(float(scores[index]) for index in target_indices), ROUND_DIGITS)
        target_mass = max(float(np.sum(probabilities[list(target_indices)])), 1e-12)
        top_tie_count = sum(1 for value in scores if round(float(value), ROUND_DIGITS) == top_score)
        target_tie_count = sum(1 for value in scores if round(float(value), ROUND_DIGITS) == target_best_score)
        losses.append(-math.log(target_mass))
        top1_hits.append(1.0 if top_index in target_set else 0.0)
        reciprocal_ranks.append(1.0 / float(rank))
        target_masses.append(target_mass)
        ranks.append(rank)
        target_score_gaps.append(round(top_score - target_best_score, ROUND_DIGITS))
        top_score_tie_counts.append(top_tie_count)
        target_score_tie_counts.append(target_tie_count)
        target_top_tie_hits.append(1.0 if target_best_score == top_score else 0.0)
    mean_loss = float(np.mean(losses))
    return {
        "period_pair": f"{period_pair[0]}/{period_pair[1]}",
        "period_a": period_pair[0],
        "period_b": period_pair[1],
        "gcd": math.gcd(*period_pair),
        "fundamental_period": fundamental_period,
        "row_count": len(rows),
        "sequence_length_min": min(row.sequence_length for row in rows),
        "sequence_length_max": max(row.sequence_length for row in rows),
        "loss": round(mean_loss, 6),
        "perplexity": round(float(math.exp(mean_loss)), 6),
        "top1_accuracy": round(float(np.mean(top1_hits)), 6),
        "mrr": round(float(np.mean(reciprocal_ranks)), 6),
        "mean_target_probability": round(float(np.mean(target_masses)), 6),
        "mean_first_relevant_rank": round(float(np.mean(ranks)), 6),
        "target_top_tie_rate": round(float(np.mean(target_top_tie_hits)), 6),
        "mean_target_score_gap": round(float(np.mean(target_score_gaps)), 6),
        "mean_top_score_tie_count": round(float(np.mean(top_score_tie_counts)), 6),
        "mean_target_score_tie_count": round(float(np.mean(target_score_tie_counts)), 6),
    }


def _task_table(rows: list[Stage12Example], period_pairs: tuple[tuple[int, int], ...]) -> list[dict[str, Any]]:
    table: list[dict[str, Any]] = []
    for task_name in TASK_NAMES:
        task_rows = [row for row in rows if row.task == task_name]
        for period_pair in period_pairs:
            row = evaluate_period_pair(task_rows, period_pair)
            row["task"] = task_name
            table.append(row)
    return table


def _length_table(rows: list[Stage12Example], period_pairs: tuple[tuple[int, int], ...]) -> list[dict[str, Any]]:
    table: list[dict[str, Any]] = []
    for sequence_length in sorted({row.sequence_length for row in rows}):
        length_rows = [row for row in rows if row.sequence_length == sequence_length]
        for period_pair in period_pairs:
            row = evaluate_period_pair(length_rows, period_pair)
            row["sequence_length"] = sequence_length
            table.append(row)
    return table


def run_stage29_audit(
    *,
    seeds: tuple[int, ...] = DEFAULT_SEEDS,
    local_context_lengths: tuple[int, ...] = LOCAL_CONTEXT_LENGTHS,
    long_context_lengths: tuple[int, ...] = LONG_CONTEXT_LENGTHS,
    examples_per_task_length: int = DEFAULT_EXAMPLES_PER_TASK_LENGTH,
    period_pairs: tuple[tuple[int, int], ...] = PERIOD_PAIR_GRID,
) -> dict[str, Any]:
    local_rows = make_stage12_examples(seeds=seeds, context_lengths=local_context_lengths, examples_per_task_length=examples_per_task_length)
    long_rows = make_stage12_examples(seeds=seeds, context_lengths=long_context_lengths, examples_per_task_length=examples_per_task_length)
    local_table = [evaluate_period_pair(local_rows, period_pair) for period_pair in period_pairs]
    long_table = [evaluate_period_pair(long_rows, period_pair) for period_pair in period_pairs]
    local_selection = sorted(local_table, key=lambda row: (row["top1_accuracy"], row["mrr"], row["mean_target_probability"], row["period_pair"]), reverse=True)
    long_selection = sorted(long_table, key=lambda row: (row["top1_accuracy"], row["mrr"], row["mean_target_probability"], row["period_pair"]), reverse=True)
    default_pair = "8/12"
    default_local = next(row for row in local_table if row["period_pair"] == default_pair)
    default_long = next(row for row in long_table if row["period_pair"] == default_pair)
    return {
        "schema_version": STAGE29_SCHEMA_VERSION,
        "stage": "stage29_period_pair_task_audit",
        "dataset": "stage12_and_stage22_non_phase_cued_retrieval_rows",
        "no_hardware_submission": True,
        "seeds": list(seeds),
        "local_context_lengths": list(local_context_lengths),
        "long_context_lengths": list(long_context_lengths),
        "examples_per_task_length": examples_per_task_length,
        "period_pairs": [list(pair) for pair in period_pairs],
        "task_names": list(TASK_NAMES),
        "local_row_count": len(local_rows),
        "long_row_count": len(long_rows),
        "claim_boundary": {
            "supported": [
                "A deterministic period-pair audit over non-phase-cued retrieval rows.",
                "Evidence about which tested period pairs reduce alias pressure or improve fixed-score retrieval metrics on these packets.",
                "Task- and length-conditioned diagnostics for target score gaps and tie counts.",
            ],
            "excluded": [
                "a proof that any period pair is globally optimal",
                "production transformer superiority",
                "full transformer-scale validation",
                "broad quantum advantage",
                "a claim that PhaseWrap-RoPE is a validated RoPE replacement",
            ],
        },
        "interpretation": (
            "Stage 29 audits fixed phase-wrap period pairs as classical scoring rules. It does not train a model. "
            "Better period-pair retrieval metrics on these rows would identify candidates for later adapters, not prove replacement."
        ),
        "local_table": local_table,
        "long_table": long_table,
        "local_selection_table": local_selection,
        "long_selection_table": long_selection,
        "task_table": _task_table(local_rows, period_pairs),
        "length_table": _length_table(long_rows, period_pairs),
        "default_pair_summary": {
            "period_pair": default_pair,
            "local_top1_accuracy": default_local["top1_accuracy"],
            "local_mrr": default_local["mrr"],
            "local_target_top_tie_rate": default_local["target_top_tie_rate"],
            "long_top1_accuracy": default_long["top1_accuracy"],
            "long_mrr": default_long["mrr"],
            "long_target_top_tie_rate": default_long["target_top_tie_rate"],
        },
        "best_local_period_pair": local_selection[0]["period_pair"],
        "best_long_period_pair": long_selection[0]["period_pair"],
    }


def write_stage29_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "dataset": result["dataset"],
        "no_hardware_submission": result["no_hardware_submission"],
        "seeds": result["seeds"],
        "local_context_lengths": result["local_context_lengths"],
        "long_context_lengths": result["long_context_lengths"],
        "examples_per_task_length": result["examples_per_task_length"],
        "period_pairs": result["period_pairs"],
        "task_names": result["task_names"],
        "result_path": str((output_dir / "results.json").as_posix()),
        "local_summary_csv_path": str((output_dir / "local_summary.csv").as_posix()),
        "long_summary_csv_path": str((output_dir / "long_summary.csv").as_posix()),
        "task_summary_csv_path": str((output_dir / "task_summary.csv").as_posix()),
        "length_summary_csv_path": str((output_dir / "length_summary.csv").as_posix()),
        "claim_boundary": result["claim_boundary"],
    }
    paths = {
        "manifest": str(output_dir / "manifest.json"),
        "results": str(output_dir / "results.json"),
        "local_summary_csv": str(output_dir / "local_summary.csv"),
        "long_summary_csv": str(output_dir / "long_summary.csv"),
        "task_summary_csv": str(output_dir / "task_summary.csv"),
        "length_summary_csv": str(output_dir / "length_summary.csv"),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    for key, rows in (
        ("local_summary_csv", result["local_table"]),
        ("long_summary_csv", result["long_table"]),
        ("task_summary_csv", result["task_table"]),
        ("length_summary_csv", result["length_table"]),
    ):
        with Path(paths[key]).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
    return paths


def print_stage29_table(result: dict[str, Any]) -> None:
    columns = ("period_pair", "top1_accuracy", "mrr", "mean_target_probability", "target_top_tie_rate", "mean_target_score_gap")
    print("local")
    print(" | ".join(columns))
    print(" | ".join("---" for _ in columns))
    for row in result["local_selection_table"][:5]:
        print(" | ".join(str(row[column]) for column in columns))
    print("long")
    print(" | ".join(columns))
    print(" | ".join("---" for _ in columns))
    for row in result["long_selection_table"][:5]:
        print(" | ".join(str(row[column]) for column in columns))
