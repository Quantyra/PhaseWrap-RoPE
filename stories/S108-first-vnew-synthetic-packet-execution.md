# Story template

## Story ID and title
S108 - First V_new synthetic packet execution

## User value
As a research lead, I want the bounded restart mechanism tested on the fixed synthetic falsification packet, so we can decide quickly whether the new comparator has any real signal over `V0`.

## Acceptance criteria
- Execute `V0` vs `V_new_explicit_interference`
- Use only `synthetic_offset_binary`
- Use only seeds `42`, `123`, `777`
- Record packet-level summary and diagnostics

## Outputs
- `logs/ablation_runs/`
- `logs/diagnostics/`
- `docs/research/`
- `docs/evidence/`
- `logs/checkpoint.json`

## Evidence and references
- `docs/research/q-rope-filled-restart-brief-v1.md`
- `docs/research/q-rope-synthetic-falsification-packet-v1.md`
- `docs/research/q-rope-vnew-implementation-v1.md`

## Out of scope
- Remote execution
- Benchmark expansion
- Additional mechanism families

## Dependencies
- S107

## Risks
- If the packet is mixed or null, the bounded restart should stop quickly rather than reopen broad experimentation.

## Unit tests (development stories only)
- Reuse the focused local test suite as needed; no new test obligations unless implementation changes.

## Cycle time
- Start: 2026-03-07 14:15 (Pacific/Honolulu)
- End: 2026-03-07 14:18 (Pacific/Honolulu)
