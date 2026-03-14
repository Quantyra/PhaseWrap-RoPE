# Q-RoPE Transfer Counterfactual-Handoff Pair-Reindex Hardening v1

## Packet
- Task: `synthetic_symbolic_insufficiency_counterfactual_handoff_response`
- Perturbation: `pair_reindex=1`
- Backend: `sim_quantum_statevector`
- Seeds: `42`, `123`, `777`
- Models:
  - `V_future_relational_witness_symbolic_insufficiency_counterfactual_handoff`
  - `V_control_symbolic_symbolic_insufficiency_counterfactual_handoff_regressor`

## Mean Results
- Witness:
  - `mae = 0.060040`
  - `rank_correlation = 0.499091`
  - `calibration_slope = 0.862179`
- Control:
  - `mae = 0.109335`
  - `rank_correlation = -0.217764`
  - `calibration_slope = -0.242966`

## Interpretation
- The `pair_reindex=1` packet was non-inert.
- The witness stayed ahead of the bounded symbolic control on both declared packet metrics in the mean.
- This structural hardening step strengthens the line rather than narrowing it.

## Artifact
- Summary CSV: `logs/ablation_runs/summary/transfer_counterfactual_handoff_pair1_v1.csv`
