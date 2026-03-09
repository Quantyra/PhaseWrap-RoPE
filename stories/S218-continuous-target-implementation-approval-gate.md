# Story template

## Story ID and title
S218 - Continuous target implementation approval gate

## User value
As a research lead, I want a real go/no-go gate for the continuous target path, so the repo either reopens one bounded implementation phase or stays memo-only.

## Acceptance criteria
- Decide approve vs hold
- If approved, limit scope to one local-only synthetic packet
- If held, document the exact remaining gap

## Outputs
- `docs/research/`
- `docs/evidence/`
- `logs/checkpoint.json`

## Dependencies
- S217
