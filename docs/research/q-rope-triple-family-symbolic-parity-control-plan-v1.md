# Research note

## Control
- `V_control_symbolic_three_family_parity`

## Feature rule
Use only the three agreement booleans already defined by the task:
- `sign_agreement`
- `content_agreement`
- `orientation_agreement`

Expose exactly one explicit symbolic parity feature:
- `triple_even_parity = 1` if the three-way parity is even
- `triple_even_parity = 0` otherwise

Optional audit fields may record the raw agreement booleans, but the trainable head must only see the parity feature.

## Why this is fair
- It is the direct symbolic analogue of the strongest signal currently used by the candidate.
- It does not add task leakage beyond the already declared agreement variables.
- It is the narrowest next baseline that can challenge the observed coefficient pattern honestly.

## Packet
- same task: `synthetic_dual_content_parity_coupling_binary`
- same seeds: `42`, `123`, `777`
- compare:
  - `V_future_relational_witness_triple`
  - `V_control_symbolic_three_family_parity`
