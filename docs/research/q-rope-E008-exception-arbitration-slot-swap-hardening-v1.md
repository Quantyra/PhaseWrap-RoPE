# Q-RoPE E008 Exception Arbitration Slot-Swap Hardening v1

Date: 2026-03-16
Stories: S1528-S1530

## Fixed Packet
- dataset: `synthetic_positional_exception_conditioned_reference_selection_response`
- perturbation: `slot_swap=1`
- witness: `V_future_relational_witness_positional_exception_conditioned_reference_selection`
- control: `V_control_symbolic_positional_exception_conditioned_reference_selection_regressor`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`

## Mean Packet Results
- witness:
  - `mae = 0.014916`
  - `rank_correlation = 0.548505`
  - `calibration_slope = 0.784550`
- control:
  - `mae = 0.019995`
  - `rank_correlation = 0.122221`
  - `calibration_slope = 0.367758`

## Interpretation
- `slot_swap=1` was non-inert.
- The witness remained ahead on both declared mean gate metrics.
- The line advances only to the closure packet `pair_reindex=7`.

## Summary CSV
- `logs/ablation_runs/summary/E008_exception_arbitration_slot1_v1.csv`
