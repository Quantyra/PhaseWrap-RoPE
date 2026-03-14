# Q-RoPE Bridge Anchor-Betweenness First Packet v1

## Fixed Packet
- dataset: `synthetic_positional_anchor_betweenness_response`
- witness: `V_future_relational_witness_positional_anchor_betweenness`
- control: `V_control_symbolic_positional_anchor_betweenness_regressor`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`

## Mean Packet Results
- witness:
  - `mae = 0.092816`
  - `rank_correlation = 0.087302`
  - `calibration_slope = 0.138591`
- control:
  - `mae = 0.101360`
  - `rank_correlation = -0.333333`
  - `calibration_slope = -0.637973`
