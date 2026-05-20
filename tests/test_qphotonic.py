from qrope.qphotonic import compute_effective_theta, derive_photonic_angles, photonic_distribution_to_score


def test_photonic_angles_are_deterministic_and_bounded() -> None:
    theta_left, theta_right, relative_phase = derive_photonic_angles("great service and clean room", variant="V3", seed=42)
    assert 0.2 <= theta_left <= 1.4
    assert 0.2 <= theta_right <= 1.4
    assert relative_phase > 0.0

    theta_left_2, theta_right_2, relative_phase_2 = derive_photonic_angles(
        "great service and clean room",
        variant="V3",
        seed=42,
    )
    assert (theta_left, theta_right, relative_phase) == (theta_left_2, theta_right_2, relative_phase_2)


def test_photonic_distribution_score_stays_in_unit_interval() -> None:
    import pytest

    pytest.importorskip("perceval")
    from perceval import BasicState

    distribution = {
        BasicState("|2,0>"): 0.4,
        BasicState("|1,1>"): 0.2,
        BasicState("|0,2>"): 0.4,
    }
    score = photonic_distribution_to_score(distribution)
    assert 0.0 <= score <= 1.0


def test_effective_theta_is_bounded() -> None:
    assert compute_effective_theta(0.1, 0.1, 0.0) == 0.2
    assert compute_effective_theta(2.0, 2.0, 0.0) == 1.4
    mid = compute_effective_theta(0.8, 0.6, 0.2)
    assert 0.2 <= mid <= 1.4


def test_v4b_photonic_relative_phase_is_lower_than_raw_v3() -> None:
    _, _, rel_v3 = derive_photonic_angles("great service and clean room", variant="V3", seed=42)
    _, _, rel_v4b = derive_photonic_angles("great service and clean room", variant="V4b", seed=42)
    assert rel_v4b < rel_v3
