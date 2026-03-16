# Q-RoPE E005 Shared-Memory Multi-Query Token-Renaming Hardening v1

Date: 2026-03-15
Stories: S1435-S1437

## Fixed Hardening Packet
- dataset: `synthetic_positional_shared_memory_multi_query_selection_response`
- hardening: `token_permutation=cdab`
- witness: `V_future_relational_witness_positional_shared_memory_multi_query_selection`
- control: `V_control_symbolic_positional_shared_memory_multi_query_selection_regressor`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`

## Mean Hardening Results
- witness:
  - `mae = 12.734432`
  - `rank_correlation = -0.067087`
  - `calibration_slope = 0.300410`
- control:
  - `mae = 0.018994`
  - `rank_correlation = -0.032134`
  - `calibration_slope = 0.142855`

## Interpretation
- `token_permutation=cdab` was strongly non-inert.
- The bounded symbolic control beat the witness on both declared mean gate metrics.
- Under the declared two-metric stop rule, the line stops immediately at retained nuisance hardening.

## Summary CSV
- `logs/ablation_runs/summary/E005_shared_memory_multi_query_selection_cdab_v1.csv`
