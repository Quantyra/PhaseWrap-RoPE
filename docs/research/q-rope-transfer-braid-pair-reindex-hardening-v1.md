# Q-RoPE Transfer Braid Pair-Reindex Hardening v1

Date: 2026-03-12
Stories: S947

## Fixed Packet
- task: `synthetic_symbolic_insufficiency_braid_crossing_response`
- perturbation: `pair_reindex = 1`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- retained models:
  - `V_future_relational_witness_symbolic_insufficiency_braid`
  - `V_control_symbolic_symbolic_insufficiency_braid_regressor`

## Mean Results
- witness:
  - `mae = 0.061082`
  - `rank_correlation = 0.429130`
  - `calibration_slope = 0.698050`
- control:
  - `mae = 0.074224`
  - `rank_correlation = -0.004399`
  - `calibration_slope = -0.031154`

## Interpretation
- the perturbation was non-inert
- the witness still beat the bounded symbolic control on both declared packet metrics in the mean
- this justifies keeping the branch active and moving to the next structural hardening step

## Artifact
- `logs/ablation_runs/summary/transfer_braid_pair1_v1.csv`
