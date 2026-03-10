# Q-RoPE Transition Orbit Order Margin Task Specification v1

Date: 2026-03-11
Stories: S392

## Task
- task id: `synthetic_transition_orbit_order_margin_response`
- posture: memo-only

## Target Rule
- each example contains one fixed candidate set within a coarse orbit-transition state
- the target is not top-1 identity and not full list ranking
- the target is the normalized margin between:
  - the highest latent orbit-order candidate
  - the second-highest latent orbit-order candidate
- target range: `[0, 1]`

## Why This Is Different
- the stopped listwise branch failed on top-1 accuracy under deeper pair perturbation
- this task preserves only the residual signal that remained stronger under the witness: ordering margin structure
- it is materially different from the stopped task because it scores separation strength inside the ranking, not only the winning slot

## Required Generator Conditions
- coarse-state lookup near-null
- within-state margin variation across seeds
- no deterministic reduction to top-1 index alone
- token-view balance preserved
