from __future__ import annotations

import pytest

from qrope import phase_margins, phase_residual, phasewrap_features, phasewrap_score
from qrope.stage11_phasewrap_theory import phasewrap_score as stage11_phasewrap_score


def test_public_phasewrap_score_matches_stage11_formula() -> None:
    for reference_delta in (-25, -1, 0, 7, 31):
        for candidate_delta in (-19, 0, 3, 19, 44):
            assert phasewrap_score(reference_delta, candidate_delta) == stage11_phasewrap_score(reference_delta, candidate_delta)


def test_phasewrap_score_translation_invariance() -> None:
    base = phasewrap_score(7, 19)
    assert phasewrap_score(7 + 24, 19 + 24) == base
    assert phasewrap_score(7 + 48, 19) == base
    assert phasewrap_score(7, 19 + 48) == base


def test_phasewrap_score_handles_large_offsets() -> None:
    base = phasewrap_score(7, 19)
    assert phasewrap_score(7 + 24 * 10**9, 19) == pytest.approx(base, abs=1e-6)
    assert phasewrap_score(7, 19 - 24 * 10**9) == pytest.approx(base, abs=1e-6)


def test_phasewrap_features_include_public_fields() -> None:
    features = phasewrap_features(7, 19)
    assert features["reference_delta"] == 7
    assert features["candidate_delta"] == 19
    assert features["period_pair"] == [8, 12]
    assert features["first_period"] == 8
    assert features["second_period"] == 12
    assert features["m8"] == features["first_margin"]
    assert features["m12"] == features["second_margin"]
    assert features["score"] == phasewrap_score(7, 19)


def test_phase_margins_accept_custom_period_pair() -> None:
    default = phase_margins(7, 19)
    custom = phase_margins(7, 19, (8, 24))
    assert default["m8"] == default["first_margin"]
    assert default["m12"] == default["second_margin"]
    assert "m8" not in custom
    assert "m12" not in custom
    assert default["margins_by_period"][8] == custom["margins_by_period"][8]
    assert default["second_margin"] != custom["second_margin"]


def test_invalid_period_inputs_raise() -> None:
    with pytest.raises(ValueError, match="period must be positive"):
        phase_residual(1, 2, 0)
    with pytest.raises(ValueError, match="period_pair"):
        phase_margins(1, 2, (8, 12, 24))  # type: ignore[arg-type]
