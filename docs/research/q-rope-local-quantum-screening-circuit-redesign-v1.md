# Q-RoPE Local Quantum Screening Circuit Redesign v1

## Problem statement
The deterministic local screening backend is now reproducible, but it is not discriminative.

Evidence:
- `V3`, `V4`, and `V4b` produced identical aggregate outcomes across all datasets and seeds in the deterministic packet
- the current gate therefore cannot support variant promotion decisions

Reference:
- [q-rope-v4b-deterministic-local-comparison-packet-v1.md](C:/Users/Dan/Desktop/Projects/QuantyraQRope/docs/research/q-rope-v4b-deterministic-local-comparison-packet-v1.md)

## Current circuit weakness
The current local screening circuit in [qsim.py](C:/Users/Dan/Desktop/Projects/QuantyraQRope/src/qrope/qsim.py):
- loads features with per-qubit `RY`
- injects positional signal with per-qubit `RZ`
- applies a single nearest-neighbor CNOT chain
- reads out only qubit `0`

Why that is weak:
- `RZ` affects phase, not amplitude directly
- with the current shallow structure, that phase information is not being converted into a sufficiently different measurement signal at the single-qubit readout
- one-qubit probability on qubit `0` is too lossy a summary for the positional differences we care about

## Redesign objective
Keep the local screening path zero-credit, but make it sensitive to positional-phase differences.

## Recommended redesign
Use a two-part change:

1. stronger phase-to-amplitude conversion
- after the `RZ` layer, add a second mixing layer before measurement
- preferred first option:
  - `RY(feature)`
  - `RZ(phase)`
  - entangling chain
  - `RX(mix_angle)` or `H`-like mixing on all qubits
  - second entangling chain

2. richer readout
- stop using only `P(qubit_0 = 1)`
- instead compute a small readout vector, then compress to a score
- preferred first option:
  - mean excitation across all qubits
  - plus parity-style signal from measured bitstrings

This is still small enough for local simulation, but it gives the phase perturbation more paths to influence the observable.

## Minimal redesign path
The next implementation should avoid a large simulator rewrite.

Recommended first local-screening design:
- keep `n_qubits = 3`
- keep deterministic feature encoding
- circuit:
  - feature `RY` layer
  - positional `RZ` layer
  - CNOT chain `0->1->2`
  - global `RX(pi/4)` mixing layer
  - reverse CNOT chain `2->1->0`
- readout:
  - use full statevector probabilities
  - score = weighted mean excitation over all qubits

## Why this is the right next step
- it keeps the local backend cheap
- it changes observability rather than changing the variant definitions again
- it directly tests whether the current failure is due to weak phase readout, which is the most plausible explanation from the code path

## What not to do yet
- do not spend remote credits
- do not widen datasets first
- do not redesign `V4b` again before we know whether the local gate can actually see positional differences

## Success condition
The redesign succeeds if the deterministic local packet produces non-identical aggregate results across `V3`, `V4`, and `V4b`, even before claiming that any one variant is best.

## Bottom line
The next blocker is circuit observability.
The local gate needs a stronger phase-sensitive screening circuit before variant comparisons are meaningful.
