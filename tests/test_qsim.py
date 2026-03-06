import pytest

from qrope.qibm import derive_ibm_angles
from qrope.qphotonic import derive_photonic_angles
from qrope.qsim import effective_variant_phases, raw_variant_phases, variant_phases


def test_v4_phase_schedule_is_damped_relative_to_v3() -> None:
    v3 = variant_phases("V3", 3)
    v4 = variant_phases("V4", 3)
    assert len(v3) == len(v4) == 3
    assert all(v4_i < v3_i for v4_i, v3_i in zip(v4, v3))
    assert v4 == pytest.approx([0.14, 0.28, 0.42])


def test_v4_backend_angle_translation_is_damped_relative_to_v3() -> None:
    text = "quiet room and fast check in"
    seed = 42

    _, _, rel_v3 = derive_photonic_angles(text=text, variant="V3", seed=seed)
    _, _, rel_v4 = derive_photonic_angles(text=text, variant="V4", seed=seed)
    _, ibm_v3 = derive_ibm_angles(text=text, variant="V3", seed=seed)
    _, ibm_v4 = derive_ibm_angles(text=text, variant="V4", seed=seed)

    assert rel_v4 < rel_v3
    assert ibm_v4 < ibm_v3


def test_v4b_effective_phase_is_clipped_and_feature_capped() -> None:
    features = [0.1, 3.0]
    raw = raw_variant_phases("V4b", 2)
    effective = effective_variant_phases("V4b", features)

    assert raw == pytest.approx([0.18, 0.36])
    assert effective[0] == pytest.approx(0.035)
    assert effective[1] == pytest.approx(0.22)
    assert effective[0] < raw[0]
    assert effective[1] < raw[1]


def test_variant_phases_returns_raw_schedule_for_backward_compatibility() -> None:
    assert variant_phases("V4b", 2) == pytest.approx([0.18, 0.36])
