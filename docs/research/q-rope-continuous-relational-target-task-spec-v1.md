# Q-RoPE Continuous Relational Target Task Specification v1

## Scope
- Story: `S215`
- Task id:
  - `synthetic_dual_continuous_coupled_response`
- Status:
  - memo-only

## Sample schema
Each sample contains two observations:
- observation `A`
- observation `B`

Each observation contains:
- left token
- right token
- left position
- right position
- signed offset

## Derived relational families
For each observation derive:
- `sector in {P_small, P_large, N_small, N_large}`
- `content_family in {aligned, crossed}`
- `token_orientation in {forward, reverse}`

Across observations derive:
- `sign_agreement in {0,1}`
- `content_agreement in {0,1}`
- `orientation_agreement in {0,1}`

## Continuous target
Define one bounded real target:
- `y = 0.5 * sign_term + 0.3 * content_term + 0.2 * orientation_term`

Where:
- `sign_term = +1` if `sign_agreement = 1`, else `-1`
- `content_term = +1` if `content_agreement = 1`, else `-1`
- `orientation_term = +1` if `orientation_agreement = 1`, else `-1`

Then optionally add one bounded interaction curvature term:
- `y_final = 0.8 * y + 0.2 * sign_term * content_term * orientation_term`

This keeps the target continuous and structured while avoiding a tiny binary truth-table task.

## Why this is harder
- A classifier over a tiny set of boolean states can exactly memorize parity.
- A continuous target forces calibration of magnitude, not just cell identity.
- Future controls must model not only which region a sample belongs to, but the response level itself.

## Minimum future control posture
Any future restart must distinguish at least:
1. single-family symbolic regressor
2. two-family bounded symbolic regressor
3. full boolean-state lookup regressor

A future candidate is only interesting if it beats the bounded regressors and is competitive with the full boolean-state lookup under declared capacity limits.

## Alignment-safe constraints
- no direct numeric offset-to-target shortcut
- no absolute-position shortcut
- no token-identity-only target rule
- balanced family frequencies
- target distribution must be symmetric and centered

## Bottom line
This is the next memo-level task family for the relational-witness line.
It changes the problem class from discrete agreement classification to bounded continuous relational response prediction.
