# Q-RoPE Transition Orbit Order-Margin First Packet v1

Date: 2026-03-11
Stories: S398

## Packet
- task: `synthetic_transition_orbit_order_margin_response`
- candidate: `V_future_relational_witness_transition_orbit_order_margin`
- controls:
  - `V_control_symbolic_transition_margin_lookup`
  - `V_control_symbolic_transition_margin_cross_direction`
  - `V_control_symbolic_transition_margin_quadratic`
  - `V_control_symbolic_transition_margin_orbit_permuted`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`

## Generator Gate
- `coarse_margin_lookup_near_null_pass = true`
- `within_state_margin_variation_pass = true`
- `top1_only_shortcut_absent = true`
- `token_view_balance_pass = true`

## Mean Metrics
- witness:
  - MAE `0.167608`
  - rank correlation `-0.254275`
  - calibration slope `-0.254561`
- lookup:
  - MAE `0.197879`
  - rank correlation `0.000000`
- cross-direction:
  - MAE `0.194488`
  - rank correlation `0.115623`
- quadratic:
  - MAE `0.196027`
  - rank correlation `-0.049917`
- orbit-permuted:
  - MAE `0.192962`
  - rank correlation `0.089594`

## Per-Seed Witness Readout
- seed `42`: MAE `0.153947`, rank correlation `0.076290`
- seed `123`: MAE `0.172423`, rank correlation `-0.340207`
- seed `777`: MAE `0.176454`, rank correlation `-0.498908`

## Interpretation
- the witness led the packet on mean MAE
- the witness failed on the second declared primary metric
- rank correlation was negative on two of three seeds
- this packet is not approval-grade under the active branch rule
