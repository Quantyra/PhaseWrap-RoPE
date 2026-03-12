# Q-RoPE Transfer Braid First Packet v1

Date: 2026-03-12
Stories: S941

## Packet
- task: `synthetic_symbolic_insufficiency_braid_crossing_response`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- models:
  - `V_future_relational_witness_symbolic_insufficiency_braid`
  - `V_control_symbolic_symbolic_insufficiency_braid_regressor`

## Mean Results
- witness:
  - `mae = 0.110535`
  - `rank_correlation = 0.492445`
  - `calibration_slope = 0.884615`
- control:
  - `mae = 0.127084`
  - `rank_correlation = 0.204614`
  - `calibration_slope = 0.288201`

## Interpretation
- the braid transfer branch is active
- the witness beat the bounded symbolic control on both declared packet metrics in the mean
- one seed favored the control on `mae`, but the control did not clear the two-metric gate overall

## Artifact
- `logs/ablation_runs/summary/transfer_braid_v1.csv`
