from __future__ import annotations

import csv
import hashlib
import json
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from .automated_stage_gates import phase_residual


STAGE12_SCHEMA_VERSION = "qrope_stage12_ruler_retrieval_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage12_ruler_retrieval"
DEFAULT_SEEDS = (401, 409, 419, 421, 431)
DEFAULT_CONTEXT_LENGTHS = (128, 256, 512, 1024)
DEFAULT_EXAMPLES_PER_TASK_LENGTH = 4
VOCAB_SIZE = 48
DEFAULT_PERIOD_PAIR = (8, 12)
TASK_NAMES = ("passkey_exact", "multi_needle", "aggregation")
METHOD_NAMES = (
    "phasewrap_rope_8_12",
    "rope_relative",
    "alibi",
    "sinusoidal",
    "no_position",
)


@dataclass(frozen=True)
class Stage12Example:
    example_id: str
    seed: int
    task: str
    sequence_length: int
    query_pos: int
    query_token: int
    reference_delta: int
    target_positions: tuple[int, ...]
    target_deltas: tuple[int, ...]
    tokens: tuple[int, ...]
    key_positions: tuple[int, ...]
    target_rule: str


def phasewrap_period_score(reference_delta: int, candidate_delta: int, period_pair: tuple[int, int] = DEFAULT_PERIOD_PAIR) -> float:
    margins = []
    for period in period_pair:
        residual = phase_residual(reference_delta, candidate_delta, period)
        margins.append(math.cos(residual) - math.cos(2.0 * math.pi / float(period)))
    return float(margins[0] * margins[1])


def _rope_inverse_frequencies(dim: int = 32, base: float = 10000.0) -> np.ndarray:
    return np.array([base ** (-2.0 * index / dim) for index in range(dim // 2)], dtype=float)


def _rope_relative_similarity(diff: np.ndarray) -> np.ndarray:
    inv_freq = _rope_inverse_frequencies()
    return np.mean(np.cos(diff[:, None] * inv_freq[None, :]), axis=1)


def _sinusoidal_similarity(diff: np.ndarray) -> np.ndarray:
    inv_freq = _rope_inverse_frequencies(dim=16, base=1000.0)
    return np.mean(np.cos(diff[:, None] * inv_freq[None, :]), axis=1)


def _candidate_delta_pool(query_pos: int) -> list[int]:
    return list(range(3, query_pos - 1))


def _non_query_tokens(query_token: int) -> list[int]:
    return [token for token in range(VOCAB_SIZE) if token != query_token]


def _select_unique_values(rng: np.random.Generator, pool: list[int], count: int) -> list[int]:
    return sorted(int(value) for value in rng.choice(pool, size=count, replace=False).tolist())


def _phasewrap_best_delta(reference_delta: int, candidate_deltas: tuple[int, ...]) -> int:
    scored = [
        (phasewrap_period_score(reference_delta, candidate_delta), -candidate_delta, candidate_delta)
        for candidate_delta in candidate_deltas
    ]
    scored.sort(reverse=True)
    return int(scored[0][2])


def _build_tokens(
    *,
    rng: np.random.Generator,
    sequence_length: int,
    query_pos: int,
    query_token: int,
    key_positions: tuple[int, ...],
) -> tuple[int, ...]:
    non_query = _non_query_tokens(query_token)
    tokens = [int(non_query[int(rng.integers(0, len(non_query)))]) for _ in range(sequence_length)]
    for position in key_positions:
        tokens[position] = query_token
    tokens[query_pos] = query_token
    return tuple(tokens)


def _make_passkey_example(
    *,
    rng: np.random.Generator,
    seed: int,
    sequence_length: int,
    item_index: int,
) -> Stage12Example:
    query_pos = sequence_length - 1
    pool = _candidate_delta_pool(query_pos)
    target_delta = int(rng.integers(max(6, query_pos // 6), max(7, query_pos - 3)))
    distractor_count = min(32, max(10, sequence_length // 32))
    distractors = [delta for delta in _select_unique_values(rng, [value for value in pool if value != target_delta], distractor_count)]
    key_deltas = tuple(sorted(set(distractors + [target_delta])))
    query_token = int(rng.integers(0, VOCAB_SIZE))
    key_positions = tuple(sorted(query_pos - delta for delta in key_deltas))
    target_positions = (query_pos - target_delta,)
    return Stage12Example(
        example_id=f"passkey_exact_seed{seed}_L{sequence_length}_{item_index:03d}",
        seed=seed,
        task="passkey_exact",
        sequence_length=sequence_length,
        query_pos=query_pos,
        query_token=query_token,
        reference_delta=target_delta,
        target_positions=target_positions,
        target_deltas=(target_delta,),
        tokens=_build_tokens(
            rng=rng,
            sequence_length=sequence_length,
            query_pos=query_pos,
            query_token=query_token,
            key_positions=key_positions,
        ),
        key_positions=key_positions,
        target_rule="exact passkey offset chosen by RNG and exposed as the query offset",
    )


def _make_multi_needle_example(
    *,
    rng: np.random.Generator,
    seed: int,
    sequence_length: int,
    item_index: int,
) -> Stage12Example:
    query_pos = sequence_length - 1
    pool = _candidate_delta_pool(query_pos)
    candidate_count = min(36, max(12, sequence_length // 28))
    key_deltas = tuple(_select_unique_values(rng, pool, candidate_count))
    occurrence_index = min(2, len(key_deltas) - 1)
    target_delta = key_deltas[occurrence_index]
    query_token = int(rng.integers(0, VOCAB_SIZE))
    key_positions = tuple(sorted(query_pos - delta for delta in key_deltas))
    target_positions = (query_pos - target_delta,)
    return Stage12Example(
        example_id=f"multi_needle_seed{seed}_L{sequence_length}_{item_index:03d}",
        seed=seed,
        task="multi_needle",
        sequence_length=sequence_length,
        query_pos=query_pos,
        query_token=query_token,
        reference_delta=target_delta,
        target_positions=target_positions,
        target_deltas=(target_delta,),
        tokens=_build_tokens(
            rng=rng,
            sequence_length=sequence_length,
            query_pos=query_pos,
            query_token=query_token,
            key_positions=key_positions,
        ),
        key_positions=key_positions,
        target_rule="third same-token occurrence in increasing delta order",
    )


def _make_aggregation_example(
    *,
    rng: np.random.Generator,
    seed: int,
    sequence_length: int,
    item_index: int,
) -> Stage12Example:
    query_pos = sequence_length - 1
    pool = _candidate_delta_pool(query_pos)
    anchor_delta = int(rng.integers(max(8, query_pos // 5), max(9, query_pos - 12)))
    partner_delta = min(query_pos - 3, anchor_delta + int(rng.integers(5, max(6, query_pos // 8))))
    if partner_delta == anchor_delta:
        partner_delta = min(query_pos - 3, anchor_delta + 1)
    target_deltas = tuple(sorted((anchor_delta, partner_delta)))
    distractor_pool = [value for value in pool if value not in target_deltas]
    distractor_count = min(34, max(12, sequence_length // 30))
    key_deltas = tuple(sorted(set(_select_unique_values(rng, distractor_pool, distractor_count) + list(target_deltas))))
    query_token = int(rng.integers(0, VOCAB_SIZE))
    key_positions = tuple(sorted(query_pos - delta for delta in key_deltas))
    target_positions = tuple(sorted(query_pos - delta for delta in target_deltas))
    return Stage12Example(
        example_id=f"aggregation_seed{seed}_L{sequence_length}_{item_index:03d}",
        seed=seed,
        task="aggregation",
        sequence_length=sequence_length,
        query_pos=query_pos,
        query_token=query_token,
        reference_delta=anchor_delta,
        target_positions=target_positions,
        target_deltas=target_deltas,
        tokens=_build_tokens(
            rng=rng,
            sequence_length=sequence_length,
            query_pos=query_pos,
            query_token=query_token,
            key_positions=key_positions,
        ),
        key_positions=key_positions,
        target_rule="two explicit offsets selected by the aggregation packet generator",
    )


def make_stage12_examples(
    *,
    seeds: tuple[int, ...] = DEFAULT_SEEDS,
    context_lengths: tuple[int, ...] = DEFAULT_CONTEXT_LENGTHS,
    examples_per_task_length: int = DEFAULT_EXAMPLES_PER_TASK_LENGTH,
) -> list[Stage12Example]:
    examples: list[Stage12Example] = []
    builders = (_make_passkey_example, _make_multi_needle_example, _make_aggregation_example)
    for seed in seeds:
        rng = np.random.default_rng(seed)
        for sequence_length in context_lengths:
            for item_index in range(examples_per_task_length):
                for builder in builders:
                    examples.append(builder(rng=rng, seed=seed, sequence_length=sequence_length, item_index=item_index))
    return examples


def attention_distribution(
    example: Stage12Example,
    method_name: str,
    *,
    period_pair: tuple[int, int] = DEFAULT_PERIOD_PAIR,
    position_scale: float = 1.0,
) -> np.ndarray:
    candidate_positions = np.arange(example.query_pos, dtype=int)
    candidate_deltas = example.query_pos - candidate_positions
    tokens = np.array(example.tokens[: example.query_pos], dtype=int)
    content_logits = np.where(tokens == example.query_token, 2.0, -4.0).astype(float)
    diff = float(example.reference_delta) - candidate_deltas.astype(float)

    if method_name.startswith("phasewrap_rope"):
        position_bias = np.array(
            [phasewrap_period_score(example.reference_delta, int(delta), period_pair) for delta in candidate_deltas],
            dtype=float,
        )
    elif method_name == "rope_relative":
        position_bias = _rope_relative_similarity(diff)
    elif method_name == "sinusoidal":
        position_bias = _sinusoidal_similarity(diff)
    elif method_name == "alibi":
        position_bias = -candidate_deltas.astype(float) / float(example.query_pos)
    elif method_name == "no_position":
        position_bias = np.zeros_like(candidate_deltas, dtype=float)
    else:
        raise ValueError(f"unknown method_name: {method_name}")

    logits = content_logits + position_scale * position_bias
    shifted = logits - np.max(logits)
    exp_values = np.exp(shifted)
    return exp_values / np.sum(exp_values)


def _ranked_indices(distribution: np.ndarray) -> list[int]:
    return sorted(range(len(distribution)), key=lambda index: (-float(distribution[index]), index))


def _first_relevant_rank(distribution: np.ndarray, target_positions: tuple[int, ...]) -> int:
    targets = set(target_positions)
    for rank, index in enumerate(_ranked_indices(distribution), start=1):
        if index in targets:
            return rank
    raise RuntimeError("target position absent from distribution")


def _bootstrap_ci(values: list[float], *, seed_text: str, iterations: int = 1000) -> dict[str, float]:
    if not values:
        raise ValueError("cannot bootstrap an empty metric list")
    rng = random.Random(int(hashlib.sha256(seed_text.encode("utf-8")).hexdigest()[:16], 16))
    means: list[float] = []
    for _ in range(iterations):
        sample = [values[rng.randrange(len(values))] for _ in range(len(values))]
        means.append(float(sum(sample) / len(sample)))
    means.sort()
    low_index = int(0.025 * (iterations - 1))
    high_index = int(0.975 * (iterations - 1))
    return {
        "low": round(means[low_index], 6),
        "high": round(means[high_index], 6),
        "iterations": iterations,
        "confidence_level": 0.95,
    }


def evaluate_method(examples: list[Stage12Example], method_name: str) -> dict[str, Any]:
    if not examples:
        raise ValueError("examples must be non-empty")
    target_probability_mass: list[float] = []
    reciprocal_ranks: list[float] = []
    top1_hits: list[float] = []
    ranks: list[int] = []
    for example in examples:
        distribution = attention_distribution(example, method_name)
        rank = _first_relevant_rank(distribution, example.target_positions)
        top_index = _ranked_indices(distribution)[0]
        ranks.append(rank)
        target_probability_mass.append(float(sum(distribution[position] for position in example.target_positions)))
        reciprocal_ranks.append(1.0 / rank)
        top1_hits.append(1.0 if top_index in set(example.target_positions) else 0.0)

    top1 = float(np.mean(top1_hits))
    mrr = float(np.mean(reciprocal_ranks))
    probability_mass = float(np.mean(target_probability_mass))
    return {
        "method": method_name,
        "row_count": len(examples),
        "seed_count": len({example.seed for example in examples}),
        "task_count": len({example.task for example in examples}),
        "sequence_length_min": min(example.sequence_length for example in examples),
        "sequence_length_max": max(example.sequence_length for example in examples),
        "top1_accuracy": round(top1, 6),
        "top1_ci_low": _bootstrap_ci(top1_hits, seed_text=f"{method_name}:top1")["low"],
        "top1_ci_high": _bootstrap_ci(top1_hits, seed_text=f"{method_name}:top1")["high"],
        "mrr": round(mrr, 6),
        "mrr_ci_low": _bootstrap_ci(reciprocal_ranks, seed_text=f"{method_name}:mrr")["low"],
        "mrr_ci_high": _bootstrap_ci(reciprocal_ranks, seed_text=f"{method_name}:mrr")["high"],
        "mean_target_probability_mass": round(probability_mass, 6),
        "target_probability_mass_ci_low": _bootstrap_ci(target_probability_mass, seed_text=f"{method_name}:prob")["low"],
        "target_probability_mass_ci_high": _bootstrap_ci(target_probability_mass, seed_text=f"{method_name}:prob")["high"],
        "mean_first_relevant_rank": round(float(np.mean(ranks)), 6),
    }


def _task_table(examples: list[Stage12Example]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for task_name in TASK_NAMES:
        task_examples = [example for example in examples if example.task == task_name]
        for method_name in METHOD_NAMES:
            row = evaluate_method(task_examples, method_name)
            row["task"] = task_name
            rows.append(row)
    return rows


def _phasewrap_target_diagnostic(examples: list[Stage12Example]) -> dict[str, Any]:
    exact_hits = 0
    per_task: list[dict[str, Any]] = []
    for task_name in TASK_NAMES:
        task_examples = [example for example in examples if example.task == task_name]
        task_hits = 0
        for example in task_examples:
            candidate_deltas = tuple(example.query_pos - position for position in example.key_positions)
            best_delta = _phasewrap_best_delta(example.reference_delta, candidate_deltas)
            hit = best_delta in set(example.target_deltas)
            exact_hits += int(hit)
            task_hits += int(hit)
        per_task.append(
            {
                "task": task_name,
                "row_count": len(task_examples),
                "phasewrap_oracle_target_overlap": round(float(task_hits / len(task_examples)), 6),
            }
        )
    return {
        "row_count": len(examples),
        "phasewrap_oracle_target_overlap": round(float(exact_hits / len(examples)), 6),
        "per_task": per_task,
        "interpretation": "Fraction of examples where the explicit task target is also the best PhaseWrap-scored same-token candidate.",
    }


def _example_result_rows(examples: list[Stage12Example]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for example in examples:
        row: dict[str, Any] = {
            "example_id": example.example_id,
            "seed": example.seed,
            "task": example.task,
            "sequence_length": example.sequence_length,
            "reference_delta": example.reference_delta,
            "target_deltas": ";".join(str(delta) for delta in example.target_deltas),
            "target_rule": example.target_rule,
        }
        for method_name in METHOD_NAMES:
            distribution = attention_distribution(example, method_name)
            row[f"{method_name}_first_relevant_rank"] = _first_relevant_rank(distribution, example.target_positions)
            row[f"{method_name}_target_probability_mass"] = round(
                float(sum(distribution[position] for position in example.target_positions)),
                8,
            )
        rows.append(row)
    return rows


def run_stage12_benchmark(
    *,
    seeds: tuple[int, ...] = DEFAULT_SEEDS,
    context_lengths: tuple[int, ...] = DEFAULT_CONTEXT_LENGTHS,
    examples_per_task_length: int = DEFAULT_EXAMPLES_PER_TASK_LENGTH,
) -> dict[str, Any]:
    examples = make_stage12_examples(
        seeds=seeds,
        context_lengths=context_lengths,
        examples_per_task_length=examples_per_task_length,
    )
    table = [evaluate_method(examples, method_name) for method_name in METHOD_NAMES]
    selection_table = sorted(
        table,
        key=lambda row: (row["top1_accuracy"], row["mrr"], row["mean_target_probability_mass"], row["method"]),
        reverse=True,
    )
    return {
        "schema_version": STAGE12_SCHEMA_VERSION,
        "stage": "stage12_ruler_retrieval",
        "dataset": "deterministic_ruler_style_non_phase_cued_retrieval_v1",
        "no_hardware_submission": True,
        "seeds": list(seeds),
        "context_lengths": list(context_lengths),
        "examples_per_task_length": examples_per_task_length,
        "row_count": len(examples),
        "method_names": list(METHOD_NAMES),
        "task_names": list(TASK_NAMES),
        "task": {
            "description": "Local RULER-style retrieval packet with passkey, multi-needle, and aggregation rows.",
            "target_construction": "Targets are selected by explicit retrieval rules and RNG offsets, not by maximizing the PhaseWrap score.",
            "note": "This is a deterministic no-credential positional-attention benchmark, not a trained production language model or proof that PhaseWrap-RoPE replaces RoPE.",
        },
        "claim_boundary": {
            "supported": [
                "A stricter local retrieval comparison where targets are not defined by the PhaseWrap score.",
                "Matched deterministic scoring rules across PhaseWrap-RoPE, RoPE-like, ALiBI-like, sinusoidal, and no-position baselines.",
                "Bootstrap intervals over benchmark rows for top-1, MRR, and target probability mass.",
            ],
            "excluded": [
                "production transformer superiority",
                "full transformer-scale validation",
                "broad quantum advantage",
                "general cross-backend robustness",
                "a claim that PhaseWrap-RoPE is a validated RoPE replacement",
            ],
        },
        "phasewrap_target_diagnostic": _phasewrap_target_diagnostic(examples),
        "table": table,
        "selection_table": selection_table,
        "task_table": _task_table(examples),
        "per_example_rows": _example_result_rows(examples),
        "best_method_by_top1_mrr": selection_table[0]["method"],
    }


def write_stage12_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "dataset": result["dataset"],
        "no_hardware_submission": result["no_hardware_submission"],
        "seeds": result["seeds"],
        "context_lengths": result["context_lengths"],
        "examples_per_task_length": result["examples_per_task_length"],
        "row_count": result["row_count"],
        "method_names": result["method_names"],
        "task_names": result["task_names"],
        "result_path": str((output_dir / "results.json").as_posix()),
        "summary_csv_path": str((output_dir / "summary.csv").as_posix()),
        "task_summary_csv_path": str((output_dir / "task_summary.csv").as_posix()),
        "per_example_csv_path": str((output_dir / "per_example_results.csv").as_posix()),
        "claim_boundary": result["claim_boundary"],
    }
    paths = {
        "manifest": str(output_dir / "manifest.json"),
        "results": str(output_dir / "results.json"),
        "summary_csv": str(output_dir / "summary.csv"),
        "task_summary_csv": str(output_dir / "task_summary.csv"),
        "per_example_csv": str(output_dir / "per_example_results.csv"),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    public_result = {key: value for key, value in result.items() if key != "per_example_rows"}
    (output_dir / "results.json").write_text(json.dumps(public_result, indent=2, sort_keys=True), encoding="utf-8")
    with (output_dir / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(result["table"][0].keys()))
        writer.writeheader()
        writer.writerows(result["table"])
    with (output_dir / "task_summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(result["task_table"][0].keys()))
        writer.writeheader()
        writer.writerows(result["task_table"])
    with (output_dir / "per_example_results.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(result["per_example_rows"][0].keys()))
        writer.writeheader()
        writer.writerows(result["per_example_rows"])
    return paths


def print_stage12_table(result: dict[str, Any]) -> None:
    columns = (
        "method",
        "row_count",
        "sequence_length_min",
        "sequence_length_max",
        "top1_accuracy",
        "top1_ci_low",
        "top1_ci_high",
        "mrr",
        "mrr_ci_low",
        "mrr_ci_high",
        "mean_target_probability_mass",
        "mean_first_relevant_rank",
    )
    print(" | ".join(columns))
    print(" | ".join("---" for _ in columns))
    for row in result["selection_table"]:
        print(" | ".join(str(row[column]) for column in columns))
