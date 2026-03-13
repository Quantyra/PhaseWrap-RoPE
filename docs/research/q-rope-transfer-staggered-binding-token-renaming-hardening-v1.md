# Q-RoPE Transfer Staggered Binding Token Renaming Hardening v1

## Packet
- Task: synthetic_symbolic_insufficiency_staggered_binding_response
- Perturbation: 	oken_permutation=cdab
- Backend: sim_quantum_statevector
- Seeds: 42, 123, 777
- Retained models:
  - V_future_relational_witness_symbolic_insufficiency_staggered_binding
  - V_control_symbolic_symbolic_insufficiency_staggered_binding_regressor

## Mean Results
- Witness:
  - mae = 0.070201
  - ank_correlation = 0.004902
  - calibration_slope = -0.226177
- Control:
  - mae = 0.079477
  - ank_correlation = 0.228432
  - calibration_slope = 0.149638

## Interpretation
- The perturbation was non-inert.
- The witness stayed ahead on mae.
- The control led on mean ank_correlation.
- Under the declared two-metric gate, mixed leadership is not enough.
