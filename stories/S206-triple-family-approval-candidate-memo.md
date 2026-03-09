# Story template

## Story ID and title
S206 - Triple-family approval-candidate memo

## User value
As a research lead, I want the triple-family witness task raised to approval-candidate status only if its controls and falsification packet are explicit enough, so implementation does not restart on an under-specified branch.

## Acceptance criteria
- Assess whether the task and control stack are specific enough for an approval gate
- Either elevate to approval-candidate or record the blocking gap
- Keep the work memo-only

## Outputs
- `docs/research/`
- `docs/evidence/`
- `logs/checkpoint.json`

## Dependencies
- S205
