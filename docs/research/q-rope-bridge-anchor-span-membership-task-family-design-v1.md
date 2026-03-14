# Q-RoPE Bridge Anchor-Span-Membership Task Family Design v1

## Intent
- Open one third bridge-task candidate that is closer to positional-encoding behavior than the transfer ladder and materially different from both `anchor-order` and `anchor-distance`.

## Core Structure
- Task family: `synthetic_positional_anchor_span_membership_response`
- Structure: `anchor -> span-left -> span-right -> probe -> resolve`
- The target depends on whether the final resolution preserves correct interval membership of the probe relative to the anchor-defined span, rather than only token identity, left/right order, or absolute distance magnitude alone.

## Why This Is a Better Bridge
- More position-like than the transfer families because the decisive relation is positional containment inside or outside an anchor-defined interval.
- Materially different from `anchor-order` because it is not only about ordering candidates around an anchor.
- Materially different from `anchor-distance` because it is not only about nearer/farther separation from an anchor.
- Still synthetic and auditable, so it stays inside the current local-only protocol.

## Candidate Witness
- `V_future_relational_witness_positional_anchor_span_membership`

## Candidate Bounded Control
- additive and bounded-quadratic regressor over declared anchor-relative span-membership summaries only
