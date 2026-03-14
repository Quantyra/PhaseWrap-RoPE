# Q-RoPE Bridge Anchor-Span-Membership First Packet v1

## Packet
- Task: `synthetic_positional_anchor_span_membership_response`
- Backend: `sim_quantum_statevector`
- Seeds: `42`, `123`, `777`
- Models:
  - `V_future_relational_witness_positional_anchor_span_membership`
  - `V_control_symbolic_positional_anchor_span_membership_regressor`

## Mean Results
- Witness:
  - `mae = 0.112664`
  - `rank_correlation = -0.007937`
  - `calibration_slope = -0.294903`
- Control:
  - `mae = 0.116094`
  - `rank_correlation = 0.190476`
  - `calibration_slope = -0.065606`

## Interpretation
- The first packet is mixed.
- The witness kept better mean `mae`.
- The control kept better mean `rank_correlation`.
- That is not enough to preserve the line as a positive bridge result.

## Artifact
- Summary CSV: `logs/ablation_runs/summary/bridge_anchor_span_membership_v1.csv`
