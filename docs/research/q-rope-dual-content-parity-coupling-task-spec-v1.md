# Q-RoPE Dual Content Parity Coupling Task Specification v1

## Scope
- Story: `S204`
- Task id:
  - `synthetic_dual_content_parity_coupling_binary`
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

## Derived variables
For each observation derive:
- `sector in {P_small, P_large, N_small, N_large}`
- `content_family in {aligned, crossed}`
- `token_orientation in {forward, reverse}`

### Sector rule
Same as the current dual task family:
- `P_small`
- `P_large`
- `N_small`
- `N_large`

### Content-family rule
Partition the token alphabet into:
- group `X = {A, C}`
- group `Y = {B, D}`

Then define:
- `content_family = aligned` if both tokens come from the same group
- `content_family = crossed` otherwise

### Token-orientation rule
Map tokens to cyclic indices:
- `A = 0`, `B = 1`, `C = 2`, `D = 3`

Then define:
- `token_orientation = forward` iff `(idx(right) - idx(left)) mod 4 in {1, 2}`
- `token_orientation = reverse` otherwise

This keeps the third family pair-relational rather than single-token-based.

## Cross-observation agreement variables
Derive:
- `sign_agreement = 1` iff `sector_a` and `sector_b` belong to the same sign family
- `content_agreement = 1` iff `content_family_a == content_family_b`
- `orientation_agreement = 1` iff `token_orientation_a == token_orientation_b`

## Label rule
Binary label:
- `1` iff `sign_agreement xor content_agreement xor orientation_agreement == 0`
- `0` otherwise

Equivalently:
- positive class = even parity over the three agreement bits
- negative class = odd parity over the three agreement bits

## Why this is harder
The exhausted task could be solved by an explicit symbolic control over:
- `sign_agreement`
- `content_agreement`

This new task requires a third relational family:
- `orientation_agreement`

So a bounded control that only sees cross-family sign/content agreement is no longer sufficient.

## Minimum future control posture
Any future restart must distinguish at least:
1. sector-only interaction control
2. content-only interaction control
3. sign-content cross interaction control
4. orientation-only interaction control
5. two-family bounded symbolic control

A candidate should only be considered interesting if it clears that stack before any expansion.

## Alignment-safe constraints
- no direct numeric offset label shortcut
- no absolute-position label shortcut
- no single-token-only feature rule
- balanced positive and negative classes
- balanced sector-family frequencies
- balanced content-family frequencies
- balanced orientation-family frequencies

## Bottom line
This is the next memo-level harder task for the relational-witness line.
It adds one more pair-relational family while keeping the task bounded and auditable.
