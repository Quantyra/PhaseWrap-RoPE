# Q-RoPE Transfer Braid Deeper Pair-Reindex Hardening v1

Date: 2026-03-12
Stories: S953

## Fixed Packet
- task: `synthetic_symbolic_insufficiency_braid_crossing_response`
- perturbation: `pair_reindex = 7`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- retained models:
  - `V_future_relational_witness_symbolic_insufficiency_braid`
  - `V_control_symbolic_symbolic_insufficiency_braid_regressor`

## Mean Results
- witness:
  - `mae = 0.115643`
  - `rank_correlation = 0.078592`
  - `calibration_slope = 0.230457`
- control:
  - `mae = 0.115444`
  - `rank_correlation = 0.123812`
  - `calibration_slope = 0.265804`

## Interpretation
- the deeper perturbation was non-inert
- the bounded symbolic control matched or beat the witness on both declared packet metrics in the mean
- this stops the braid execution branch under the active gate

## Artifact
- `logs/ablation_runs/summary/transfer_braid_pair7_v1.csv`
