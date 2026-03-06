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
}

V4B_PHASE_CLIP = 0.22
V4B_RATIO_FACTOR = 0.35
FEATURE_FLOOR = 0.05
SCREENING_MIX_ANGLE = math.pi / 4.0
SUPPORTED_READOUTS = {"weighted", "q2", "parity"}


def simple_quantum_score(
    text: str,
    variant: str,
    seed: int,
    n_qubits: int = 3,
    readout: str = "weighted",
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
    n = max(2, min(n_qubits, 6))
    dim = 1 << n
    state = np.zeros(dim, dtype=np.complex128)
    state[0] = 1.0 + 0.0j

    features = feature_angles(text=text, n_qubits=n, seed=seed)
    phases = effective_variant_phases(variant, features)

    for q in range(n):
        state = apply_single_qubit_gate(state, ry(features[q]), q, n)
        state = apply_single_qubit_gate(state, rz(phases[q]), q, n)

    for q in range(n - 1):
        state = apply_cnot(state, control=q, target=q + 1, n_qubits=n)

    for q in range(n):
        state = apply_single_qubit_gate(state, rx(SCREENING_MIX_ANGLE), q, n)

    for q in range(n - 1, 0, -1):
        state = apply_cnot(state, control=q, target=q - 1, n_qubits=n)

    return state_readout_score(state=state, n_qubits=n, readout=readout)


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
