# Q-RoPE E007 Reference Revision Pair-Reindex Hardening v1

Date: 2026-03-16
Stories: S1493-S1495

## Fixed Packet
- dataset: `synthetic_positional_reference_revision_selection_response`
- perturbation: `pair_reindex=1`
- witness: `V_future_relational_witness_positional_reference_revision_selection`
- control: `V_control_symbolic_positional_reference_revision_selection_regressor`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`

## Mean Packet Results
- witness:
  - `mae = 0.019141`
  - `rank_correlation = 0.363269`
  - `calibration_slope = 0.835984`
- control:
  - `mae = 0.022156`
  - `rank_correlation = -0.019540`
  - `calibration_slope = -0.165309`

## Interpretation
- `pair_reindex=1` was non-inert.
- The witness remained ahead on both declared mean gate metrics.
- The first structural packet strengthened the line relative to the retained nuisance packet.

## Summary CSV
- `logs/ablation_runs/summary/E007_reference_revision_pair1_v1.csv`
