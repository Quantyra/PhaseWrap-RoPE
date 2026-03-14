# Q-RoPE Transfer Echo-Resolution Token-Renaming Hardening v1

## Packet
- task: `synthetic_symbolic_insufficiency_echo_resolution_response`
- perturbation: `token_permutation=cdab`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- models:
  - `V_future_relational_witness_symbolic_insufficiency_echo_resolution`
  - `V_control_symbolic_symbolic_insufficiency_echo_resolution_regressor`

## Mean Results
- Witness:
  - `mae = 0.086174`
  - `rank_correlation = 0.099605`
  - `calibration_slope = 0.188653`
- Control:
  - `mae = 0.094488`
  - `rank_correlation = 0.261729`
  - `calibration_slope = 0.892792`

## Interpretation
- `token_permutation=cdab` was non-inert.
- The witness kept the lower mean `mae`.
- The bounded symbolic control took the higher mean `rank_correlation`.
- Under the declared two-metric gate, mixed leadership stops the line.

## Artifact
- Summary CSV: `logs/ablation_runs/summary/transfer_echo_resolution_cdab_v1.csv`
