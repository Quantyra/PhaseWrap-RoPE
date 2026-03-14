# Q-RoPE Transfer Selector-Arbitration First Packet v1

## Packet
- Task: `synthetic_symbolic_insufficiency_selector_arbitration_response`
- Backend: `sim_quantum_statevector`
- Seeds: `42`, `123`, `777`
- Models:
  - `V_future_relational_witness_symbolic_insufficiency_selector_arbitration`
  - `V_control_symbolic_symbolic_insufficiency_selector_arbitration_regressor`

## Mean Results
- Witness:
  - `mae = 0.150487`
  - `rank_correlation = -0.228432`
  - `calibration_slope = -0.467896`
- Control:
  - `mae = 0.138308`
  - `rank_correlation = -0.499019`
  - `calibration_slope = -0.589566`

## Interpretation
- The declared packet metrics for this line are:
  - `mae`
  - `rank_correlation`
- The control kept the lower mean `mae`.
- The witness kept the stronger mean `rank_correlation`.
- Under the declared two-metric gate, mixed leadership stops the line.

## Artifact
- Summary CSV: `logs/ablation_runs/summary/transfer_selector_arbitration_v1.csv`
