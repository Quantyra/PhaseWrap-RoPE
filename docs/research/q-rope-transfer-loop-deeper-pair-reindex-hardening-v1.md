# Q-RoPE Transfer Loop-Closure Deeper Pair-Reindex Hardening v1

Date: 2026-03-11
Stories: S898

## Packet
- task:
  - `synthetic_symbolic_insufficiency_loop_closure_response`
- perturbation:
  - `pair_reindex = 7`
- backend:
  - `sim_quantum_statevector`
- seeds:
  - `42`, `123`, `777`
- compared:
  - `V_future_relational_witness_symbolic_insufficiency_loop`
  - `V_control_symbolic_symbolic_insufficiency_loop_regressor`

## Mean Results
- witness:
  - `mae = 0.046279`
  - `rank_correlation = 0.565547`
  - `calibration_slope = 0.774584`
- control:
  - `mae = 0.088880`
  - `rank_correlation = -0.183958`
  - `calibration_slope = -0.164278`

## Interpretation
- the deeper perturbation was non-inert
- the witness stayed ahead on both declared packet metrics in the mean
- this is the strongest packet inside the loop hardening cycle

## Artifact
- summary:
  - `logs/ablation_runs/summary/transfer_loop_pair7_v1.csv`
