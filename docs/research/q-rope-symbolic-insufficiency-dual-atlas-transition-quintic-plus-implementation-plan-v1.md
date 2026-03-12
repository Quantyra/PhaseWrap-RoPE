# Q-RoPE Symbolic Insufficiency Dual-Atlas Transition-Quintic-Plus Implementation Plan v1

Date: 2026-03-11
Stories: S837

## Objective
Define one bounded implementation cycle for a materially stronger symbolic challenger without relaxing the frozen symbolic-insufficiency fairness contract.

## Challenger
- `V_control_symbolic_symbolic_insufficiency_regressor_dual_atlas_transition_quintic_plus`

## Standing Witness Benchmark
- `V_future_relational_witness_symbolic_insufficiency`

## Frozen Task
- `synthetic_symbolic_insufficiency_transition_response`
- backend: `sim_quantum_statevector`
- seeds:
  - `42`
  - `123`
  - `777`

## Writable Scope
- `src/qrope/run.py`
- `tests/test_run_real_mode.py`

## Frozen Basis Extension
- preserve the full dual-atlas transition-quintic basis
- add exactly these per-cell features only:
  - `cell_ij_kl_source_to_dest_sector_times_orientation_minus_content_times_orientation_plus_content_times_orientation_delta_times_ordered_content_delta`
  - `cell_ij_kl_dest_to_source_sector_times_orientation_minus_content_times_orientation_plus_content_times_orientation_delta_times_ordered_content_delta`
- no other per-cell feature types are allowed

## Fixed Packet Rule
Run exactly one packet:
- witness vs dual-atlas transition-quintic-plus challenger
- seeds `42`, `123`, `777`
- stop the line immediately if the challenger matches or beats the witness on both declared packet metrics

## Declared Packet Metrics
- `mae`
- `rank_correlation`
