from qrope.qibm import derive_ibm_angles


def test_ibm_angles_are_deterministic_and_positive() -> None:
    feature_angle, phase_angle = derive_ibm_angles("good food and quick service", variant="V3", seed=42)
    assert 0.0 <= feature_angle <= 3.141592653589793
    assert phase_angle > 0.0

    feature_angle_2, phase_angle_2 = derive_ibm_angles("good food and quick service", variant="V3", seed=42)
    assert (feature_angle, phase_angle) == (feature_angle_2, phase_angle_2)


def test_v4b_ibm_phase_angle_is_ratio_controlled() -> None:
    _, phase_angle_v3 = derive_ibm_angles("good food and quick service", variant="V3", seed=42)
    _, phase_angle_v4b = derive_ibm_angles("good food and quick service", variant="V4b", seed=42)
    assert phase_angle_v4b < phase_angle_v3
