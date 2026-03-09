# Transition Orbit Chart-Relabel Hardening Plan v1

## Hardening question
- does the witness retain its lead when latent chart ids are deterministically relabeled while orbit structure and labels are preserved?

## Fixed perturbation
- apply one bijection over chart ids before transition-table lookup
- keep orbit membership and target construction fixed
- keep rendered token nuisance handling unchanged

## Packet
- dataset: `synthetic_chart_transition_orbit_response`
- seeds: `42`, `123`, `777`
- witness: `V_future_relational_witness_transition_orbit`
- strongest current symbolic baseline: `V_control_symbolic_transition_cross_direction_regressor`
