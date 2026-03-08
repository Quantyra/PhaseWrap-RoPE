# Q-RoPE Pair-State Measurement Operator Memo v1

## Status
- `memo-only`
- `archive-safe`
- `not approved for implementation`

## Goal
Define one candidate measurement-operator family for `V_pairstate_relational` that stays relational long enough to avoid collapsing into another global-score proxy.

## Candidate operator family
Use a `sector-resolved signed-response operator` family.

Conceptually:
- each sector has its own response channel
- the operator reads sector-resolved response before final aggregation

For the four-sector scheme:
- `M(P_small)`
- `M(P_large)`
- `M(N_small)`
- `M(N_large)`

## Candidate primary operator
Primary relational signal:
- `O_sign = [M(P_small) + M(P_large)] - [M(N_small) + M(N_large)]`

This is consistent with the sector memo, but here the emphasis is operational:
- the operator family must expose each term separately before the final subtraction

## Candidate auxiliary operator
Auxiliary stability operator:
- `O_stability = - ( |M(P_small) - M(P_large)| + |M(N_small) - M(N_large)| )`

Interpretation:
- strong sign contrast with poor intra-sign stability is a weak mechanism result

## Anti-collapse criterion
The pair-state angle should be rejected if the proposed implementation would only make available:
- one pooled scalar response
- or one pooled parity-like summary before sector resolution

Reason:
- that would reproduce the exact compression failure mode the archive is trying to avoid

## What counts as an acceptable operator direction
An acceptable future operator direction must:
1. expose sector-level responses explicitly
2. support signed contrast after, not before, sector resolution
3. preserve visibility of asymmetric failures across sub-sectors

## What remains open
Even after this memo, two details remain open:
- the exact low-level encoding rule for the content block
- the exact low-level realization of sector-resolved measurement in the simulator

So the pair-state direction is still not ready for implementation approval.

## Bottom line
The leading operator direction for the pair-state angle is now:
- sector-resolved signed-response measurement

And the key anti-collapse rule is explicit:
- if measurement is pooled before sector resolution, the angle should be rejected.

