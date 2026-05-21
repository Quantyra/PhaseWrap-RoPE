# PhaseWrap-RoPE Strongest Honest Claim Goal v1

Date: `2026-05-21`

Status: `active`

## Goal

Find the strongest honest claim PhaseWrap-RoPE can support under fair RoPE, ALiBI, sinusoidal, and no-position comparisons, preserving both positive evidence and failure modes.

The program should optimize for the maximum defensible claim boundary, not for proving that PhaseWrap-RoPE replaces RoPE. A negative or mixed result is successful if it cleanly separates useful PhaseWrap behavior from unsupported replacement, hardware-advantage, or production-transformer claims.

## Evidence Standard

Promotion evidence must include:

- matched positional-method comparisons against RoPE or RoPE-like, ALiBI, sinusoidal, and no-position baselines;
- non-PhaseWrap-labeled retrieval, QA, or language-model-style tasks;
- at least five seeds for learned components;
- loss or perplexity, top-1, MRR, target probability, calibration, confidence intervals, and weak-run reporting;
- failed, diverged, and underperforming runs retained in the artifact tree.

Evidence is not enough for a RoPE-replacement claim if it is only a compact bridge, a deterministic copy diagnostic, a post-hoc calibration audit, a PhaseWrap-labeled task, a small-circuit hardware witness, or a result selected only by top-1/MRR while probability and calibration remain worse.

## Current Claim Boundary

Supported now:

- PhaseWrap-RoPE is an auditable modular phase-wrap scoring rule with reproducible classical analyses.
- The repository contains bounded small-circuit hardware readout witnesses for the recorded packets, providers, dates, and calibration contexts.
- PhaseWrap-derived adapters can be competitive on ranking in several compact retrieval and copy-aware diagnostics.
- Stage 43 shows that generator-target hardening improves the Stage 42 learned vocab branch and preserves PhaseWrap-derived ranking competitiveness.

Not supported now:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- a claim that PhaseWrap-RoPE replaces RoPE;
- a claim that the Stage 4 hardware witnesses establish model advantage;
- a claim that Stage 43 solves free learned value generation or validates PhaseWrap-RoPE as a RoPE replacement.

## Decision Outcomes

The active research goal can resolve in any of three valid outcomes:

- `PROMOTE`: PhaseWrap-derived mechanisms become credible auxiliary or replacement candidates under matched transformer-style benchmarks.
- `BOUND`: PhaseWrap remains useful as a bounded modular feature, adapter, or hardware-witness system, with clear limits.
- `FALSIFY_PROMOTION`: PhaseWrap fails the transformer promotion path, while the repo preserves a defensible negative result and avoids overclaiming.

Until a matched transformer-style benchmark satisfies the evidence standard, the default outcome remains `BOUND`.

## Next Gate

The next gate should move beyond compact output-path diagnostics: either test the same fair comparison in a stronger matched decoder-only transformer, or record a bounded compact-diagnostic plateau before further claim expansion.

Preferred next direction:

- keep RoPE/ALiBI/sinusoidal/no-position/PhaseWrap comparisons matched;
- move from compact pointer-generator diagnostics toward a stronger decoder-only harness when practical;
- report ranking and calibration even if the PhaseWrap result weakens.

Because Stage 43 still leaves RoPE-like scoring clearly stronger on probability/calibration, another compact diagnostic should be justified only if it directly prepares the matched decoder-only transformer or a bounded-claim plateau audit.
