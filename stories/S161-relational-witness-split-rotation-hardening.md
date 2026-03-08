# Story template

## Story ID and title
S161 - Relational witness split-rotation hardening

## User value
As a research lead, I want the positive witness result checked under a minimal alternate split policy, so we can measure robustness without broadening scope.

## Acceptance criteria
- Implement one deterministic split-rotation policy
- Reuse the same task, candidate, seeds, and diagnostics
- Compare against the original packet without adding new branches

## Outputs
- `src/qrope/`
- `tests/`
- `logs/ablation_runs/`
- `docs/research/`
- `docs/evidence/`
- `logs/checkpoint.json`

## Evidence and references
- `docs/research/q-rope-relational-witness-validity-hardening-plan-v1.md`
- `docs/research/q-rope-first-relational-witness-packet-v1.md`

## Out of scope
- New tasks
- New variants
- Remote execution

## Dependencies
- S160

## Risks
- If hardening broadens beyond split robustness, the branch may lose the causal clarity earned by the first positive packet.

## Unit tests (development stories only)
- Add focused split-policy tests only.

## Cycle time
- Start: 2026-03-08 11:13 (Pacific/Honolulu)
- End: 2026-03-08 11:25 (Pacific/Honolulu)
