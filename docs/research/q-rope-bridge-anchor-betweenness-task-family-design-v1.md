# Q-RoPE Bridge Anchor-Betweeness Task Family Design v1

## Intent
- Open one fifth bridge-task candidate that is closer to positional-encoding behavior than the transfer ladder and materially different from `anchor-order`, `anchor-distance`, `anchor-span-membership`, and `anchor-offset-signature`.

## Core Structure
- Task family: `synthetic_positional_anchor_betweenness_response`
- Structure: `left-bound -> anchor -> right-bound -> probe -> resolve`
- The target depends on whether the final resolution preserves correct positional betweenness of the probe relative to the ordered anchor-bounded frame, rather than only side, raw distance, interval membership, or signed offset class alone.

## Why This Is a Better Bridge
- More position-like than the transfer families because the decisive relation is ordered betweenness inside an anchor-centered frame.
- Materially different from `anchor-order` because it is not only about which side of the anchor comes first.
- Materially different from `anchor-distance` because it is not only about nearer or farther separation from an anchor.
- Materially different from `anchor-span-membership` because it depends on ordered betweenness within a frame rather than simple inside or outside containment.
- Materially different from `anchor-offset-signature` because it is not only about signed directional offset class.
- Still synthetic and auditable, so it stays inside the current local-only protocol.

## Candidate Witness
- `V_future_relational_witness_positional_anchor_betweenness`

## Candidate Bounded Control
- additive and bounded-quadratic regressor over declared anchor-relative betweenness summaries only
