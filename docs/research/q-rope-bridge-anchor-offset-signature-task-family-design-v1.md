# Q-RoPE Bridge Anchor-Offset-Signature Task Family Design v1

## Intent
- Open one fourth bridge-task candidate that is closer to positional-encoding behavior than the transfer ladder and materially different from `anchor-order`, `anchor-distance`, and `anchor-span-membership`.

## Core Structure
- Task family: `synthetic_positional_anchor_offset_signature_response`
- Structure: `anchor -> probe-a -> probe-b -> resolve`
- The target depends on whether the final resolution preserves the correct signed offset signature of the selected probe relative to the anchor, rather than only left/right order, raw distance magnitude, or interval membership alone.

## Why This Is a Better Bridge
- More position-like than the transfer families because the decisive relation is the signed offset class relative to an anchor.
- Materially different from `anchor-order` because it is not only about which side of the anchor comes first.
- Materially different from `anchor-distance` because it is not only about nearer/farther magnitude.
- Materially different from `anchor-span-membership` because it is not only about inside/outside containment.
- Still synthetic and auditable, so it stays inside the current local-only protocol.

## Candidate Witness
- `V_future_relational_witness_positional_anchor_offset_signature`

## Candidate Bounded Control
- additive and bounded-quadratic regressor over declared anchor-relative offset-signature summaries only
