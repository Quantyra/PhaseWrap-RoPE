# QRoPE Stage 147 - First Provider Calibration Confidence Audit

## Objective
Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, under fixed circuit width.

## Result
Stage 147 preregisters known-state calibration confidence thresholds for the IBM-first path. It does not submit hardware jobs, create provider SDK clients, record credentials, or inspect real provider counts.

Current decision: `FIRST_PROVIDER_CALIBRATION_CONFIDENCE_CONTRACT_READY_COUNTS_REQUIRED`.

For IBM Runtime, Stage 147 covers:

- expected bitstring order: `q1q0`
- 4 known states: `00`, `01`, `10`, `11`
- 1000 shots per known state
- Stage 101 dominant-fraction threshold: 0.80
- Wilson 95% lower-bound threshold: at least 825 dominant counts per state

## Claim Boundary
Supported:

- first-provider known-state calibration confidence thresholds before matched packet interpretation
- state-level Wilson 95% dominant-count requirements for the Stage 101 bitstring-order check
- a non-submitting calibration-confidence guardrail for later noisy-hardware evidence

Excluded:

- provider credential values
- hardware job submission
- real provider calibration counts
- readout mitigation or correction
- a noisy-hardware robustness or auditability conclusion

## Evidence
- `logs/automated_stage_gates/stage147_first_provider_calibration_confidence_audit/manifest.json`
- `logs/automated_stage_gates/stage147_first_provider_calibration_confidence_audit/results.json`
- `logs/automated_stage_gates/stage147_first_provider_calibration_confidence_audit/summary.csv`
