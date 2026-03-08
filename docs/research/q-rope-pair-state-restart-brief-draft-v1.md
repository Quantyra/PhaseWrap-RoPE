# Q-RoPE Pair-State Restart Brief Draft v1

Submitting this brief would not authorize implementation.
It is a draft gate document only.

## 1. Restart title
- brief title: `Pair-State Relational Restart`
- date: `2026-03-07`
- owner: `Quantyra Research`

## 2. Mechanism hypothesis
- New mechanism:
  - represent each token pair as one joint pair-state with explicit relative-offset sectors
  - measure sector-contrast relational response directly
- Materially different from the paused line:
  - does not depend on branch-local phase plus downstream scalar recovery
  - does not reuse the stopped parity-contrast branch-local comparator
- Not another tuning tweak because:
  - the represented object changes
  - the measured object changes

## 3. Failure mode targeted
- Targeted failure mode:
  - prior branches encoded phase but failed to convert it into stronger relative-offset discrimination
- Why this may help:
  - relative offset becomes explicit state structure rather than an inferred downstream relation
- Why this should beat uniform score shift:
  - success is tied to sector contrast, not total score elevation

## 4. Exact state-preparation structure
- state object:
  - one joint pair-state over `(x_i, x_j, i, j)`
- where token content enters:
  - token-pair content block
- where positional information enters:
  - explicit relative-offset sectors
- what remains interpretable:
  - token-pair content block
  - offset-sector block
  - coupling rule between them

## 5. Exact interference/comparison structure
- comparison primitive:
  - no separate branch comparison in the old sense
  - the relation is embedded directly into the pair-state and interrogated by sector contrast
- where relative operator structure is exposed:
  - in the pair-state sector definition for signed offset
- why this is phase-sensitive:
  - relative-offset sectors may still carry phase structure, but phase is subordinate to the explicit relational partition
- why this is not the stopped pairwise-overlap branch:
  - it does not ask similarity magnitude to recover relation after the fact

## 6. Exact observable
- observable definition:
  - sector-contrast relational measurement
  - positive-offset response minus negative-offset response
- why it distinguishes relative-phase contrast from global score elevation:
  - it compares relational sectors rather than one total-state scalar
- working evidence condition:
  - positive/negative sector contrast must improve over `V0`

## 7. Synthetic falsification packet
- dataset: `synthetic_offset_binary`
- seeds: `42`, `123`, `777`
- baseline: `V0`
- proposed variant: `V_pairstate_relational`
- readout policy: sector-contrast relational measurement
- no-remote confirmation: `required`

## 8. Predeclared success criteria
Required in advance:
- mean accuracy condition:
  - must not regress materially versus `V0`
- mean F1 condition:
  - may improve, but cannot be the sole win condition
- score-vs-offset improvement:
  - relational sector contrast must improve over `V0`
- offset-gap improvement:
  - positive-minus-negative offset gap must improve over `V0`
- non-uniform-shift condition:
  - effect must be attributable to sector contrast, not total score elevation alone

## 9. Predeclared failure criteria
Stop immediately if:
- mixed headline metrics with no mechanism win
- no sector-contrast structure gain
- no offset-gap improvement
- effect explainable by uniform score elevation
- one-seed-only improvement

## 10. Minimal implementation boundary
- exact files expected to change:
  - `src/qrope/qsim.py`
  - `src/qrope/run.py`
  - possibly `src/qrope/synthetic.py` only if diagnostics require it
- exact files not allowed to change:
  - remote backends
  - cloud scripts
  - broader benchmark configs
- tests required before first run:
  - focused local simulator and runner tests
- diagnostics required per run:
  - sector responses
  - offset-gap summary
  - evidence against uniform score shift

## 11. Budget and scope guardrails
- Quandela credits allowed: `0`
- IBM remote allowed: `no`
- broad benchmark expansion allowed: `no`
- new variant branching allowed: `only V_pairstate_relational`

## 12. Decision request
- Why approval could be justified:
  - this is the cleanest materially different angle preserved in archive posture
- smallest decisive experiment:
  - one local synthetic packet against `V0`
- immediate stop result:
  - any failure of offset-gap or sector-contrast improvement

## Status
- `draft only`
- `not approved`
- `archive-safe`

