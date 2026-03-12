# Q-RoPE Transfer Path Token-Renaming Hardening v1

Date: 2026-03-11
Stories: S860

## Packet
- task:
  - `synthetic_symbolic_insufficiency_path_response`
- perturbation:
  - `token_permutation = cdab`
- backend:
  - `sim_quantum_statevector`
- seeds:
  - `42`, `123`, `777`
- compared:
  - `V_future_relational_witness_symbolic_insufficiency_path`
  - `V_control_symbolic_symbolic_insufficiency_path_regressor`

## Mean Results
- witness:
  - `mae = 0.085598`
  - `rank_correlation = 0.119048`
  - `calibration_slope = 0.434974`
- control:
  - `mae = 0.115659`
  - `rank_correlation = 0.238095`
  - `calibration_slope = 0.313315`

## Per-Seed Result
- seed `42`
  - witness: `mae 0.072124`, `rank_correlation -0.547619`
  - control: `mae 0.054755`, `rank_correlation 0.285714`
- seed `123`
  - witness: `mae 0.127780`, `rank_correlation 0.595238`
  - control: `mae 0.224337`, `rank_correlation -0.285714`
- seed `777`
  - witness: `mae 0.056889`, `rank_correlation 0.309524`
  - control: `mae 0.067886`, `rank_correlation 0.714286`

## Interpretation
- the packet was non-inert
- the witness stayed ahead on `mae`
- the control moved ahead on mean `rank_correlation`
- this is mixed leadership, not a stop under the current hardening rule
