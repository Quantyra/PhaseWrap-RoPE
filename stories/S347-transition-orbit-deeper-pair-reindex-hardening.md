# Story template

## Story ID and title
S347 - Transition orbit deeper pair-reindex hardening

## User value
As a research lead, I want one more non-inert pair-reindex hardening packet executed, so the branch is judged on a real robustness perturbation.

## Acceptance criteria
- run the fixed six-run packet with `pair_reindex = 7`
- compare witness against the strongest current symbolic baseline
- use the primary metric for branch outcome

## Outputs
- `docs/research/`
- `logs/ablation_runs/summary/`
- `docs/evidence/`

## Dependencies
- S346
