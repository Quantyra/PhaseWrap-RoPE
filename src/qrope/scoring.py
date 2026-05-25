from __future__ import annotations

import math
from typing import Any


DEFAULT_PERIOD_PAIR = (8, 12)


def _wrap_to_pi(angle: float) -> float:
    while angle <= -math.pi:
        angle += 2.0 * math.pi
    while angle > math.pi:
        angle -= 2.0 * math.pi
    return angle


def phase_residual(reference_delta: int, candidate_delta: int, period: int) -> float:
    if period <= 0:
        raise ValueError("period must be positive")
    reference_theta = _wrap_to_pi(2.0 * math.pi * float(reference_delta) / float(period))
    candidate_theta = _wrap_to_pi(2.0 * math.pi * float(candidate_delta) / float(period))
    return abs(_wrap_to_pi(reference_theta - candidate_theta))


def phase_margins(
    reference_delta: int,
    candidate_delta: int,
    period_pair: tuple[int, int] = DEFAULT_PERIOD_PAIR,
) -> dict[str, float]:
    if len(period_pair) != 2:
        raise ValueError("period_pair must contain exactly two periods")
    first_period, second_period = period_pair
    first_residual = phase_residual(reference_delta, candidate_delta, first_period)
    second_residual = phase_residual(reference_delta, candidate_delta, second_period)
    first_margin = math.cos(first_residual) - math.cos(2.0 * math.pi / float(first_period))
    second_margin = math.cos(second_residual) - math.cos(2.0 * math.pi / float(second_period))
    return {
        "m8": first_margin,
        "m12": second_margin,
        "first_margin": first_margin,
        "second_margin": second_margin,
        "first_residual": first_residual,
        "second_residual": second_residual,
    }


def phasewrap_score(
    reference_delta: int,
    candidate_delta: int,
    period_pair: tuple[int, int] = DEFAULT_PERIOD_PAIR,
) -> float:
    margins = phase_margins(reference_delta, candidate_delta, period_pair)
    return float(margins["first_margin"] * margins["second_margin"])


def phasewrap_features(
    reference_delta: int,
    candidate_delta: int,
    period_pair: tuple[int, int] = DEFAULT_PERIOD_PAIR,
) -> dict[str, Any]:
    margins = phase_margins(reference_delta, candidate_delta, period_pair)
    return {
        "reference_delta": reference_delta,
        "candidate_delta": candidate_delta,
        "period_pair": list(period_pair),
        "first_period": period_pair[0],
        "second_period": period_pair[1],
        **margins,
        "score": phasewrap_score(reference_delta, candidate_delta, period_pair),
    }
