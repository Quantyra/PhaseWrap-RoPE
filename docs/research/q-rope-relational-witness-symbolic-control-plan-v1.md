# Q-RoPE Relational Witness Symbolic-Control Plan v1

## Scope
- Story: `S169`
- Task: `synthetic_sector_parity_binary`
- Backend: local-only
- Seeds: `42`, `123`, `777`
- Candidate comparator:
  - `V_future_relational_witness` under `contrasts_only`
- New control:
  - `V_control_symbolic_relational`

## Why this step exists
The witness branch now has a compact winning schema.

That removes most internal mechanism ambiguity.
The next validity question is external:
- does the compact quantum-derived contrast core still beat a fair direct symbolic relational baseline?

## Fixed control schema
Use one direct symbolic sector encoding only.

### Allowed features
One-hot sector identity:
- `sec_P_small`
- `sec_P_large`
- `sec_N_small`
- `sec_N_large`

Exactly one feature is `1` per sample.
All others are `0`.

### Forbidden features
- token identity
- raw token pair identity
- absolute positions
- numeric offset sign
- numeric offset magnitude
- handcrafted task-parity scalar
- hidden layers or feature crosses

## Head constraint
Use the same head family as the witness branch:
- logistic-regression-equivalent only
- no hidden layers
- no sweeps
- no ensembles

## Exact packet
Run the same fixed three-seed packet on:
- `V_future_relational_witness` with `contrasts_only`
- `V_control_symbolic_relational`

Keep fixed:
- task
- split policy
- seeds
- local-only execution

## Why sector one-hot is the right control
It is the strongest fair symbolic baseline.

If it matches the witness perfectly, then:
- the task is linearly easy once sector identity is explicit
- the quantum branch remains interesting, but not yet uniquely necessary on this task

If it trails the witness, then:
- the quantum-derived continuous relational contrast is adding information beyond explicit symbolic sector identity alone

## Required outputs
For both paths, emit:
- mean accuracy
- mean F1
- coefficients
- intercept
- feature schema

## What is explicitly not allowed
- second symbolic control families
- token-aware classical baselines
- remote execution
- new tasks

## Bottom line
This control is intentionally strong.
It is the right next bounded test because it directly answers whether the current witness win is still meaningful once a tiny classical model is given explicit sector identity.
