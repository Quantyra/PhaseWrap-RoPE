# PhaseWrap-RoPE Stage 4 Classical Compute Cost Estimate v1

Date: `2026-05-20`

## Purpose

This note records a no-hardware, deterministic estimate of the local classical work needed to recompute the committed Stage 4 hardware sweep metrics from raw counts.

Artifacts:

- Manifest: `logs/automated_stage_gates/stage4_classical_compute_cost/manifest.json`
- Results: `logs/automated_stage_gates/stage4_classical_compute_cost/results.json`
- Summary CSV: `logs/automated_stage_gates/stage4_classical_compute_cost/summary.csv`
- Script: `scripts/estimate_stage4_classical_compute_cost.py`

Reproduce:

```bash
python scripts/estimate_stage4_classical_compute_cost.py
```

## Result

The active Stage 4 sweep contains six passing hardware records with `163072` total recorded hardware shots. The deterministic static estimate for local recomputation of expectation values, witness/control predictions, and aggregate metrics is `4096` arithmetic-scale operations. Under the artifact's declared assumption of `1,000,000` operations per second, the estimated local recomputation time is `0.004096` seconds and the incremental local verifier cost is `0.0` USD.

The sum of recorded submitted-to-completed hardware elapsed times in the committed artifacts is `808.0` seconds. This elapsed value is descriptive only: it includes provider execution and queue-related timing as recorded in the artifacts and is not a future queue-time predictor.

## Claim Boundary

This artifact supports a narrow cost/timing statement: recomputing the committed Stage 4 evidence from saved raw counts is computationally tiny and credential-free. It does not reconstruct provider billing, predict hardware queue time, establish quantum advantage or disadvantage, or make a production transformer runtime claim.
