# Relay-Binding Pair-Reindex Hardening v1

Status: completed

Packet:
- task: `synthetic_symbolic_insufficiency_relay_binding_response`
- perturbation: `pair_reindex=1`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- retained models:
  - `V_future_relational_witness_symbolic_insufficiency_relay_binding`
  - `V_control_symbolic_symbolic_insufficiency_relay_binding_regressor`

Hardening packet means:
- witness:
  - `mae = 0.083597`
  - `rank_correlation = 0.412440`
  - `calibration_slope = 0.921238`
- control:
  - `mae = 0.101134`
  - `rank_correlation = -0.008335`
  - `calibration_slope = -0.356471`

Interpretation:
- The first structural perturbation was non-inert.
- The witness stayed ahead of the bounded symbolic control on both declared packet metrics in the mean.
- The relay-binding branch remains active.
