# Story template

## Story ID and title
S201 - Dual content-coupled implementation

## User value
As a research lead, I want the harder dual content-coupled path implemented and run on its fixed first packet, so the repo can test whether the branch survives the stronger control stack under a truly harder task.

## Acceptance criteria
- Implement only the approved task, candidate, and three control families
- Run the fixed first packet
- Emit auditable diagnostics for all four variants

## Outputs
- `src/qrope/synthetic.py`
- `src/qrope/run.py`
- `tests/`
- `logs/ablation_runs/`
- `docs/research/`
- `docs/evidence/`
- `logs/checkpoint.json`

## Evidence and references
- `docs/research/q-rope-dual-content-coupled-implementation-plan-v1.md`

## Out of scope
- Remote execution
- Benchmark expansion
- Extra variants or controls

## Dependencies
- S200

## Risks
- If the implementation drifts beyond the fixed task/control stack, the first packet will stop being interpretable.

## Unit tests (development stories only)
- Add focused tests only for the new task and the three control families.

## Cycle time
- Start: 2026-03-08 19:55 (Pacific/Honolulu)
