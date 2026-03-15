# Q-RoPE Executive Summary v18

## BLUF
- The research line now preserves selective positional relevance with one surviving realism-bridge retrieval task and two surviving more model-like successor-class tasks.
- The newest preserved survivor is `dual-anchor-offset-consensus`.
- This strengthens the internal case for the mechanism, but still does not justify hardware reopening or external claims.

## What Changed
- `synthetic_positional_dual_anchor_offset_consensus_response` survived the full bounded hardening cycle.
- The successor-class layer now includes both:
  - `key-query-offset-selection`
  - `dual-anchor-offset-consensus`

## Decision
- Keep the line alive at low intensity.
- Keep default execution closed.
- Reopen only for a materially different missing question with explicit approval.
