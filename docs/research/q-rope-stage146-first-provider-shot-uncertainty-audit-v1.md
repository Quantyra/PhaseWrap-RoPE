# QRoPE Stage 146 - First Provider Shot Uncertainty Audit

## Objective
Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, under fixed circuit width.

## Result
Stage 146 preregisters conservative shot-noise uncertainty thresholds for the IBM-first matched packet plan. It does not submit hardware jobs, create provider SDK clients, record credentials, or inspect real provider results.

Current decision: `FIRST_PROVIDER_SHOT_UNCERTAINTY_CONTRACT_READY_HARDWARE_COUNTS_REQUIRED`.

For the IBM Runtime first-provider plan, Stage 146 covers:

- 2 independent IBM windows
- 20 IBM matched packet templates
- 4 provider/window/source-lane/circuit lane summaries
- 4096 shots per matched packet row
- 16 rows per IBM packet

The conservative 95% shot-noise separation half-width for each IBM lane is `0.003828125` MAE. A later PhaseWrap lower-MAE observation should exceed this lane-specific margin against the best comparator before being described as shot-noise-separated.

## Claim Boundary
Supported:

- conservative shot-noise uncertainty thresholds for the first-provider matched packet plan
- lane-specific minimum PhaseWrap MAE margins for later shot-noise-separated interpretation
- a statistical guardrail that does not depend on provider credentials or hardware execution

Excluded:

- provider credential values
- hardware job submission
- real provider result records
- readout calibration correction
- a noisy-hardware robustness or auditability conclusion

## Evidence
- `logs/automated_stage_gates/stage146_first_provider_shot_uncertainty_audit/manifest.json`
- `logs/automated_stage_gates/stage146_first_provider_shot_uncertainty_audit/results.json`
- `logs/automated_stage_gates/stage146_first_provider_shot_uncertainty_audit/summary.csv`
