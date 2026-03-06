# Q-RoPE Local Screening Circuit Implementation Plan v1

## Goal
Implement the redesigned local quantum screening circuit with the smallest possible write set, keeping the work zero-credit and focused on discriminability.

## Minimal write set
1. [qsim.py](C:/Users/Dan/Desktop/Projects/QuantyraQRope/src/qrope/qsim.py)
- extend the local simulation path to support a stronger screening circuit
- keep deterministic feature encoding and existing variant definitions
- add:
  - post-phase mixing layer
  - reverse entangling layer
  - richer score readout from full-state probabilities

2. [run.py](C:/Users/Dan/Desktop/Projects/QuantyraQRope/src/qrope/run.py)
- no redesign required if `simple_quantum_score(...)` remains the entry point
- local comparison packet can reuse the current runner path

3. `tests/`
- add focused tests for:
  - richer readout stays in `[0,1]`
  - the redesigned screening circuit remains deterministic
  - variant-sensitive path no longer collapses trivially in simple sanity checks

## Recommended circuit change
Current:
- `RY(feature)`
- `RZ(phase)`
- CNOT chain
- read `P(qubit_0 = 1)`

Target first implementation:
- `RY(feature)`
- `RZ(phase)`
- forward CNOT chain
- global `RX(pi/4)` mixing layer
- reverse CNOT chain
- score from all-qubit state probabilities

## Recommended score function
Use a weighted mean-excitation score from the final statevector:

1. compute probability of each computational basis state
2. compute excitation fraction for each basis state:
- `excitation = (# of 1 bits) / n_qubits`
3. return probability-weighted mean excitation

Why this score:
- still bounded in `[0,1]`
- more sensitive than single-qubit readout
- no need for a large simulator abstraction change

## Deterministic validation packet
Backend:
- `sim_quantum_statevector`

Variants:
- `V3`
- `V4`
- `V4b`

Datasets:
- `yelp`
- `imdb`
- `amazon`

Seeds:
- `42`
- `123`
- `777`

## Promotion criterion
The redesign is successful if the deterministic local packet produces at least one non-trivial separation among `V3`, `V4`, and `V4b` on at least two datasets.

This does not require `V4b` to win yet.
It requires the local gate to become informative.

## Non-goals
- no paid remote runs
- no remote backend changes
- no wider dataset expansion
- no new variant redesign before this circuit is tested

## Bottom line
The next engineering step is a small `qsim.py`-centered circuit/readout upgrade.
If that still fails to separate variants, the local gate may need replacement rather than further tuning.
