# Q-RoPE Bridge Anchor-Distance Task Family Design v1

## Intent
- Open one second bridge-task candidate that is closer to positional-encoding behavior than the earlier transfer ladder and materially different from `anchor-order`.

## Core Structure
- Task family: `synthetic_positional_anchor_distance_response`
- Structure: `anchor -> candidate-near -> candidate-far -> resolve`
- The target depends on whether the final resolution preserves the correct relative distance relationship to the anchor rather than only token identity or coarse order signs.

## Why This Is a Better Bridge
- More position-like than the transfer families because the decisive relation is anchor-relative distance magnitude.
- Materially different from `anchor-order` because it tests positional gap structure, not only left/right order around an anchor.
- Still synthetic and auditable, so it stays inside the current local-only protocol.

## Candidate Witness
- `V_future_relational_witness_positional_anchor_distance`

## Candidate Bounded Control
- additive and bounded-quadratic regressor over declared anchor-relative distance summaries only
