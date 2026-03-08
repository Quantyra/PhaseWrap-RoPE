# Q-RoPE Sector-Parity Task Spec v1

## Decision
- preserve one exact alignment-safe synthetic candidate:
  - `synthetic_sector_parity_binary`

## Task rule
Keep the same four sectors:
- `P_small`
- `P_large`
- `N_small`
- `N_large`

Assign labels by crossed sector parity:
- label `1` for:
  - `P_small`
  - `N_large`
- label `0` for:
  - `N_small`
  - `P_large`

## Why this is better than the old task
The old family labeled by sign of offset.

This one does not:
- positive labels are not all positive-sign offsets
- negative labels are not all negative-sign offsets

So a mechanism cannot win merely by recovering offset sign.

## Why this still preserves relational structure
The task still depends only on:
- relative offset sector
- not raw token identity
- not absolute position alone

So it remains a clean relational test, just with a harder and less tautological target.

## Archive value
This spec gives the repo one exact future restart family that:
- reuses the pair-state sector language
- blocks the previous shortcut
- stays small enough for a bounded synthetic falsification packet

## Future restart bar
A future branch should only get implementation approval on this family if:
- its sector-level responses are declared up front
- it beats `V0` across seeds `42/123/777`
- and its gain cannot be reduced to pooled-score drift
