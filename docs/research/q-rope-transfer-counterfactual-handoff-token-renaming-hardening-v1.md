# Q-RoPE Transfer Counterfactual-Handoff Token-Renaming Hardening v1

## Packet
- Task: `synthetic_symbolic_insufficiency_counterfactual_handoff_response`
- Perturbation: `token_permutation=cdab`
- Backend: `sim_quantum_statevector`
- Seeds: `42`, `123`, `777`
- Models:
  - `V_future_relational_witness_symbolic_insufficiency_counterfactual_handoff`
  - `V_control_symbolic_symbolic_insufficiency_counterfactual_handoff_regressor`

## Mean Results
- Witness:
  - `mae = 0.089160`
  - `rank_correlation = 0.086141`
  - `calibration_slope = 0.170833`
- Control:
  - `mae = 0.105955`
  - `rank_correlation = 0.084729`
  - `calibration_slope = 0.255280`

## Interpretation
- The token-renaming packet was non-inert.
- The witness stayed ahead of the bounded symbolic control on both declared packet metrics in the mean.
- The `rank_correlation` margin narrowed materially, so the line stays active but should advance only to structural hardening.

## Artifact
- Summary CSV: `logs/ablation_runs/summary/transfer_counterfactual_handoff_cdab_v1.csv`
