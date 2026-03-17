# Q-RoPE E010 Nested-Scope Shadow Deeper Pair-Reindex Hardening v1

Date: 2026-03-17
Stories: S1595-S1598

## Packet
- Dataset:
  - synthetic_positional_nested_scope_shadow_selection_response
- Perturbation:
  - pair_reindex=7
- Backend:
  - sim_quantum_statevector
- Seeds:
  - 42, 123, 777
- Variants:
  - V_future_relational_witness_positional_nested_scope_shadow_selection
  - V_control_symbolic_positional_nested_scope_shadow_selection_regressor

## Mean Packet Result
- witness:
  - mae = 0.011088
  - ank_correlation = 0.353937
  - calibration_slope = 0.478495
- control:
  - mae = 0.016712
  - ank_correlation = -0.033415
  - calibration_slope = -0.203220

## Interpretation
- pair_reindex=7 was non-inert.
- The witness remained ahead on both declared mean gate metrics.
- The nested-scope shadow line survived the full retained hardening ladder.
