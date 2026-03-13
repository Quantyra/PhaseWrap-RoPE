# Relay-Binding Token-Renaming Hardening v1

Status: completed

Packet:
- task: `synthetic_symbolic_insufficiency_relay_binding_response`
- perturbation: `token_permutation=cdab`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- retained models:
  - `V_future_relational_witness_symbolic_insufficiency_relay_binding`
  - `V_control_symbolic_symbolic_insufficiency_relay_binding_regressor`

Hardening packet means:
- witness:
  - `mae = 0.069986`
  - `rank_correlation = 0.255407`
  - `calibration_slope = 0.354386`
- control:
  - `mae = 0.076181`
  - `rank_correlation = -0.031041`
  - `calibration_slope = -0.065107`

Interpretation:
- The perturbation was non-inert.
- The witness stayed ahead of the bounded symbolic control on both declared packet metrics in the mean.
- The relay-binding branch remains active.
