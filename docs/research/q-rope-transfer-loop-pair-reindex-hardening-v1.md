# Q-RoPE Transfer Loop-Closure Pair-Reindex Hardening v1

Date: 2026-03-11
Stories: S892

## Packet
- task:
  - `synthetic_symbolic_insufficiency_loop_closure_response`
- perturbation:
  - `pair_reindex = 1`
- backend:
  - `sim_quantum_statevector`
- seeds:
  - `42`, `123`, `777`
- compared:
  - `V_future_relational_witness_symbolic_insufficiency_loop`
  - `V_control_symbolic_symbolic_insufficiency_loop_regressor`

## Mean Results
- witness:
  - `mae = 0.049351`
  - `rank_correlation = 0.224757`
  - `calibration_slope = 0.358089`
- control:
  - `mae = 0.060533`
  - `rank_correlation = -0.067719`
  - `calibration_slope = -0.486749`

## Interpretation
- the perturbation was non-inert
- the witness stayed ahead on both declared packet metrics in the mean
- this is the first structural hardening step on the loop line, and it supports keeping the branch active

## Artifact
- summary:
  - `logs/ablation_runs/summary/transfer_loop_pair1_v1.csv`
