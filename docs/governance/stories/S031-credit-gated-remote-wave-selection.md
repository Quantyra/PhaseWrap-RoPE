# Story template

## Story ID and title
S031 - Credit-gated remote wave selection

## User value
As a research lead, I want the next Quandela remote wave selected under an explicit budget gate, so limited credits are spent only on the highest-value evidence.

## Acceptance criteria
- Identify the smallest next remote evidence packet worth spending credits on.
- State why the packet changes the evidence state more than the alternatives.
- Mark whether the step should proceed now or wait for a larger budget.

## Outputs
- `docs/research/`
- `docs/governance/stories/`

## Evidence and references
- `docs/research/q-rope-credit-aware-remote-execution-policy-v1.md`
- `docs/research/q-rope-matched-remote-supplemental-note-v1.md`

## Out of scope
- Executing the remote wave itself unless explicitly approved
- Manuscript drafting

## Dependencies
- S030

## Risks
- Without a provider-side balance API or cost formula, wave sizing remains approximate.

## Unit tests (development stories only)
- n/a

## Cycle time
- Start: 2026-03-06 08:23 (Pacific/Honolulu)
- End: 2026-03-06 08:31 (Pacific/Honolulu)
- Total: 00:08

## Notes
- Completed with decision: do not spend additional Quandela credits yet.
- The already-completed 3-seed matched remote packet is sufficient to justify a zero-credit synthesis pass before any further paid wave.
