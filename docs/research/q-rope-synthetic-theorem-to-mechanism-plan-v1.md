# Q-RoPE Synthetic Theorem-to-Mechanism Plan v1

## Decision
Restart the initiative only through a zero-credit synthetic validation path that directly tests whether the relative-phase construction expresses relative-offset structure under controlled conditions.

## Why this is the right restart path
The current benchmark and remote evidence are too unstable to support a publication or active expansion path.
But the original theorem target is still precise:
- `P(i)^dagger P(j) = P(j - i)`
- relative-position behavior should emerge inside the comparison primitive

The salvage question is therefore narrower than the original program:
- does the mechanism express the intended inductive bias at all when token content, offsets, and labels are fully controlled?

## Restart principles
- `zero-credit only`
- `local-only`
- `causally interpretable`
- `mechanism-first, benchmark-second`
- `no broad architecture search`

## First synthetic task family
Use tightly controlled pairwise offset tasks where the label depends on relative displacement rather than semantic token content.

### Task family A: signed relative-offset classification
Construct token pairs `(x_i, x_j)` with controlled token identities and positions `(i, j)`.
Set the label from offset structure only, for example:
- positive if `(j - i) in D_pos`
- negative if `(j - i) in D_neg`

Token identities should be balanced so token-content shortcuts are weak or removable.

### Task family B: relative-offset bucket prediction
Given a pair `(i, j)`, predict the bucket of `(j - i)`, for example:
- near
- mid
- far

This tests whether the phase mechanism preserves a monotone or structured offset response rather than only a binary threshold.

### Task family C: same-offset retrieval mini-task
Given a query pair with offset `d`, retrieve the matching candidate pair from a small candidate set whose token identities are permuted but offset structure is controlled.

This is the closest synthetic bridge to the original query-key thesis.

## Required controls
- balanced token vocabulary across classes
- balanced absolute positions so absolute-index shortcuts are weak
- train/test offset stratification documented explicitly
- fixed deterministic generation with stored seeds
- `V0` as content-only baseline
- `V3` as active relative-phase path

## First restart packet
Start with the smallest decisive packet:
- backend: `sim_quantum_statevector`
- scoring paths:
  - current proxy path
  - one synthetic comparison path aligned to the task
- variants:
  - `V0`
  - `V3`
- datasets:
  - synthetic offset binary
  - synthetic offset bucket
- seeds:
  - `42`, `123`, `777`

## Restart gate
The salvage restart is `GO` only if all of the following hold on the first synthetic packet:
1. `V3` beats `V0` on mean task performance for at least one synthetic family tied directly to offset structure.
2. The observed lift is consistent across at least two of the three seeds.
3. Diagnostics show the score changes track relative offset more clearly under `V3` than `V0`.
4. The result can be explained without relying on token-content leakage or threshold-only effects.

If any of these fail, the salvage path should be paused again rather than expanded.

## Diagnostics required for restart
- score vs relative-offset curves
- within-offset variance by seed
- token-permutation sensitivity
- absolute-position leakage checks
- simple separability summaries for `V0` vs `V3`

## Explicit non-goals
- no remote execution
- no photonic-provider work
- no IBM work
- no new `V4`/`V5` branch
- no manuscript preparation

## Next step
Specify the first synthetic dataset family and generation protocol, then implement only the minimum local machinery needed to run it.
