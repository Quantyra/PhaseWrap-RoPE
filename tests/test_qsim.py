import pytest

from qrope.qibm import derive_ibm_angles
from qrope.qphotonic import derive_photonic_angles
from qrope.qsim import (
    PAIRSTATE_CONTROL_MODES,
    SUPPORTED_MIXING_PRESETS,
    build_quantum_state,
    build_branch_state,
    effective_variant_phases,
    explicit_interference_score,
    feature_angles,
    hadamard,
    offset_sector,
    ordered_pair_content_value,
    pairstate_signed_contrast,
    pairstate_quantum_result,
    parity_readout,
    parse_synthetic_pair_text,
    pairwise_quantum_score,
    position_phase_angle,
    prob_qubit_one,
    raw_variant_phases,
    rx,
    simple_quantum_score,
    stable_token_hash,
    state_overlap_score,
    state_readout_score,
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


def test_q2_readout_uses_last_qubit_probability() -> None:
    import numpy as np

    state = np.zeros(8, dtype=np.complex128)
    state[4] = 1.0 + 0.0j
    assert state_readout_score(state, n_qubits=3, readout="q2") == pytest.approx(prob_qubit_one(state, qubit=2, n_qubits=3))


def test_parity_readout_stays_in_unit_interval() -> None:
    import numpy as np

    state = np.zeros(4, dtype=np.complex128)
    state[0] = 1.0 + 0.0j
    assert parity_readout(state, n_qubits=2) == pytest.approx(1.0)


def test_simple_quantum_score_supports_alternative_readouts() -> None:
    weighted = simple_quantum_score("good food and quick service", variant="V3", seed=42, readout="weighted")
    q2 = simple_quantum_score("good food and quick service", variant="V3", seed=42, readout="q2")
    parity = simple_quantum_score("good food and quick service", variant="V3", seed=42, readout="parity")
    assert 0.0 <= weighted <= 1.0
    assert 0.0 <= q2 <= 1.0
    assert 0.0 <= parity <= 1.0


def test_supported_mixing_presets_are_available() -> None:
    assert SUPPORTED_MIXING_PRESETS == {"mix_it1", "mix_v0", "mix_v1", "mix_v2"}


def test_simple_quantum_score_supports_mixing_presets() -> None:
    scores = {
        preset: simple_quantum_score(
            "good food and quick service",
            variant="V3",
            seed=42,
            readout="parity",
            mixing_preset=preset,
        )
        for preset in sorted(SUPPORTED_MIXING_PRESETS)
    }
    assert all(0.0 <= score <= 1.0 for score in scores.values())
    assert len(set(round(score, 12) for score in scores.values())) >= 2


def test_interference_tail_differs_from_baseline_tail() -> None:
    baseline = simple_quantum_score(
        "good food and quick service",
        variant="V3",
        seed=42,
        readout="parity",
        mixing_preset="mix_v0",
    )
    candidate = simple_quantum_score(
        "good food and quick service",
        variant="V3",
        seed=42,
        readout="parity",
        mixing_preset="mix_it1",
    )
    assert baseline != pytest.approx(candidate)


def test_rx_gate_is_unitary() -> None:
    import numpy as np

    gate = rx(0.3)
    ident = gate.conjugate().T @ gate
    assert np.allclose(ident, np.eye(2))


def test_hadamard_gate_is_unitary() -> None:
    import numpy as np

    gate = hadamard()
    ident = gate.conjugate().T @ gate
    assert np.allclose(ident, np.eye(2))


def test_build_quantum_state_is_normalized() -> None:
    import numpy as np

    state = build_quantum_state("good food and quick service", variant="V3", seed=42)
    assert np.allclose(float(np.vdot(state, state).real), 1.0)


def test_state_overlap_score_identity_is_one() -> None:
    state = build_quantum_state("good food and quick service", variant="V3", seed=42)
    assert state_overlap_score(state, state) == pytest.approx(1.0)


def test_pairwise_quantum_score_is_deterministic_and_bounded() -> None:
    score_a = pairwise_quantum_score("good food and quick service", "bad slow dirty product", variant="V3", seed=42)
    score_b = pairwise_quantum_score("good food and quick service", "bad slow dirty product", variant="V3", seed=42)
    assert score_a == pytest.approx(score_b)
    assert 0.0 <= score_a <= 1.0


def test_pairwise_quantum_score_prefers_identical_input() -> None:
    identical = pairwise_quantum_score("good food and quick service", "good food and quick service", variant="V3", seed=42)
    different = pairwise_quantum_score("good food and quick service", "bad slow dirty product", variant="V3", seed=42)
    assert identical >= different


def test_parse_synthetic_pair_text_extracts_fields() -> None:
    parsed = parse_synthetic_pair_text("lt:A rt:C lp:2 rp:5 off:+3")
    assert parsed == {
        "left_token": "A",
        "right_token": "C",
        "left_pos": 2,
        "right_pos": 5,
        "offset": 3,
    }


def test_position_phase_angle_scales_with_position() -> None:
    assert position_phase_angle(position=0, qubit_index=1) == pytest.approx(0.0)
    assert position_phase_angle(position=2, qubit_index=1) > position_phase_angle(position=1, qubit_index=1)


def test_build_branch_state_is_normalized() -> None:
    import numpy as np

    state = build_branch_state(token="A", position=3, seed=42)
    assert np.allclose(float(np.vdot(state, state).real), 1.0)


def test_explicit_interference_score_is_deterministic_and_bounded() -> None:
    text = "lt:A rt:C lp:2 rp:5 off:+3"
    score_a = explicit_interference_score(text=text, seed=42)
    score_b = explicit_interference_score(text=text, seed=42)
    assert score_a == pytest.approx(score_b)
    assert 0.0 <= score_a <= 1.0


def test_ordered_pair_content_value_distinguishes_order() -> None:
    ab = ordered_pair_content_value("A", "B", seed=42)
    ba = ordered_pair_content_value("B", "A", seed=42)
    assert ab != pytest.approx(ba)


def test_offset_sector_maps_sign_and_magnitude() -> None:
    assert offset_sector(1) == "P_small"
    assert offset_sector(4) == "P_large"
    assert offset_sector(-2) == "N_small"
    assert offset_sector(-3) == "N_large"


def test_pairstate_quantum_result_exposes_sector_responses_before_aggregation() -> None:
    result = pairstate_quantum_result("lt:A rt:C lp:2 rp:5 off:+3", seed=42)
    assert 0.0 <= float(result["score"]) <= 1.0
    assert result["sector"] == "P_large"
    assert result["sector_resolution_pre_aggregation"] is True
    responses = result["sector_responses"]
    assert set(responses.keys()) == {"P_small", "P_large", "N_small", "N_large"}
    assert result["control_mode"] in PAIRSTATE_CONTROL_MODES


def test_pairstate_sector_permuted_changes_signed_contrast() -> None:
    aligned = pairstate_quantum_result("lt:A rt:C lp:2 rp:5 off:+3", seed=42, control_mode="aligned")
    permuted = pairstate_quantum_result("lt:A rt:C lp:2 rp:5 off:+3", seed=42, control_mode="sector_permuted")
    assert aligned["aggregation_buckets"] != permuted["aggregation_buckets"]
    assert float(aligned["signed_contrast"]) != float(permuted["signed_contrast"])


def test_pairstate_signed_contrast_rejects_unknown_mode() -> None:
    with pytest.raises(ValueError, match="Unsupported pairstate control mode"):
        pairstate_signed_contrast(
            {"P_small": 0.5, "P_large": 0.5, "N_small": 0.5, "N_large": 0.5},
            control_mode="bad_mode",
        )


def test_pairstate_sector_parity_uses_crossed_assignment() -> None:
    result = pairstate_quantum_result("lt:A rt:C lp:2 rp:5 off:+3", seed=42, control_mode="sector_parity")
    assert result["aggregation_buckets"] == {
        "positive": ["P_small", "N_large"],
        "negative": ["N_small", "P_large"],
    }
    assert result["sector_resolution_pre_aggregation"] is True
