# PhaseWrap-RoPE Stage 98 Noisy Hardware Robustness Goal Audit v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 98 opens a separate noisy-hardware readout-robustness track.

Goal:

> Determine whether PhaseWrap-RoPE's compact phase-wrap positional score has measurable robustness or auditability advantages on noisy quantum hardware, compared with matched positional-score encodings, under fixed circuit width.

This is not a transformer-performance goal. It is a hardware score/readout robustness goal.

## Reviewer Command

```bash
python scripts/run_stage98_noisy_hardware_robustness_goal_audit.py
```

This writes:

- `logs/automated_stage_gates/stage98_noisy_hardware_robustness_goal_audit/manifest.json`
- `logs/automated_stage_gates/stage98_noisy_hardware_robustness_goal_audit/results.json`
- `logs/automated_stage_gates/stage98_noisy_hardware_robustness_goal_audit/summary.csv`

## Result

Stage 98 records `NOISY_HARDWARE_GOAL_FRAMED_MATCHED_ENCODINGS_REQUIRED`.

Current evidence:

- Stage 4 already contains bounded two-qubit hardware-positive artifacts on IBM Runtime and Amazon Braket backends.
- The Stage 4 sweep verifier recomputes the active records from committed raw counts.
- Current records are useful evidence that the track is worth investigating.

Current blockers:

- Stage 4 does not yet compare PhaseWrap against matched fixed-width RoPE-like, sinusoidal-like, ALIBI-like, and no-position/control score encodings.
- Provider bitstring calibration specs exist, but real known-state calibration counts have not been supplied.
- Existing intervals are row-bootstrap and shot-resampling diagnostics over committed artifacts, not independent date/calibration reruns.

## Interpretation

The right research question is:

> Does the PhaseWrap positional score retain rank/support/readout structure better than matched fixed-width positional-score encodings under noisy execution?

The wrong research question is:

> Does noisy quantum hardware make PhaseWrap-RoPE better for language models?

Stage 98 keeps those separated.

## Claim Boundary

Supported:

- a no-credential goal-framing audit for a noisy-hardware readout-robustness track;
- a distinction between existing bounded Stage 4 hardware-positive artifacts and the stronger matched-encoding robustness claim;
- a fixed-width protocol gate for comparing PhaseWrap score readout with matched positional-score encodings.

Excluded:

- a claim that PhaseWrap-RoPE replaces RoPE;
- a claim that noisy quantum hardware improves language models;
- a claim that Stage 4 already proves general noisy-hardware robustness;
- provider-wide bitstring-order validation without known-state calibration counts;
- production transformer superiority;
- broad quantum advantage.

## Next Gate

Freeze matched two-qubit positional-score encoding packets for PhaseWrap, RoPE-like, sinusoidal-like, ALIBI-like, and no-position/control families before any new hardware execution.
