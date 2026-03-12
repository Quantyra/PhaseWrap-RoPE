# Q-RoPE Transfer Path Deeper Pair-Reindex Hardening v1

Date: 2026-03-11
Stories: S868

## Packet
Ran one bounded structural hardening packet with:
- task:
  - `synthetic_symbolic_insufficiency_path_response`
- perturbation:
  - `pair_reindex = 7`
- backend:
  - `sim_quantum_statevector`
- seeds:
  - `42`, `123`, `777`

## Compared
- `V_future_relational_witness_symbolic_insufficiency_path`
- `V_control_symbolic_symbolic_insufficiency_path_regressor`

## Means
- witness:
  - `mae = 0.134157`
  - `rank_correlation = 0.349206`
  - `calibration_slope = 0.630060`
- control:
  - `mae = 0.193133`
  - `rank_correlation = 0.246032`
  - `calibration_slope = 0.670181`

## Interpretation
- The packet was non-inert.
- The witness remained ahead on both declared packet metrics.
- The result is weaker than the base packet on `rank_correlation`, but it still clears the frozen bounded symbolic control.
