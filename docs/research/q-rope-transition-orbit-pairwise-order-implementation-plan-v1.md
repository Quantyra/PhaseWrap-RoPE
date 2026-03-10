# Q-RoPE Transition Orbit Pairwise Order Implementation Plan v1

Date: 2026-03-11
Stories: S368-S369

## Writable Scope
- [synthetic.py](C:/Users/Dan/Desktop/Projects/QuantyraQRope/src/qrope/synthetic.py)
- [run.py](C:/Users/Dan/Desktop/Projects/QuantyraQRope/src/qrope/run.py)
- focused tests only:
  - [test_synthetic.py](C:/Users/Dan/Desktop/Projects/QuantyraQRope/tests/test_synthetic.py)
  - [test_run_real_mode.py](C:/Users/Dan/Desktop/Projects/QuantyraQRope/tests/test_run_real_mode.py)

## Required Additions
- generator: `generate_transition_orbit_pairwise_order_binary_bundle(...)`
- candidate backend path:
  - `V_future_relational_witness_transition_orbit_order`
- control backend paths:
  - `V_control_symbolic_transition_order_lookup`
  - `V_control_symbolic_transition_order_cross_direction`
  - `V_control_symbolic_transition_order_quadratic`
  - `V_control_symbolic_transition_order_orbit_permuted`

## Packet
- one fixed 15-run packet
- seeds `42/123/777`
- candidate plus four controls

## Required Artifacts
- implementation note
- first packet memo
- decision memo
- one summary CSV

## Branch Rule
The branch remains active only if the witness leads on the primary classification metrics against the fixed bounded control stack.
