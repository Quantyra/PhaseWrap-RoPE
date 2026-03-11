# Q-RoPE Symbolic Insufficiency Stronger-Control Implementation Plan v1

Date: 2026-03-10
Stories: S694

## Goal
Define the exact bounded implementation plan for one stronger symbolic control family under the frozen stronger basis.

## Allowed Writable Scope
- `src/qrope/run.py`
- focused tests only
- packet summaries and decision memos only after a future implementation approval

## Fixed Task
- `synthetic_symbolic_insufficiency_transition_response`

## Fixed Baseline Reference
- `V_future_relational_witness_symbolic_insufficiency`

## Future Stronger Control
- one control only: `V_control_symbolic_symbolic_insufficiency_regressor_v2`
- required basis:
  - coarse transition indicators
  - first-order single-channel analog summaries
  - first-order pairwise cross-direction summaries
  - bounded quadratic analog terms
  - bounded cubic analog terms
  - bounded gated coarse-indicator times analog terms

## Forbidden Implementation Moves
- latent path identifiers in features
- explicit microstate keys
- per-latent lookup tables
- arbitrary feature crosses beyond the declared basis
- second stronger control family
- task changes

## Future Packet Shape
- same seeds: `42`, `123`, `777`
- same backend: `sim_quantum_statevector`
- witness baseline vs one stronger symbolic control only

## Approval Dependency
- code stays closed until a separate implementation approval explicitly adopts this plan
