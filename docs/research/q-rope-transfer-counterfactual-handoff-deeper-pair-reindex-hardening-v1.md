# Q-RoPE Transfer Counterfactual-Handoff Deeper Pair-Reindex Hardening v1

## Packet
- Task: `synthetic_symbolic_insufficiency_counterfactual_handoff_response`
- Perturbation: `pair_reindex=7`
- Backend: `sim_quantum_statevector`
- Seeds: `42`, `123`, `777`
- Models:
  - `V_future_relational_witness_symbolic_insufficiency_counterfactual_handoff`
  - `V_control_symbolic_symbolic_insufficiency_counterfactual_handoff_regressor`

## Mean Results
- Witness:
  - `mae = 0.071772`
  - `rank_correlation = 0.633949`
  - `calibration_slope = 1.394101`
- Control:
  - `mae = 0.117851`
  - `rank_correlation = 0.044135`
  - `calibration_slope = -0.007205`

## Interpretation
- The `pair_reindex=7` packet was non-inert.
- The witness stayed ahead of the bounded symbolic control on both declared packet metrics in the mean.
- The line survived the full bounded hardening cycle.

## Artifact
- Summary CSV: `logs/ablation_runs/summary/transfer_counterfactual_handoff_pair7_v1.csv`
