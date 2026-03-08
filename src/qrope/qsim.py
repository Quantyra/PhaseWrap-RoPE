from __future__ import annotations

import hashlib
import math
from typing import Iterable

import numpy as np

VARIANT_PHASE_BASES = {
    "V0": 0.00,
    "V1": 0.08,
    "V2": 0.16,
    "V3": 0.24,
    "V4": 0.14,
    "V4b": 0.18,
    "V_new_explicit_interference": 0.24,
    "V_pairstate_relational": 0.20,
    "V_future_sector_contrast_pairstate": 0.20,
}

V4B_PHASE_CLIP = 0.22
V4B_RATIO_FACTOR = 0.35
FEATURE_FLOOR = 0.05
SCREENING_MIX_ANGLE = math.pi / 4.0
SUPPORTED_READOUTS = {"weighted", "q2", "parity"}
SUPPORTED_MIXING_PRESETS = {"mix_it1", "mix_v0", "mix_v1", "mix_v2"}
PAIRSTATE_CONTROL_MODES = {"aligned", "sector_permuted", "sector_parity"}


def simple_quantum_score(
    text: str,
    variant: str,
    seed: int,
    n_qubits: int = 3,
    readout: str = "weighted",
    mixing_preset: str = "mix_v0",
) -> float:
    """Return a probability score from a small statevector circuit.

    This is an actual quantum simulation (statevector evolution) with:
    - per-qubit RY feature loading
    - positional-like RZ phase gates by variant
    - forward nearest-neighbor CNOT entangling layer
    - global RX mixing layer to convert phase differences into readout differences
    - reverse CNOT chain
    - all-qubit weighted excitation readout
    """
    if variant == "V_new_explicit_interference":
        return explicit_interference_score(text=text, seed=seed, n_qubits=n_qubits)
    if variant in {"V_pairstate_relational", "V_future_sector_contrast_pairstate"}:
        return pairstate_quantum_result(text=text, seed=seed, n_qubits=n_qubits)["score"]
    state = build_quantum_state(
        text=text,
        variant=variant,
        seed=seed,
        n_qubits=n_qubits,
        mixing_preset=mixing_preset,
    )
    n = int(round(math.log2(len(state))))
    return state_readout_score(state=state, n_qubits=n, readout=readout)


def build_quantum_state(
    text: str,
    variant: str,
    seed: int,
    n_qubits: int = 3,
    mixing_preset: str = "mix_v0",
) -> np.ndarray:
    n = max(2, min(n_qubits, 6))
    dim = 1 << n
    state = np.zeros(dim, dtype=np.complex128)
    state[0] = 1.0 + 0.0j

    features = feature_angles(text=text, n_qubits=n, seed=seed)
    phases = effective_variant_phases(variant, features)

    for q in range(n):
        state = apply_single_qubit_gate(state, ry(features[q]), q, n)
        state = apply_single_qubit_gate(state, rz(phases[q]), q, n)

    state = apply_forward_cnot_chain(state, n_qubits=n)
    state = apply_mixing_preset(state=state, n_qubits=n, mixing_preset=mixing_preset)
    return state


def pairwise_quantum_score(
    text_a: str,
    text_b: str,
    variant: str,
    seed: int,
    n_qubits: int = 3,
    mixing_preset: str = "mix_v0",
) -> float:
    state_a = build_quantum_state(
        text=text_a,
        variant=variant,
        seed=seed,
        n_qubits=n_qubits,
        mixing_preset=mixing_preset,
    )
    state_b = build_quantum_state(
        text=text_b,
        variant=variant,
        seed=seed,
        n_qubits=n_qubits,
        mixing_preset=mixing_preset,
    )
    return state_overlap_score(state_a, state_b)


def explicit_interference_score(text: str, seed: int, n_qubits: int = 3) -> float:
    sample = parse_synthetic_pair_text(text)
    state_a = build_branch_state(
        token=sample["left_token"],
        position=sample["left_pos"],
        seed=seed,
        n_qubits=n_qubits,
    )
    state_b = build_branch_state(
        token=sample["right_token"],
        position=sample["right_pos"],
        seed=seed,
        n_qubits=n_qubits,
    )
    constructive = normalize_state(state_a + state_b)
    destructive = normalize_state(state_a - state_b)
    parity_plus = parity_readout(constructive, n_qubits=n_qubits)
    parity_minus = parity_readout(destructive, n_qubits=n_qubits)
    contrast = parity_plus - parity_minus
    return max(0.0, min(1.0, 0.5 + contrast / 2.0))


def pairstate_signed_contrast(
    sector_responses: dict[str, float],
    control_mode: str = "aligned",
) -> tuple[float, dict[str, list[str]]]:
    if control_mode == "aligned":
        positive_keys = ["P_small", "P_large"]
        negative_keys = ["N_small", "N_large"]
    elif control_mode == "sector_permuted":
        positive_keys = ["P_small", "N_large"]
        negative_keys = ["N_small", "P_large"]
    elif control_mode == "sector_parity":
        positive_keys = ["P_small", "N_large"]
        negative_keys = ["N_small", "P_large"]
    else:
        raise ValueError(f"Unsupported pairstate control mode: {control_mode}")
    positive_mean = sum(float(sector_responses[key]) for key in positive_keys) / len(positive_keys)
    negative_mean = sum(float(sector_responses[key]) for key in negative_keys) / len(negative_keys)
    return positive_mean - negative_mean, {"positive": positive_keys, "negative": negative_keys}


def pairstate_magnitude_balance(sector_responses: dict[str, float]) -> float:
    return abs(sector_responses["P_small"] - sector_responses["P_large"]) + abs(
        sector_responses["N_small"] - sector_responses["N_large"]
    )


def pairstate_quantum_result(
    text: str,
    seed: int,
    n_qubits: int = 3,
    control_mode: str = "aligned",
) -> dict[str, object]:
    sample = parse_synthetic_pair_text(text)
    sector = offset_sector(int(sample["offset"]))
    if control_mode == "aligned" and sector[0] != ("P" if int(sample["offset"]) > 0 else "N"):
        raise ValueError("Aligned pairstate control mode requires sign-aligned sector mapping")
    sector_responses = sector_response_map(sample=sample, seed=seed, n_qubits=n_qubits)
    signed_contrast, aggregation_buckets = pairstate_signed_contrast(
        sector_responses=sector_responses,
        control_mode=control_mode,
    )
    magnitude_balance = pairstate_magnitude_balance(sector_responses)
    score = max(0.0, min(1.0, 0.5 + signed_contrast / 2.0))
    return {
        "score": score,
        "sector": sector,
        "control_mode": control_mode,
        "sector_responses": {k: round(v, 6) for k, v in sector_responses.items()},
        "aggregation_buckets": aggregation_buckets,
        "signed_contrast": round(signed_contrast, 6),
        "magnitude_balance": round(magnitude_balance, 6),
        "sector_resolution_pre_aggregation": True,
    }


def build_branch_state(token: str, position: int, seed: int, n_qubits: int = 3) -> np.ndarray:
    n = max(2, min(n_qubits, 6))
    dim = 1 << n
    state = np.zeros(dim, dtype=np.complex128)
    state[0] = 1.0 + 0.0j

    features = feature_angles(text=token, n_qubits=n, seed=seed)
    for q in range(n):
        state = apply_single_qubit_gate(state, ry(features[q]), q, n)
        state = apply_single_qubit_gate(state, rz(position_phase_angle(position=position, qubit_index=q)), q, n)

    state = apply_forward_cnot_chain(state, n_qubits=n)
    state = apply_global_rx_layer(state, n_qubits=n, angle=SCREENING_MIX_ANGLE)
    state = apply_reverse_cnot_chain(state, n_qubits=n)
    return state


def token_code(token: str, side: str, seed: int) -> float:
    raw = stable_token_hash(tok=f"{side}:{token}", qubit_index=0, seed=seed)
    return (raw % 10000) / 10000.0


def ordered_pair_content_value(left_token: str, right_token: str, seed: int) -> float:
    left = token_code(left_token, side="L", seed=seed)
    right = token_code(right_token, side="R", seed=seed)
    same_pair_bonus = 0.08 if left_token == right_token else -0.02
    raw = 0.55 * left + 0.45 * right + same_pair_bonus
    return max(0.0, min(1.0, raw))


def offset_sector(offset: int) -> str:
    magnitude = abs(offset)
    band = "small" if magnitude in {1, 2} else "large"
    sign = "P" if offset > 0 else "N"
    return f"{sign}_{band}"


def sector_response_map(sample: dict[str, int | str], seed: int, n_qubits: int = 3) -> dict[str, float]:
    left_token = str(sample["left_token"])
    right_token = str(sample["right_token"])
    sector = offset_sector(int(sample["offset"]))
    content = ordered_pair_content_value(left_token=left_token, right_token=right_token, seed=seed)
    base_phase = VARIANT_PHASE_BASES["V_pairstate_relational"]

    responses: dict[str, float] = {}
    for idx, key in enumerate(("P_small", "P_large", "N_small", "N_large")):
        sign_match = 1.0 if key[0] == sector[0] else -1.0
        mag_match = 1.0 if key.split("_", 1)[1] == sector.split("_", 1)[1] else -1.0
        theta = base_phase * (idx + 1) + content * math.pi * 0.75 + sign_match * 0.35 + mag_match * 0.18
        response = 0.5 + 0.18 * math.sin(theta) + 0.12 * sign_match + 0.05 * mag_match
        responses[key] = max(0.0, min(1.0, response))
    return responses


def position_phase_angle(position: int, qubit_index: int) -> float:
    base = VARIANT_PHASE_BASES["V_new_explicit_interference"]
    return base * (qubit_index + 1) * position


def parse_synthetic_pair_text(text: str) -> dict[str, int | str]:
    fields: dict[str, str] = {}
    for part in text.split():
        if ":" not in part:
            continue
        key, value = part.split(":", 1)
        fields[key] = value
    required = {"lt", "rt", "lp", "rp", "off"}
    missing = required.difference(fields)
    if missing:
        raise ValueError(f"Missing synthetic pair fields: {sorted(missing)}")
    return {
        "left_token": fields["lt"],
        "right_token": fields["rt"],
        "left_pos": int(fields["lp"]),
        "right_pos": int(fields["rp"]),
        "offset": int(fields["off"]),
    }


def normalize_state(state: np.ndarray) -> np.ndarray:
    norm = float(np.linalg.norm(state))
    if norm == 0.0:
        raise ValueError("Cannot normalize zero state")
    return state / norm


def feature_angles(text: str, n_qubits: int, seed: int) -> list[float]:
    tokens = [t for t in text.lower().split() if t]
    if not tokens:
        return [0.0] * n_qubits
    vals: list[float] = []
    for i in range(n_qubits):
        total = 0
        for tok in tokens:
            total += stable_token_hash(tok=tok, qubit_index=i, seed=seed)
        norm = (total % 10000) / 10000.0
        vals.append(norm * math.pi)
    return vals


def stable_token_hash(tok: str, qubit_index: int, seed: int) -> int:
    payload = f"{tok}|{qubit_index}|{seed}".encode("utf-8")
    digest = hashlib.sha256(payload).digest()
    return int.from_bytes(digest[:2], byteorder="big", signed=False)


def raw_variant_phases(variant: str, n_qubits: int) -> list[float]:
    base = VARIANT_PHASE_BASES.get(variant, 0.04)
    return [base * (i + 1) for i in range(n_qubits)]


def effective_variant_phases(variant: str, features: list[float]) -> list[float]:
    raw_phases = raw_variant_phases(variant, len(features))
    if variant != "V4b":
        return raw_phases

    effective: list[float] = []
    for raw_phase, feature in zip(raw_phases, features):
        clipped = max(-V4B_PHASE_CLIP, min(V4B_PHASE_CLIP, raw_phase))
        cap = V4B_RATIO_FACTOR * max(abs(feature), FEATURE_FLOOR)
        if clipped == 0.0:
            effective.append(0.0)
            continue
        effective.append(math.copysign(min(abs(clipped), cap), clipped))
    return effective


def variant_phases(variant: str, n_qubits: int) -> list[float]:
    return raw_variant_phases(variant, n_qubits)


def apply_mixing_preset(state: np.ndarray, n_qubits: int, mixing_preset: str) -> np.ndarray:
    if mixing_preset not in SUPPORTED_MIXING_PRESETS:
        raise ValueError(f"Unsupported mixing preset: {mixing_preset}")

    mixed = state
    if mixing_preset == "mix_it1":
        mixed = apply_global_rx_layer(mixed, n_qubits=n_qubits, angle=SCREENING_MIX_ANGLE)
        mixed = apply_global_hadamard_layer(mixed, n_qubits=n_qubits)
        return apply_reverse_cnot_chain(mixed, n_qubits=n_qubits)
    if mixing_preset == "mix_v0":
        mixed = apply_global_rx_layer(mixed, n_qubits=n_qubits, angle=SCREENING_MIX_ANGLE)
        return apply_reverse_cnot_chain(mixed, n_qubits=n_qubits)
    if mixing_preset == "mix_v1":
        mixed = apply_global_rx_layer(mixed, n_qubits=n_qubits, angle=SCREENING_MIX_ANGLE * 1.5)
        return apply_reverse_cnot_chain(mixed, n_qubits=n_qubits)

    mixed = apply_global_rx_layer(mixed, n_qubits=n_qubits, angle=SCREENING_MIX_ANGLE)
    mixed = apply_reverse_cnot_chain(mixed, n_qubits=n_qubits)
    mixed = apply_forward_cnot_chain(mixed, n_qubits=n_qubits)
    mixed = apply_global_rx_layer(mixed, n_qubits=n_qubits, angle=SCREENING_MIX_ANGLE / 2.0)
    return apply_reverse_cnot_chain(mixed, n_qubits=n_qubits)


def apply_global_rx_layer(state: np.ndarray, n_qubits: int, angle: float) -> np.ndarray:
    out = state
    for q in range(n_qubits):
        out = apply_single_qubit_gate(out, rx(angle), q, n_qubits)
    return out


def apply_global_hadamard_layer(state: np.ndarray, n_qubits: int) -> np.ndarray:
    out = state
    gate = hadamard()
    for q in range(n_qubits):
        out = apply_single_qubit_gate(out, gate, q, n_qubits)
    return out


def apply_forward_cnot_chain(state: np.ndarray, n_qubits: int) -> np.ndarray:
    out = state
    for q in range(n_qubits - 1):
        out = apply_cnot(out, control=q, target=q + 1, n_qubits=n_qubits)
    return out


def apply_reverse_cnot_chain(state: np.ndarray, n_qubits: int) -> np.ndarray:
    out = state
    for q in range(n_qubits - 1, 0, -1):
        out = apply_cnot(out, control=q, target=q - 1, n_qubits=n_qubits)
    return out


def ry(theta: float) -> np.ndarray:
    c = math.cos(theta / 2.0)
    s = math.sin(theta / 2.0)
    return np.array([[c, -s], [s, c]], dtype=np.complex128)


def rz(theta: float) -> np.ndarray:
    return np.array(
        [
            [np.exp(-1j * theta / 2.0), 0.0j],
            [0.0j, np.exp(1j * theta / 2.0)],
        ],
        dtype=np.complex128,
    )


def rx(theta: float) -> np.ndarray:
    c = math.cos(theta / 2.0)
    s = math.sin(theta / 2.0)
    return np.array([[c, -1j * s], [-1j * s, c]], dtype=np.complex128)


def hadamard() -> np.ndarray:
    scale = 1.0 / math.sqrt(2.0)
    return np.array([[scale, scale], [scale, -scale]], dtype=np.complex128)


def apply_single_qubit_gate(state: np.ndarray, gate: np.ndarray, qubit: int, n_qubits: int) -> np.ndarray:
    out = state.copy()
    step = 1 << qubit
    size = 1 << n_qubits
    span = step << 1
    for base in range(0, size, span):
        for i in range(step):
            i0 = base + i
            i1 = i0 + step
            a0 = state[i0]
            a1 = state[i1]
            out[i0] = gate[0, 0] * a0 + gate[0, 1] * a1
            out[i1] = gate[1, 0] * a0 + gate[1, 1] * a1
    return out


def apply_cnot(state: np.ndarray, control: int, target: int, n_qubits: int) -> np.ndarray:
    out = state.copy()
    size = 1 << n_qubits
    c_mask = 1 << control
    t_mask = 1 << target
    for idx in range(size):
        if idx & c_mask:
            flipped = idx ^ t_mask
            if idx < flipped:
                out[idx], out[flipped] = out[flipped], out[idx]
    return out


def prob_qubit_one(state: np.ndarray, qubit: int, n_qubits: int) -> float:
    mask = 1 << qubit
    prob = 0.0
    for idx, amp in enumerate(state):
        if idx & mask:
            prob += float((amp.conjugate() * amp).real)
    return max(0.0, min(1.0, prob))


def parity_readout(state: np.ndarray, n_qubits: int) -> float:
    total = 0.0
    for idx, amp in enumerate(state):
        prob = float((amp.conjugate() * amp).real)
        parity = -1.0 if (idx.bit_count() % 2) else 1.0
        total += parity * prob
    return max(0.0, min(1.0, (total + 1.0) / 2.0))


def weighted_mean_excitation(state: np.ndarray, n_qubits: int) -> float:
    if n_qubits <= 0:
        return 0.0
    total = 0.0
    for idx, amp in enumerate(state):
        prob = float((amp.conjugate() * amp).real)
        excitation_fraction = idx.bit_count() / n_qubits
        total += prob * excitation_fraction
    return max(0.0, min(1.0, total))


def state_readout_score(state: np.ndarray, n_qubits: int, readout: str) -> float:
    if readout == "weighted":
        return weighted_mean_excitation(state, n_qubits=n_qubits)
    if readout == "q2":
        qubit = min(2, max(0, n_qubits - 1))
        return prob_qubit_one(state, qubit=qubit, n_qubits=n_qubits)
    if readout == "parity":
        return parity_readout(state, n_qubits=n_qubits)
    raise ValueError(f"Unsupported local readout: {readout}")


def state_overlap_score(state_a: np.ndarray, state_b: np.ndarray) -> float:
    overlap = np.vdot(state_a, state_b)
    value = float(abs(overlap) ** 2)
    return max(0.0, min(1.0, value))
