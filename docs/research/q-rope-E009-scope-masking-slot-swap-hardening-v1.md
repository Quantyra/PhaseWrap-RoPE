# Q-RoPE E009 Scope-Masking Slot-Swap Hardening v1

Date: 2026-03-17
Stories: S1560-S1562

## Fixed Packet
- dataset: `synthetic_positional_scope_masked_reference_selection_response`
- perturbation: `slot_swap=1`
- witness: `V_future_relational_witness_positional_scope_masked_reference_selection`
- control: `V_control_symbolic_positional_scope_masked_reference_selection_regressor`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`

## Mean Packet Results
- witness:
  - `mae = 0.015967`
  - `rank_correlation = 0.217958`
  - `calibration_slope = 1.088827`
- control:
  - `mae = 0.016591`
  - `rank_correlation = 0.082318`
  - `calibration_slope = 0.156209`

## Interpretation
- `slot_swap=1` was non-inert.
- The witness remained ahead on both declared mean packet metrics.
- The next valid move is the closure packet `pair_reindex=7` only.

## Summary CSV
- `logs/ablation_runs/summary/E009_scope_masking_slot1_v1.csv`
