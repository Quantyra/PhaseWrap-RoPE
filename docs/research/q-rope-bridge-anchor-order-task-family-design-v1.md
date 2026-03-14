# Q-RoPE Bridge Anchor-Order Task Family Design v1

## Intent
- Open one bridge-task candidate that is closer to positional-encoding behavior than the current transfer ladder.

## Core Structure
- Task family: `synthetic_positional_anchor_order_response`
- Structure: `anchor -> candidate-left -> candidate-right -> resolve`
- The target depends on whether the final resolution matches the correct order of the two candidates relative to the anchor rather than on absolute token identity alone.

## Why This Is a Better Bridge
- More position-like than the current transfer families because the decisive relation is relative order around an anchor.
- Still synthetic and auditable, so it stays inside the current local-only protocol.
- Closer to a positional-encoding question than:
  - `path`
  - `loop-closure`
  - `fork-join`
  - `relay-binding`
  - `cascade-reconciliation`
  - `counterfactual-handoff`

## Candidate Witness
- `V_future_relational_witness_positional_anchor_order`

## Candidate Bounded Control
- additive and bounded-quadratic regressor over declared anchor-relative order summaries only
