# Story template

## Story ID and title
S045 - Rerun V4b local comparison on deterministic sim

## User value
As a research lead, I want the `V3` vs `V4` vs `V4b` local packet rerun on a deterministic simulator path, so the gate for any future remote spend is based on valid local evidence.

## Acceptance criteria
- The local packet is rerun on `sim_quantum_statevector`
- Stability metrics are recomputed from deterministic runs
- A fresh go/no-go decision is recorded for `V4b`

## Outputs
- `logs/ablation_runs/`
- `docs/research/`
- `docs/evidence/`

## Evidence and references
- `docs/research/q-rope-deterministic-local-feature-encoding-fix-v1.md`

## Out of scope
- Paid remote execution
- Broader benchmark expansion

## Dependencies
- S044

## Risks
- The deterministic rerun may materially change the previous provisional ordering.

## Unit tests (development stories only)
- Reuse current test coverage unless comparison tooling changes.

## Cycle time
- Start: 2026-03-06 11:58 (Pacific/Honolulu)
- End: 2026-03-06 12:12 (Pacific/Honolulu)

## Notes
- Keep this step zero-credit.
- Completed with a deterministic rerun and a no-go outcome because the local statevector gate is reproducible but non-discriminative across `V3`, `V4`, and `V4b`.
