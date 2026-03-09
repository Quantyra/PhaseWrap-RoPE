# Story template

## Story ID and title
S318 - Token-invariant chart-transition decision memo

## User value
As a research lead, I want the branch closed cleanly after the packet, so the repo preserves only the next memo-only angle instead of drifting into invalid execution.

## Acceptance criteria
- decide stop or continue
- preserve one materially new next angle if stopped
- return the line to memo-only posture if it fails

## Outputs
- `docs/research/`
- `docs/evidence/`
- `logs/checkpoint.json`

## Dependencies
- S317
