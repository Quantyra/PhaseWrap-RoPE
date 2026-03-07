# Story template

## Story ID and title
S081 - Pairwise relative-overlap implementation plan

## User value
As a research lead, I want the pairwise-relative-overlap screening path translated into a minimal implementation plan, so we can test a more faithful Q-RoPE comparison primitive locally before any broader expansion.

## Acceptance criteria
- The pairwise-overlap implementation boundary is explicit
- The first diagnostic packet is locked
- The promotion gate is preserved exactly

## Outputs
- `docs/research/`
- `docs/evidence/`
- `logs/checkpoint.json`

## Evidence and references
- `docs/research/q-rope-core-scoring-redesign-plan-v1.md`

## Out of scope
- Paid remote execution
- Benchmark/task expansion as the primary branch

## Dependencies
- S080

## Risks
- Even the more faithful pairwise scoring path may still fail to separate `V3` from baselines on the current local datasets.

## Unit tests (development stories only)
- No new unit tests required unless code changes are introduced.

## Cycle time
- Start: 2026-03-06 14:38 (Pacific/Honolulu)

## Completion
- Completed: 2026-03-06 14:40 (Pacific/Honolulu)
- Decision: add one pairwise-overlap diagnostic path beside the current proxy path, using a small `V0` vs `V3` local packet before any broader refactor.
