# Story template

## Story ID and title
S130 - First pair-state synthetic packet

## User value
As a research lead, I want the approved pair-state mechanism tested on the fixed synthetic falsification packet, so we can decide quickly whether the new branch has real mechanism signal over `V0`.

## Acceptance criteria
- Execute `V0` vs `V_pairstate_relational`
- Use only `synthetic_offset_binary`
- Use only seeds `42`, `123`, `777`
- Record packet-level metrics and sector diagnostics

## Outputs
- `logs/ablation_runs/`
- `docs/research/`
- `docs/evidence/`
- `logs/checkpoint.json`

## Evidence and references
- `docs/research/q-rope-pairstate-implementation-v1.md`
- `docs/research/q-rope-pair-state-restart-brief-draft-v1.md`

## Out of scope
- Remote execution
- Benchmark expansion
- Additional pair-state branches

## Dependencies
- S129

## Risks
- If the packet result is mixed or collapse-like, the bounded branch should stop immediately rather than broaden.

## Unit tests (development stories only)
- Reuse the focused local suite as needed; no new test obligations unless implementation changes.

## Cycle time
- Start: 2026-03-07 20:03 (Pacific/Honolulu)
- End: 2026-03-07 20:07 (Pacific/Honolulu)
