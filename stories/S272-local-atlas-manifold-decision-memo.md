# Story template

## Story ID and title
S272 - Local atlas manifold decision memo

## User value
As a research lead, I want the local atlas manifold branch closed cleanly after its first packet if it fails, so the repo does not drift into low-value iteration on an exhausted task.

## Acceptance criteria
- Record the packet outcome
- Record the stop decision
- Return the branch to memo-only posture

## Outputs
- `docs/research/`
- `docs/evidence/`
- `logs/checkpoint.json`

## Dependencies
- S271
