import pytest

from qrope.qibm import derive_ibm_angles
from qrope.qphotonic import derive_photonic_angles
from qrope.qsim import (
    effective_variant_phases,
    feature_angles,
    raw_variant_phases,
    rx,
    stable_token_hash,
    variant_phases,
    weighted_mean_excitation,
)


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


def test_stable_token_hash_is_deterministic() -> None:
    value = stable_token_hash(tok="service", qubit_index=1, seed=42)
    assert value == stable_token_hash(tok="service", qubit_index=1, seed=42)
    assert value != stable_token_hash(tok="service", qubit_index=2, seed=42)


def test_feature_angles_are_deterministic() -> None:
    angles_a = feature_angles("good food and quick service", n_qubits=3, seed=42)
    angles_b = feature_angles("good food and quick service", n_qubits=3, seed=42)
    assert angles_a == pytest.approx(angles_b)


def test_weighted_mean_excitation_stays_in_unit_interval() -> None:
    import numpy as np

    state = np.zeros(4, dtype=np.complex128)
    state[1] = 1.0 + 0.0j
    assert weighted_mean_excitation(state, n_qubits=2) == pytest.approx(0.5)


def test_rx_gate_is_unitary() -> None:
    import numpy as np

    gate = rx(0.3)
    ident = gate.conjugate().T @ gate
    assert np.allclose(ident, np.eye(2))
