# Q-RoPE E010 Nested-Scope Shadow First Packet v1

Date: 2026-03-17
Stories: S1582-S1585

## Fixed Packet
- dataset: `synthetic_positional_nested_scope_shadow_selection_response`
- witness: `V_future_relational_witness_positional_nested_scope_shadow_selection`
- control: `V_control_symbolic_positional_nested_scope_shadow_selection_regressor`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`

## Mean Packet Results
- witness:
  - `mae = 0.009715`
  - `rank_correlation = 0.335252`
  - `calibration_slope = 1.184847`
- control:
  - `mae = 0.012971`
  - `rank_correlation = 0.143085`
  - `calibration_slope = 0.934954`

## Interpretation
- The witness beat the bounded symbolic control on both declared mean packet metrics.
- The nested-scope shadow task stayed within the frozen fairness contract.
- The line has earned exactly one next move: retained nuisance hardening with `token_permutation=cdab`.

## Summary CSV
- `logs/ablation_runs/summary/E010_nested_scope_shadow_v1.csv`
