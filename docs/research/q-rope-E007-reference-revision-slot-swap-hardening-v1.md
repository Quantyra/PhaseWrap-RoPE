# Q-RoPE E007 Reference Revision Slot-Swap Hardening v1

Date: 2026-03-16
Stories: S1496-S1498

## Fixed Packet
- dataset: `synthetic_positional_reference_revision_selection_response`
- perturbation: `slot_swap=1`
- witness: `V_future_relational_witness_positional_reference_revision_selection`
- control: `V_control_symbolic_positional_reference_revision_selection_regressor`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`

## Mean Packet Results
- witness:
  - `mae = 0.025234`
  - `rank_correlation = 0.389474`
  - `calibration_slope = 0.958636`
- control:
  - `mae = 0.028721`
  - `rank_correlation = 0.203446`
  - `calibration_slope = 0.725894`

## Interpretation
- `slot_swap=1` was non-inert.
- The witness remained ahead on both declared mean gate metrics.
- The control took one seed on `rank_correlation`, but did not recover the mean two-metric gate.
- The line advances only to the closure packet `pair_reindex=7`.

## Summary CSV
- `logs/ablation_runs/summary/E007_reference_revision_slot1_v1.csv`
