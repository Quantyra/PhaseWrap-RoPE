# Story template

## Story ID and title
S004 - Minimal publishable experiment design and ablation grid

## User value
As a research lead, I want a compact and defensible experiment matrix, so that we can isolate Q-RoPE positional effects with publishable clarity.

## Acceptance criteria
- One primary architecture family is selected for first experiment pass.
- Ablation grid includes no-PE, additive PE, fixed-gate PE, and Q-RoPE.
- Metrics include predictive quality and hardware cost (gate count/depth).
- Reproducibility details are complete.

## Outputs
- `docs/research/q-rope-experiment-plan-v1.md`

## Evidence and references
- `docs/research/q-rope-concept-note-v1.md`
- S002 prior-art map

## Out of scope
- Large-scale hyperparameter sweeps.

## Dependencies
- S002 baseline mapping.
- S003 theorem-condition framing.

## Risks
- Benchmark choice may bias conclusions if task is too narrow.

## Unit tests (development stories only)
- Not applicable.

## Cycle time
- Start: 2026-03-05 07:25 (Pacific/Honolulu)
- End: 2026-03-05 07:33 (Pacific/Honolulu)
- Total: 00:08

## Notes
- Align with `docs/protocols/experiment-reproducibility.md`.
- Completion: benchmark track locked to QMSAN-style text classification and ablation grid formalized with hardware-cost metrics.
