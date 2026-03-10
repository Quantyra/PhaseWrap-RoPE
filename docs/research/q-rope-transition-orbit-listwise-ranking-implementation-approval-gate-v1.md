# Q-RoPE Transition Orbit Listwise Ranking Implementation Approval Gate v1

Date: 2026-03-11
Stories: S377-S378

## Decision
Approve one strictly bounded implementation phase for the transition-orbit listwise ranking line.

## Approved Scope
- task: `synthetic_transition_orbit_listwise_ranking`
- candidate: `V_future_relational_witness_transition_orbit_listwise`
- controls:
  - `V_control_symbolic_transition_list_lookup`
  - `V_control_symbolic_transition_list_cross_direction`
  - `V_control_symbolic_transition_list_quadratic`
  - `V_control_symbolic_transition_list_orbit_permuted`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- local-only
- zero-credit

## Required Generator Diagnostics
- `coarse_list_lookup_near_null_pass = true`
- `within_state_list_count_min >= 2`
- `rank_position_balance_pass = true`
- `token_view_balance_pass = true`

## Primary Metrics
- top-1 listwise accuracy
- mean ordinal agreement score

## Secondary Diagnostics
- calibration-style diagnostics only if they are naturally available from the ranking head without inventing a second task

## Explicitly Disallowed
- remote execution
- task expansion
- second witness candidate
- additional symbolic ranking controls beyond the fixed first packet
- fallback reinterpretation of the task as pairwise classification after execution

## Hard Stop Rule
If the generator cannot prove within-state list variation or the coarse list lookup is not near-null, stop before packet interpretation.
