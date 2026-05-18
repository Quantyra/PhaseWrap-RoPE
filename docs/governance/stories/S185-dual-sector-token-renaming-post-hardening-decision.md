# Story template

## Story ID and title
S185 - Dual-sector token-renaming post-hardening decision

## User value
As a research lead, I want the dual-sector witness branch reassessed after token-renaming hardening, so the repo can choose one next bounded robustness check without broadening prematurely.

## Acceptance criteria
- Interpret the token-renaming packet result
- Decide whether the branch remains active
- Select one next bounded hardening step only

## Outputs
- `docs/research/`
- `docs/evidence/`
- `logs/checkpoint.json`

## Evidence and references
- `docs/research/q-rope-dual-sector-token-renaming-hardening-v1.md`
- `logs/ablation_runs/summary/dual_sector_token_renaming_v1.csv`

## Out of scope
- Benchmark expansion
- Remote execution
- Multiple new hardening steps in parallel

## Dependencies
- S184

## Risks
- If the branch broadens after only invariance checks, the repo may still miss brittleness to concrete sample choice.

## Unit tests (development stories only)
- No new unit tests required in this memo step.

## Cycle time
- Start: 2026-03-08 17:50 (Pacific/Honolulu)
- End: 2026-03-08 17:55 (Pacific/Honolulu)

