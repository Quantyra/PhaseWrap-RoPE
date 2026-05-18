# Story template

## Story ID and title
S044 - Deterministic local feature encoding fix

## User value
As a research lead, I want the local quantum simulation path to be deterministic across process launches, so local stability gates are decision-grade before any remote spend.

## Acceptance criteria
- The feature-angle mapping no longer depends on process-salted Python hashing
- Repeated identical local runs produce identical metrics
- Focused reproducibility tests pass

## Outputs
- `src/qrope/`
- `tests/`
- `docs/research/`
- `docs/evidence/`

## Evidence and references
- `docs/research/q-rope-v4b-local-comparison-packet-v1.md`

## Out of scope
- Paid remote execution
- Broad benchmark reruns

## Dependencies
- S043

## Risks
- Fixing deterministic encoding may materially change prior local comparison results.

## Unit tests (development stories only)
- Add focused reproducibility coverage.

## Cycle time
- Start: 2026-03-06 11:45 (Pacific/Honolulu)
- End: 2026-03-06 11:58 (Pacific/Honolulu)

## Notes
- Keep this step zero-credit.
- Completed with a deterministic SHA-256-based feature encoder, passing reproducibility validation across separate process launches.
