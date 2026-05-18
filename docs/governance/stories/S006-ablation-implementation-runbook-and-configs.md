# Story template

## Story ID and title
S006 - Ablation implementation runbook and configs

## User value
As a research lead, I want an execution-ready runbook and configuration package, so that the first Q-RoPE ablation batch runs reproducibly.

## Acceptance criteria
- Runbook includes end-to-end commands for all ablation variants (`V0-V3`).
- Config files specify fixed seeds, dataset splits, and training budgets.
- Logging schema captures metrics plus hardware-cost fields.

## Outputs
- `docs/research/q-rope-ablation-runbook-v1.md`
- `configs/ablation/`

## Evidence and references
- `docs/research/q-rope-experiment-plan-v1.md`
- `docs/protocols/experiment-reproducibility.md`

## Out of scope
- Final manuscript writing.

## Dependencies
- S004 and S005 completion.

## Risks
- Hidden implementation differences between variants may invalidate comparisons.

## Unit tests (development stories only)
- n/a

## Cycle time
- Start: 2026-03-05 07:53 (Pacific/Honolulu)
- End: 2026-03-05 08:05 (Pacific/Honolulu)
- Total: 00:12

## Notes
- Launch story after architecture codebase path is confirmed.
- Completion: runbook and variant configs (`V0-V3`) created with fixed seeds, split policy, logging schema, and canonical execution commands.
