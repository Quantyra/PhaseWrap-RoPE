# Relay-Binding Slot-Swap Hardening v1

Status: completed

Packet:
- task: `synthetic_symbolic_insufficiency_relay_binding_response`
- perturbation: `slot_swap=1`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- retained models:
  - `V_future_relational_witness_symbolic_insufficiency_relay_binding`
  - `V_control_symbolic_symbolic_insufficiency_relay_binding_regressor`

Hardening packet means:
- witness:
  - `mae = 0.071185`
  - `rank_correlation = 0.361765`
  - `calibration_slope = 0.836729`
- control:
  - `mae = 0.105258`
  - `rank_correlation = 0.068627`
  - `calibration_slope = -0.271780`

Interpretation:
- The structural perturbation was non-inert.
- The witness stayed ahead of the bounded symbolic control on both declared packet metrics in the mean.
- The relay-binding branch remains active.
