# PhaseWrap-RoPE Stage 95 Headline Interval Audit v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 95 surfaces seed confidence intervals for the current headline evidence.

It reads existing summary CSV artifacts for selected structural positives and free learned retrieval failures, extracts top-1/MRR/probability/calibration intervals, and writes them into a machine-readable manifest. This improves reporting rigor without changing the promotion boundary.

## Reviewer Command

```bash
python scripts/run_stage95_headline_interval_audit.py
```

This writes:

- `logs/automated_stage_gates/stage95_headline_interval_audit/manifest.json`
- `logs/automated_stage_gates/stage95_headline_interval_audit/results.json`
- `logs/automated_stage_gates/stage95_headline_interval_audit/summary.csv`

## Result

Stage 95 records `HEADLINE_INTERVALS_ADDED_PROMOTION_STILL_BOUND`.

Headline top-1 intervals:

| headline | stage | method | top-1 mean | interval |
| --- | --- | --- | ---: | --- |
| structural phase-cued solve | Stage 88 | `rope_relative` | `0.783333` | `[0.750000, 0.816666]` |
| structural exact-offset solve | Stage 88 | `rope_relative` | `1.000000` | `[1.000000, 1.000000]` |
| best free learned phase-cued | Stage 85 | `sinusoidal` | `0.050000` | `[0.000000, 0.116667]` |
| best free learned exact-offset | Stage 90 | `sinusoidal` | `0.433333` | `[0.316667, 0.516667]` |
| recent support-binding phase-cued | Stage 92 | `alibi` | `0.050000` | `[0.016667, 0.083333]` |
| recent support-binding exact-offset | Stage 92 | `sinusoidal` | `0.366667` | `[0.300000, 0.450000]` |

## Interpretation

The interval gap identified in Stage 94 is now addressed for selected headline artifacts. The remaining blocker is the substantive one: no current free learned artifact solves both original retrieval tasks with PhaseWrap-led methods.

This keeps the strongest honest claim bounded while making the failure reporting more defensible.

## Claim Boundary

Supported:

- a no-credential interval extraction audit for current headline structural and free learned retrieval evidence;
- seed-interval preservation for positive structural row-family solvability and negative free learned retrieval results;
- a narrowed promotion-gate gap showing interval reporting exists while PhaseWrap-led free learned retrieval evidence remains missing.

Excluded:

- a claim that PhaseWrap-RoPE replaces RoPE;
- a claim that interval reporting creates a PhaseWrap-led retrieval solve;
- a claim that structural copy experts are standard free decoder-only language modeling;
- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage.

## Next Gate

Use these surfaced intervals when reporting the bounded claim. The next model gate must still produce free learned PhaseWrap-led retrieval evidence before promotion can be reconsidered.
