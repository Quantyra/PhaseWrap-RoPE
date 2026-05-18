# Story template

## Story ID and title
S019 - Quantum simulator backend integration

## User value
As a research lead, I want a real quantum simulator backend path integrated, so empirical runs can include actual circuit simulation instead of purely classical surrogates.

## Acceptance criteria
- Backend `sim_quantum_statevector` is implemented.
- One real-mode run executes through this backend and writes metrics.
- Tests pass for quantum backend execution path.

## Outputs
- `src/qrope/qsim.py`
- `src/qrope/run.py` updates
- `docs/research/q-rope-quantum-simulator-backend-v1.md`

## Evidence and references
- `logs/ablation_runs/v3-yelp-qsim-s42/metrics.json`
- test output for `tests/test_run_real_mode.py`

## Out of scope
- Cloud photonic hardware execution.

## Dependencies
- S011

## Risks
- Internal simulator is minimal and not equivalent to full photonic stack behavior.

## Unit tests (development stories only)
- Validate quantum backend path in `test_run_real_mode.py`.

## Cycle time
- Start: 2026-03-05 10:20 (Pacific/Honolulu)
- End: 2026-03-05 10:27 (Pacific/Honolulu)
- Total: 00:07

## Notes
- Completion: actual internal statevector quantum simulator backend integrated and validated.
