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
- Stage 44 records Stages 39-43 as a compact-diagnostic plateau: useful bounded mechanism evidence, not promotion evidence.
- Stage 45 runs a matched one-block decoder-only gate and records `PROMOTION_NOT_SUPPORTED`; the harness remains near chance and is not a reliable promotion discriminator.
- Stage 46 applies longer training to that one-block harness and records `CAPACITY_NOT_ESTABLISHED`; weak PhaseWrap tiny text-fact QA positives remain below the capacity threshold.
- Stage 47 applies Adam optimizer hardening and records `TRAIN_FIT_WITH_PARTIAL_GENERALIZATION`; PhaseWrap leads tiny text-fact QA, but retrieval lanes still fail held-out generalization.
- Stage 48 reruns the Adam decoder audit across five seeds and records `TINY_QA_POSITIVE_NOT_PHASEWRAP_STABLE_RETRIEVAL_FAILED`; tiny text-fact QA stays positive, but the PhaseWrap lead is not stable and retrieval still fails.

Not supported now:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- a claim that PhaseWrap-RoPE replaces RoPE;
- a claim that the Stage 4 hardware witnesses establish model advantage;
- a claim that Stage 43 solves free learned value generation or validates PhaseWrap-RoPE as a RoPE replacement.
- a claim that additional compact copy-path diagnostics should broaden the claim boundary after the Stage 44 plateau audit.
- a claim that Stage 45 validates PhaseWrap-RoPE as a replacement or production transformer mechanism.
- a claim that Stage 46 validates the one-block decoder harness as a positional-method discriminator.
- a claim that Stage 47's tiny text-fact QA positive is enough for a RoPE-replacement claim.
- a claim that the Stage 47 one-seed PhaseWrap tiny text-fact QA lead is stable across seeds.

## Decision Outcomes

The active research goal can resolve in any of three valid outcomes:

- `PROMOTE`: PhaseWrap-derived mechanisms become credible auxiliary or replacement candidates under matched transformer-style benchmarks.
- `BOUND`: PhaseWrap remains useful as a bounded modular feature, adapter, or hardware-witness system, with clear limits.
- `FALSIFY_PROMOTION`: PhaseWrap fails the transformer promotion path, while the repo preserves a defensible negative result and avoids overclaiming.

Until a matched transformer-style benchmark satisfies the evidence standard, the default outcome remains `BOUND`.

## Next Gate

The next gate should replace or materially strengthen the matched decoder-only implementation enough to generalize on retrieval tasks, then rerun the same fair RoPE, ALiBI, sinusoidal, no-position, and PhaseWrap comparison.

Preferred next direction:

- keep RoPE/ALiBI/sinusoidal/no-position/PhaseWrap comparisons matched;
- move from the partially generalizing one-block decoder-only gate into a stronger decoder-only harness;
- report ranking and calibration even if the PhaseWrap result weakens.

Because Stage 44 records the compact plateau and Stages 45-48 show the one-block decoder only partially generalizes, another diagnostic should be justified only if it directly improves retrieval generalization in the matched decoder-only transformer implementation.
