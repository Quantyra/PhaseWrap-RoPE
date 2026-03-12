# Q-RoPE Transfer Braid Token-Renaming Hardening v1

Date: 2026-03-12
Stories: S944

## Fixed Packet
- task: `synthetic_symbolic_insufficiency_braid_crossing_response`
- perturbation: `token_permutation = cdab`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- retained models:
  - `V_future_relational_witness_symbolic_insufficiency_braid`
  - `V_control_symbolic_symbolic_insufficiency_braid_regressor`

## Mean Results
- witness:
  - `mae = 0.118168`
  - `rank_correlation = 0.210777`
  - `calibration_slope = 0.322935`
- control:
  - `mae = 0.124607`
  - `rank_correlation = -0.113026`
  - `calibration_slope = -0.177230`

## Interpretation
- the perturbation was non-inert
- the witness still beat the bounded symbolic control on both declared packet metrics in the mean
- the margin narrowed versus the base braid packet, so structural hardening is justified next

## Artifact
- `logs/ablation_runs/summary/transfer_braid_cdab_v1.csv`
