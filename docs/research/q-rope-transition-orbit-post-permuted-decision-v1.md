# Transition Orbit Post Permuted Decision v1

## Decision
- keep the transition-orbit branch active

## Why
- `V_control_symbolic_transition_orbit_permuted_regressor` did not match the witness on mean MAE
- it also stayed weaker on mean rank correlation
- this keeps the current task alive after another bounded fairness test

## Next bounded step
- orbit-preserving token-renaming hardening
- use a label-preserving permutation that stays inside orbit families
- keep the packet local-only, zero-credit, and fixed to witness vs strongest current symbolic baseline
