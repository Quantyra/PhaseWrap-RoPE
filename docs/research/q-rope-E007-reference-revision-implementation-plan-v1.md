# Q-RoPE E007 Reference Revision Implementation Plan v1

Date: 2026-03-16

## BLUF
- `synthetic_positional_reference_revision_selection_response` passes only to one bounded local implementation cycle.
- The stale/current validity contract stays frozen under one symbolic family.
- Stop immediately if implementation requires explicit revision lookup or count-specific symbolic families.

## Frozen Task
- `synthetic_positional_reference_revision_selection_response`

## Frozen Witness
- `V_future_relational_witness_positional_reference_revision_selection`

## Frozen Bounded Symbolic Control
- `V_control_symbolic_positional_reference_revision_selection_regressor`
- additive and bounded-quadratic regressor over declared query summaries, per-candidate content summaries, per-candidate positional summaries, and bounded aggregate stale/current ambiguity summaries only

## Frozen Bounds
- candidate counts:
  - `4`, `5`
- content-class bound:
  - `3`
- stale/current requirement:
  - at least one stale candidate and one revised candidate in every active set
- validity rule:
  - exactly one current-valid candidate in every accepted example

## Writable Scope
- `src/qrope/synthetic.py`
- `src/qrope/run.py`
- `tests/test_synthetic.py`
- `tests/test_run_real_mode.py`

## Fixed Packet
- backend:
  - `sim_quantum_statevector`
- seeds:
  - `42`, `123`, `777`

## Hard-Stop Conditions
Stop `E007` immediately if implementation requires:
- explicit stale/current lookup tables
- symbolic-family branching by candidate count or revision pattern
- token-id shortcuts
- slot-id shortcuts
- candidate-count cap above `5`
- content-class cap above `3`
- examples without active stale/current competition
- content-only solvability by construction
- position-only solvability by construction
