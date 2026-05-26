from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Any

from .scoring import DEFAULT_PERIOD_PAIR, phase_residual, phasewrap_score


STAGE11_SCHEMA_VERSION = "qrope_stage11_phasewrap_theory_v1"
DEFAULT_OUTPUT_DIR = Path("logs") / "automated_stage_gates" / "stage11_phasewrap_theory"
PERIOD_PAIR_GRID = (
    (4, 8),
    (5, 10),
    (6, 12),
    (7, 11),
    (8, 12),
    (8, 16),
    (8, 24),
    (9, 15),
    (10, 16),
    (12, 24),
    (16, 32),
)
DEFAULT_CONTEXT_LENGTHS = (24, 48, 96, 192, 384, 768, 1024)
ROUND_DIGITS = 12


def lcm(a: int, b: int) -> int:
    if a <= 0 or b <= 0:
        raise ValueError("periods must be positive")
    return abs(a * b) // math.gcd(a, b)


def score_from_difference(difference: int, period_pair: tuple[int, int] = DEFAULT_PERIOD_PAIR) -> float:
    return phasewrap_score(difference, 0, period_pair)


def _score_key(value: float) -> str:
    return f"{value:.{ROUND_DIGITS}f}"


def residue_score_table(period_pair: tuple[int, int] = DEFAULT_PERIOD_PAIR) -> list[dict[str, Any]]:
    period = lcm(*period_pair)
    return [
        {
            "difference_mod_lcm": difference,
            "score": round(score_from_difference(difference, period_pair), ROUND_DIGITS),
        }
        for difference in range(period)
    ]


def alias_classes_for_context(
    context_length: int,
    *,
    reference_delta: int = 0,
    period_pair: tuple[int, int] = DEFAULT_PERIOD_PAIR,
) -> list[dict[str, Any]]:
    if context_length <= 0:
        raise ValueError("context_length must be positive")
    groups: dict[str, list[int]] = defaultdict(list)
    fundamental_period = lcm(*period_pair)
    for candidate_delta in range(1, context_length + 1):
        difference_mod_lcm = (reference_delta - candidate_delta) % fundamental_period
        score = score_from_difference(difference_mod_lcm, period_pair)
        groups[_score_key(score)].append(candidate_delta)

    rows = [
        {
            "score": float(score),
            "alias_count": len(candidate_deltas),
            "candidate_delta_min": min(candidate_deltas),
            "candidate_delta_max": max(candidate_deltas),
            "candidate_delta_examples": candidate_deltas[:8],
        }
        for score, candidate_deltas in groups.items()
    ]
    return sorted(rows, key=lambda row: (-row["alias_count"], row["score"]))


def context_alias_summary(
    context_lengths: tuple[int, ...] = DEFAULT_CONTEXT_LENGTHS,
    *,
    period_pair: tuple[int, int] = DEFAULT_PERIOD_PAIR,
) -> list[dict[str, Any]]:
    rows = []
    fundamental_period = lcm(*period_pair)
    for context_length in context_lengths:
        classes = alias_classes_for_context(context_length, period_pair=period_pair)
        unique_scores = len(classes)
        max_alias = max(row["alias_count"] for row in classes)
        mean_alias = float(context_length / unique_scores)
        rows.append(
            {
                "period_pair": list(period_pair),
                "fundamental_period": fundamental_period,
                "context_length": context_length,
                "unique_score_count": unique_scores,
                "mean_alias_class_size": round(mean_alias, 6),
                "max_alias_class_size": max_alias,
                "top_alias_score": classes[0]["score"],
                "top_alias_examples": classes[0]["candidate_delta_examples"],
            }
        )
    return rows


def period_pair_summary(
    period_pairs: tuple[tuple[int, int], ...] = PERIOD_PAIR_GRID,
    *,
    context_length: int = 1024,
) -> list[dict[str, Any]]:
    rows = []
    for period_pair in period_pairs:
        fundamental_period = lcm(*period_pair)
        classes = alias_classes_for_context(context_length, period_pair=period_pair)
        unique_scores = len(classes)
        residue_scores = residue_score_table(period_pair)
        positive_scores = [row["score"] for row in residue_scores if row["score"] > 0.0]
        rows.append(
            {
                "period_pair": list(period_pair),
                "gcd": math.gcd(*period_pair),
                "fundamental_period": fundamental_period,
                "context_length": context_length,
                "unique_score_count": unique_scores,
                "mean_alias_class_size": round(float(context_length / unique_scores), 6),
                "max_alias_class_size": max(row["alias_count"] for row in classes),
                "positive_residue_count": len(positive_scores),
                "score_range": round(max(row["score"] for row in residue_scores) - min(row["score"] for row in residue_scores), 12),
                "one_step_thresholds": [
                    round(2.0 * math.pi / float(period_pair[0]), 12),
                    round(2.0 * math.pi / float(period_pair[1]), 12),
                ],
            }
        )
    return sorted(rows, key=lambda row: (row["fundamental_period"], row["unique_score_count"], row["period_pair"]))


def fourier_support(period_pair: tuple[int, int] = DEFAULT_PERIOD_PAIR, *, tolerance: float = 1e-9) -> dict[str, Any]:
    period = lcm(*period_pair)
    values = [score_from_difference(difference, period_pair) for difference in range(period)]
    coefficients = []
    positive_frequency_support = []
    for frequency in range(period):
        real = 0.0
        imag = 0.0
        for index, value in enumerate(values):
            angle = -2.0 * math.pi * frequency * index / float(period)
            real += value * math.cos(angle)
            imag += value * math.sin(angle)
        real /= float(period)
        imag /= float(period)
        magnitude = math.hypot(real, imag)
        if magnitude > tolerance:
            coefficients.append(
                {
                    "frequency": frequency,
                    "real": round(real, 12),
                    "imag": round(imag, 12),
                    "magnitude": round(magnitude, 12),
                }
            )
            if 0 < frequency <= period // 2:
                positive_frequency_support.append(frequency)
    return {
        "period_pair": list(period_pair),
        "fundamental_period": period,
        "positive_frequency_support": positive_frequency_support,
        "nonzero_coefficient_count": len(coefficients),
        "coefficients": coefficients,
        "interpretation": (
            "The score is exactly representable as a small periodic feature map over the least common period. "
            "For 8/12 this is a classical mod-24 feature map, not quantum-specific evidence."
        ),
    }


def invariance_checks(period_pair: tuple[int, int] = DEFAULT_PERIOD_PAIR) -> dict[str, Any]:
    period = lcm(*period_pair)
    examples = [(3, 14), (7, 31), (19, 5), (44, 89)]
    translation_holds = all(
        abs(phasewrap_score(a, b, period_pair) - phasewrap_score(a + 17, b + 17, period_pair)) <= 1e-12
        for a, b in examples
    )
    lcm_shift_holds = all(
        abs(phasewrap_score(a, b, period_pair) - phasewrap_score(a + period, b, period_pair)) <= 1e-12
        for a, b in examples
    )
    mirror_holds = all(
        abs(score_from_difference(difference, period_pair) - score_from_difference(-difference, period_pair)) <= 1e-12
        for difference in range(-period, period + 1)
    )
    return {
        "period_pair": list(period_pair),
        "fundamental_period": period,
        "translation_invariance_holds": translation_holds,
        "lcm_shift_invariance_holds": lcm_shift_holds,
        "mirror_symmetry_holds": mirror_holds,
        "alias_driver": (
            "Scores depend only on the offset difference modulo the least common period and are symmetric under sign reversal. "
            "Longer contexts therefore contain repeated and mirrored score aliases."
        ),
    }


def run_phasewrap_theory_analysis(
    *,
    period_pair: tuple[int, int] = DEFAULT_PERIOD_PAIR,
    context_lengths: tuple[int, ...] = DEFAULT_CONTEXT_LENGTHS,
) -> dict[str, Any]:
    alias_summary = context_alias_summary(context_lengths, period_pair=period_pair)
    pair_summary = period_pair_summary(context_length=max(context_lengths))
    support = fourier_support(period_pair)
    invariances = invariance_checks(period_pair)
    return {
        "schema_version": STAGE11_SCHEMA_VERSION,
        "stage": "stage11_phasewrap_theory",
        "no_hardware_submission": True,
        "default_period_pair": list(period_pair),
        "fundamental_period": lcm(*period_pair),
        "context_lengths": list(context_lengths),
        "invariance_checks": invariances,
        "residue_score_table": residue_score_table(period_pair),
        "alias_summary": alias_summary,
        "period_pair_summary": pair_summary,
        "fourier_support": support,
        "claim_boundary": {
            "supported": [
                "The 8/12 score is translation invariant in joint offset shifts.",
                "The 8/12 score depends on offset difference modulo 24 and has mirrored aliases.",
                "The score is exactly representable as a small classical periodic feature map over mod 24.",
                "Alias classes grow as context length exceeds the fundamental period.",
            ],
            "excluded": [
                "a proof that 8/12 is globally optimal",
                "evidence that PhaseWrap replaces RoPE in production transformers",
                "quantum advantage",
                "general cross-backend robustness",
            ],
        },
        "interpretation": (
            "Stage 11 strengthens the mathematical audit trail for the fixed score. It also narrows the claim: "
            "PhaseWrap is a compact periodic positional scoring rule whose aliases and classical feature equivalent "
            "must be considered before making transformer-replacement claims."
        ),
    }


def write_stage11_outputs(result: dict[str, Any], output_dir: Path = DEFAULT_OUTPUT_DIR) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "schema_version": result["schema_version"],
        "stage": result["stage"],
        "no_hardware_submission": result["no_hardware_submission"],
        "default_period_pair": result["default_period_pair"],
        "fundamental_period": result["fundamental_period"],
        "context_lengths": result["context_lengths"],
        "result_path": str((output_dir / "results.json").as_posix()),
        "alias_summary_csv_path": str((output_dir / "alias_summary.csv").as_posix()),
        "period_pair_summary_csv_path": str((output_dir / "period_pair_summary.csv").as_posix()),
        "residue_score_table_csv_path": str((output_dir / "residue_score_table.csv").as_posix()),
        "claim_boundary": result["claim_boundary"],
    }
    paths = {
        "manifest": str(output_dir / "manifest.json"),
        "results": str(output_dir / "results.json"),
        "alias_summary_csv": str(output_dir / "alias_summary.csv"),
        "period_pair_summary_csv": str(output_dir / "period_pair_summary.csv"),
        "residue_score_table_csv": str(output_dir / "residue_score_table.csv"),
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "results.json").write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    _write_csv(output_dir / "alias_summary.csv", result["alias_summary"])
    _write_csv(output_dir / "period_pair_summary.csv", result["period_pair_summary"])
    _write_csv(output_dir / "residue_score_table.csv", result["residue_score_table"])
    return paths


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"cannot write empty CSV: {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def print_stage11_summary(result: dict[str, Any]) -> None:
    print("context_length | unique_score_count | mean_alias_class_size | max_alias_class_size")
    print("--- | --- | --- | ---")
    for row in result["alias_summary"]:
        print(
            " | ".join(
                str(row[column])
                for column in (
                    "context_length",
                    "unique_score_count",
                    "mean_alias_class_size",
                    "max_alias_class_size",
                )
            )
        )
    print(f"fundamental_period: {result['fundamental_period']}")
    print(f"positive_frequency_support: {result['fourier_support']['positive_frequency_support']}")
