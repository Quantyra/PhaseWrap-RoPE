# Q-RoPE Transfer Loop-Closure Token-Renaming Hardening v1

Date: 2026-03-11
Stories: S889

## Packet
- task:
  - `synthetic_symbolic_insufficiency_loop_closure_response`
- perturbation:
  - `token_permutation = cdab`
- backend:
  - `sim_quantum_statevector`
- seeds:
  - `42`, `123`, `777`
- compared:
  - `V_future_relational_witness_symbolic_insufficiency_loop`
  - `V_control_symbolic_symbolic_insufficiency_loop_regressor`

## Mean Results
- witness:
  - `mae = 0.065364`
  - `rank_correlation = 0.063339`
  - `calibration_slope = 0.092894`
- control:
  - `mae = 0.066916`
  - `rank_correlation = -0.176662`
  - `calibration_slope = -0.063125`

## Interpretation
- the perturbation was non-inert
- the witness stayed ahead on both declared packet metrics in the mean
- the margin narrowed materially versus the base loop packet
- this supports keeping the branch active, but it does not justify widening the line

## Artifact
- summary:
  - `logs/ablation_runs/summary/transfer_loop_cdab_v1.csv`
