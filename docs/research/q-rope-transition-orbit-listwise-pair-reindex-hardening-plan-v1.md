# Q-RoPE Transition Orbit Listwise Pair-Reindex Hardening Plan v1

Date: 2026-03-11
Stories: S385

## Next Packet
- task: `synthetic_transition_orbit_listwise_ranking`
- perturbation: `pair_reindex = 1`
- candidate: `V_future_relational_witness_transition_orbit_listwise`
- comparison controls:
  - `V_control_symbolic_transition_list_cross_direction`
  - `V_control_symbolic_transition_list_orbit_permuted`

## Rule
- the witness must remain at least tied on top-1 accuracy and still lead on order-F1
- if it loses the primary listwise metric after this non-inert pairing perturbation, stop the execution branch

## Scope
- local-only
- zero-credit
- no new controls
- no task expansion
