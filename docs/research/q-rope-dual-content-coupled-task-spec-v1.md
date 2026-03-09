# Q-RoPE Dual Content-Coupled Task Specification v1

## Scope
- Story: `S196`
- Task id:
  - `synthetic_dual_sector_content_agreement_binary`
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

## Derived relational variables
For each observation derive:
- `sector in {P_small, P_large, N_small, N_large}`
- `content_family in {aligned, crossed}`

### Sector rule
Same as the current dual task:
- `P_small`
- `P_large`
- `N_small`
- `N_large`

### Content-family rule
Partition the token alphabet into:
- group `X = {A, C}`
- group `Y = {B, D}`

Then define:
- `content_family = aligned` if `(left in X and right in X)` or `(left in Y and right in Y)`
- `content_family = crossed` otherwise

This makes content-family a binary relational property of the token pair, not of one token alone.

## Higher-level agreement variables
From the two observations derive:
- `sign_agreement = 1` iff `sector_a` and `sector_b` belong to the same sign family
- `content_agreement = 1` iff `content_family_a == content_family_b`

## Label rule
Binary label:
- `1` iff `sign_agreement == content_agreement`
- `0` otherwise

This is an equality/XNOR coupling between:
- sector-sign agreement
- content-family agreement

## Why this is harder than the exhausted task
A bounded sector-pair interaction baseline can represent:
- `sign_agreement`

But it cannot represent:
- `content_agreement`

unless content-family variables are also exposed.

Likewise, a content-only baseline cannot represent:
- the coupled rule over both relational families

So the task is only meaningful if future controls declare exactly which family they can use.

## Required future control posture
Any future approval must distinguish at least:
1. sector-only interaction control
2. content-only interaction control
3. cross-family interaction control

Otherwise the repo will blur why a candidate wins or loses.

## Alignment-safe constraints
- no direct numeric offset label shortcut
- no single-token shortcut
- no absolute-position label shortcut
- balanced positive and negative classes
- balanced sector-family frequencies
- balanced content-family frequencies

## Bottom line
This is the first harder dual task in the repo that explicitly requires interaction between:
- sector-sign relation
- content-family relation

That makes it the right next memo-only target after the current dual task exhausted its uniqueness story.
