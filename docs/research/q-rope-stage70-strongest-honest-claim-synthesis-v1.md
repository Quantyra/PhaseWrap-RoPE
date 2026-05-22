# PhaseWrap-RoPE Stage 70 Strongest Honest Claim Synthesis v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 70 is a synthesis checkpoint for the active north-star goal: find the strongest honest claim PhaseWrap-RoPE can support under fair RoPE, ALiBI, sinusoidal, and no-position comparisons while preserving both positive evidence and failure modes.

It does not train another model. It reads the current stage manifests and documented source artifacts, then emits a machine-readable claim boundary.

## Reviewer Command

```bash
python scripts/run_stage70_strongest_honest_claim_synthesis.py
```

This writes:

- `logs/automated_stage_gates/stage70_strongest_honest_claim_synthesis/manifest.json`
- `logs/automated_stage_gates/stage70_strongest_honest_claim_synthesis/results.json`
- `logs/automated_stage_gates/stage70_strongest_honest_claim_synthesis/summary.csv`

## Result

Stage 70 records `BOUND_STRONGEST_HONEST_CLAIM_WITH_RETRIEVAL_FAILURES`.

The generated strongest honest claim is:

> PhaseWrap-RoPE is a compact, auditable phase-wrap positional scoring rule with reproducible hardware/readout witnesses and mixed toy/diagnostic downstream evidence. Hard and soft support-routing diagnostics show the row family can be solved, but learned scalar, nonlinear, in-decoder support-supervised, dual support/target-attention, and practical budget-sensitivity routes still fail free held-out support-to-token retrieval. A structural in-decoder support-routed copy expert repairs phase-cued retrieval for no_position too, so fair matched decoder/pointer-generator audits do not yet support RoPE replacement or positional-method promotion.

The refreshed synthesis loads source manifests through Stage 87 with no missing source artifacts. It also preserves the key positive and negative evidence:

- Stage 67 proves that standard visible content-key retrieval is solvable by the current two-block pointer-generator harness for every tested method, including `no_position`.
- Recent pointer-generator variants preserve train capacity and include tiny text-fact QA positives, with Stage 65 reaching `0.783333` best held-out top-1.
- Stage 68 shows content-key auxiliary rows do not transfer back to original phase-cued/exact-offset retrieval.
- Stage 69 shows original-task multitask training also does not repair original held-out retrieval.
- Stages 80 and 81 show hard and soft support-routed token selection can solve phase-cued retrieval, but only as non-promotional/method-nonspecific diagnostics.
- Stages 82-86 show the current learned scalar, nonlinear, in-decoder support-supervised, dual support/target-attention, and practical budget-sensitivity routes still fail held-out support-to-token retrieval.
- Stage 87 shows a structural support-routed copy expert can repair phase-cued retrieval, but `no_position` solves too and exact-offset remains below threshold.

## Interpretation

Stage 70 keeps the current posture bounded. PhaseWrap-RoPE remains RoPE-adjacent in mechanism shape because it is a phase/position scoring rule, but the current fair-comparison evidence does not justify a RoPE-replacement claim.

The strongest defensible position is that PhaseWrap-RoPE is compact, auditable, and worth continued controlled study. The unsupported position is that it is already better than RoPE in matched transformer settings.

## Claim Boundary

Supported:

- a no-credential synthesis of current fair RoPE/ALiBI/sinusoidal/no-position/PhaseWrap evidence;
- a bounded strongest-honest-claim checkpoint preserving both positive evidence and failure modes;
- a reviewer gate for deciding whether the next step should be stronger matched transformer evidence.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- a claim that PhaseWrap-RoPE replaces RoPE;
- a claim that PhaseWrap-RoPE is currently better than RoPE in fair matched transformer settings;
- a claim that content-key row redesign success is positional-method promotion evidence.

## Next Gate

Run a stronger matched decoder-only transformer or original-row mechanism that improves held-out support-to-token retrieval for phase-cued and exact-offset rows before evaluating positional-method promotion.
