# Q-RoPE E010 Nested-Scope Shadow Slot-Swap Hardening v1

Date: 2026-03-17
Stories: S1592-S1594

## Packet
- Dataset:
  - synthetic_positional_nested_scope_shadow_selection_response
- Perturbation:
  - slot_swap=1
- Backend:
  - sim_quantum_statevector
- Seeds:
  - 42, 123, 777
- Variants:
  - V_future_relational_witness_positional_nested_scope_shadow_selection
  - V_control_symbolic_positional_nested_scope_shadow_selection_regressor

## Mean Packet Result
- witness:
  - mae = 0.008569
  - ank_correlation = -0.056200
  - calibration_slope = -0.227570
- control:
  - mae = 0.008626
  - ank_correlation = -0.132109
  - calibration_slope = -0.632397

## Interpretation
- slot_swap=1 was non-inert.
- The witness remained ahead on both declared mean gate metrics.
- The next valid move is the closure packet pair_reindex=7 only.
