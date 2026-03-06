# Story template

## Story ID and title
S046 - Local quantum screening circuit redesign

## User value
As a research lead, I want the local quantum screening backend to discriminate between positional variants, so local promotion decisions are technically meaningful before any remote spend.

## Acceptance criteria
- The current non-discriminative behavior is documented
- A concrete redesign direction for the local screening circuit is specified
- The redesign is scoped as zero-credit local work

## Outputs
- `docs/research/`
- `docs/evidence/`

## Evidence and references
- `docs/research/q-rope-v4b-deterministic-local-comparison-packet-v1.md`

## Out of scope
- Paid remote execution
- Broad benchmark expansion

## Dependencies
- S045

## Risks
- A stronger local circuit may increase simulation cost or still fail to separate variants.

## Unit tests (development stories only)
- None unless code implementation starts in this story.

## Cycle time
- Start: 2026-03-06 12:12 (Pacific/Honolulu)
- End: 2026-03-06 12:20 (Pacific/Honolulu)

## Notes
- Keep this step zero-credit.
- Completed with a concrete redesign direction centered on stronger phase-to-amplitude conversion and richer local readout.
