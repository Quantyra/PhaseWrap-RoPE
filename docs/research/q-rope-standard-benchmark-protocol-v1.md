# PhaseWrap-RoPE Standard Benchmark Protocol v1

Date: `2026-05-23`

Status: `implemented_primary_gate`

## Purpose

This protocol defines the next evidence-producing transformer benchmark before any stronger RoPE-facing claim. It exists to keep the public claim boundary honest: PhaseWrap-RoPE is currently supported as a compact phase-wrap feature and bounded hardware witness, not as a proven RoPE replacement.

Implementation status: Stage 219 now applies this protocol to the Stage 30 matched retrieval bridge as the primary bounded benchmark and Stage 32 as full-context corroboration. The result supports bounded substitution with measured degradation, not general RoPE replacement.

## Promotion Question

Can a PhaseWrap-derived positional mechanism improve a matched trained attention model on a non-phase-cued long-context task when compared with `no_position`, sinusoidal, ALiBI, and RoPE-style baselines under the same training budget?

## Minimum Benchmark

The first implementation should be intentionally small but reviewer-clean:

- task family: passkey or RULER-style retrieval where labels are not generated from the PhaseWrap score;
- context lengths: train short, evaluate at held-out longer lengths;
- seeds: at least five initialization/data seeds;
- model: same architecture, optimizer, scheduler, batch size, gradient clipping, and token budget for every method;
- methods: `no_position`, `sinusoidal`, `alibi`, `rope_relative`, `phasewrap_bias`, and `phasewrap_adapter`;
- reporting: every failed, diverged, or underperforming run remains in the artifact tree.

## Metrics

Headline metrics must include:

- validation loss or perplexity;
- retrieval top-1 accuracy;
- mean reciprocal rank;
- target probability mass;
- expected calibration error or an equivalent calibration statistic;
- confidence intervals over seeds.

Top-1 or MRR alone is not enough to promote the claim, because earlier stages showed PhaseWrap-derived adapters can recover argmax behavior while RoPE-like scoring remains stronger on probability/calibration.

## Claim Gate

A positive benchmark may support only this claim:

> Under a matched small-transformer benchmark, a PhaseWrap-derived positional mechanism improves a bounded non-phase-cued retrieval metric relative to specified baselines.

It does not support:

- general RoPE replacement;
- production transformer superiority;
- quantum advantage;
- hardware-specific computational benefit.

## Required Artifacts

The implementation should write:

- config file with all model/training/task settings;
- per-seed raw metrics;
- aggregate metrics with intervals;
- verifier script that recomputes the claim table from raw metrics;
- README/paper update that reports both positive and negative outcomes.
