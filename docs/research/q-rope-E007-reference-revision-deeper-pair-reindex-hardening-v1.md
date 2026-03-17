# Q-RoPE E007 Reference Revision Deeper Pair-Reindex Hardening v1

Date: 2026-03-16
Stories: S1499-S1502

## Fixed Packet
- dataset: `synthetic_positional_reference_revision_selection_response`
- perturbation: `pair_reindex=7`
- witness: `V_future_relational_witness_positional_reference_revision_selection`
- control: `V_control_symbolic_positional_reference_revision_selection_regressor`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`

## Mean Packet Results
- witness:
  - `mae = 0.030521`
  - `rank_correlation = 0.464923`
  - `calibration_slope = 0.936892`
- control:
  - `mae = 0.036370`
  - `rank_correlation = -0.196616`
  - `calibration_slope = -0.639053`

## Interpretation
- `pair_reindex=7` was non-inert.
- The witness remained ahead on both declared mean gate metrics.
- The line survived the full bounded hardening ladder and qualifies for preservation rather than further default perturbation expansion.

## Summary CSV
- `logs/ablation_runs/summary/E007_reference_revision_pair7_v1.csv`
