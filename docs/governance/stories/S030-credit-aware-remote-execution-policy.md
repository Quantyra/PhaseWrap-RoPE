# Story template

## Story ID and title
S030 - Credit-aware remote execution policy

## User value
As a research lead, I want explicit credit-aware execution rules, so remote runs do not silently burn limited provider budgets.

## Acceptance criteria
- Repo policy states which steps are zero-credit vs credit-consuming.
- Remote execution requires explicit budget-awareness in notes/runbooks.
- Current provider credit uncertainty is documented.

## Outputs
- `docs/research/`
- `docs/governance/stories/`

## Evidence and references
- `docs/research/q-rope-quandela-credit-recovery-note-v1.md`

## Out of scope
- Building provider-side balance APIs
- Manuscript drafting

## Dependencies
- S029

## Risks
- Official provider docs may not expose exact cost-per-run formulas.

## Unit tests (development stories only)
- n/a

## Cycle time
- Start: 2026-03-06 08:16 (Pacific/Honolulu)
- End: 2026-03-06 08:22 (Pacific/Honolulu)
- Total: 00:06

## Notes
- Completed with explicit zero-credit vs credit-consuming rules and run-budget gating for Quandela.
- Policy does not estimate exact remaining runs because no source-backed credit-per-run formula is currently available.
