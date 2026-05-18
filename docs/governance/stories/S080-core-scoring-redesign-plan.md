# Story template

## Story ID and title
S080 - Core scoring redesign plan

## User value
As a research lead, I want the next core scoring-formulation redesign planned explicitly, so we can test a more faithful Q-RoPE mechanism instead of continuing weak local proxy tuning.

## Acceptance criteria
- The redesign target for the comparison/scoring primitive is defined clearly
- The plan stays zero-credit and local-first
- The evaluation gate is explicit before implementation

## Outputs
- `docs/research/`
- `docs/evidence/`
- `logs/checkpoint.json`

## Evidence and references
- `docs/research/q-rope-next-technical-options-evaluation-v1.md`

## Out of scope
- Paid remote execution
- Benchmark/task expansion as the primary branch

## Dependencies
- S079

## Risks
- The redesign may require a larger local scoring-path refactor than the previous screening branches.

## Unit tests (development stories only)
- No new unit tests required unless code changes are introduced.

## Cycle time
- Start: 2026-03-06 14:36 (Pacific/Honolulu)

## Completion
- Completed: 2026-03-06 14:38 (Pacific/Honolulu)
- Decision: redesign the local scoring primitive around a pairwise-relative-overlap screening path, using `V0` vs `V3` local diagnostics before any broader expansion.
