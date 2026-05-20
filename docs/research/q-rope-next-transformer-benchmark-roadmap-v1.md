# PhaseWrap-RoPE Next Transformer Benchmark Roadmap v1

Date: `2026-05-20`

Status: `planned`

## Purpose

This roadmap defines the evidence needed before PhaseWrap-RoPE can be presented as a credible RoPE-replacement candidate rather than an auditable phase-wrap scoring rule with bounded hardware witnesses and toy downstream checks.

The current repository already separates three tracks:

- the mathematical score: a classical modular phase feature;
- the transformer hypothesis: unproven until matched trained-model ablations show value;
- the hardware witness: a small-circuit readout audit of the score, not evidence of model advantage.

This document makes the next promotion gate explicit.

## Minimum Next Milestone

The next high-impact experiment should be a real transformer ablation where the positional mechanism is the intended experimental variable.

Required comparison set:

| Variant | Requirement |
| --- | --- |
| `no_position` | Same architecture with no explicit positional mechanism. |
| `sinusoidal` | Fixed sinusoidal positional baseline. |
| `alibi` | ALiBI-style attention bias baseline. |
| `rope` | RoPE or RoPE-like rotary query/key baseline. |
| `phasewrap_bias` | PhaseWrap-derived positional attention bias. |
| `phasewrap_adapter` | Learned adapter around PhaseWrap positional features. |
| `phasewrap_rotation` | Optional query/key rotation analogue if implemented without giving oracle labels. |

Controls:

- matched parameter counts, with any extra PhaseWrap parameters explicitly reported;
- matched optimizer, scheduler, batch size, gradient clipping, training tokens, and hyperparameter budget;
- at least five initialization/data seeds;
- train-short/test-long context extrapolation;
- all failed, diverged, or underperforming runs retained in the artifact tree;
- confidence intervals over seeds for all headline metrics.

Metrics:

- loss or perplexity;
- retrieval top-1 accuracy;
- mean reciprocal rank;
- target probability or another calibration-sensitive score;
- expected calibration error or comparable calibration statistic;
- confidence intervals for each metric and method.

## Task Requirements

The benchmark must include at least one task where the answer is not constructed from the PhaseWrap score.

Preferred task lanes:

| Lane | Examples | Reason |
| --- | --- | --- |
| Standard retrieval | Needle-in-Haystack, passkey retrieval, multi-needle retrieval | Tests positional recall without using PhaseWrap as the label generator. |
| RULER-style retrieval | multi-hop retrieval, aggregation, variable tracking | Tests compositional long-context behavior. |
| Compact QA or language modeling | controlled text-fact QA, small natural-language corpus | Checks whether the mechanism survives a non-synthetic text setting. |
| Synthetic diagnostics | phase-cued retrieval, alias/adversarial rows | Preserves interpretability, but cannot be the sole success criterion. |

Stage 26 provides a useful compact content-key QA packet. Stage 27 adds a compact attention bridge over that packet with five deterministic model initialization seeds. Stage 28 adds a compact attention bridge directly over non-phase-cued RULER-style retrieval rows. The next step is to move these structures into a stronger small decoder-only transformer or a standard retrieval harness while preserving matched compute, multiple seeds, and failed-run reporting.

## PhaseWrap Mechanism Requirements

The PhaseWrap variant should be implemented as a positional mechanism comparable to RoPE or ALiBI, not as a scalar oracle feature.

Acceptable implementations include:

- positional attention bias derived from PhaseWrap residual features;
- learned adapter around PhaseWrap residual features;
- query/key rotation analogue tied to the phase-wrap feature map;
- hybrid mechanism that combines PhaseWrap features with explicit distance, if the extra features are also reported for baselines or treated as a separate adapter family.

Unacceptable promotion evidence:

- a target label directly algebraically generated from the same PhaseWrap feature exposed to the model;
- selecting the winning method from top-1 or MRR alone while hiding loss, probability mass, or calibration;
- reporting a phase-cued synthetic task as a standard retrieval or language-model benchmark.

## Hardware Track

The hardware track should remain framed as an auditable witness for a classical phase score.

Next hardware hardening items:

- execute the predeclared provider bit-order calibration circuits for each hardware provider before interpreting provider-specific bitstrings;
- report bootstrap intervals over rows and shot-resampling intervals from raw counts;
- run independent reruns across different dates, queue conditions, and calibration windows;
- keep product-state, CX, and future entangling witness families separate in the manifest and report;
- include classical compute-equivalent timing or operation-count estimates when discussing hardware cost.

These items improve artifact reliability. They do not, by themselves, establish quantum-enhanced attention or model advantage.

## Theory Track

Stage 11 shows that the fixed 8/12 score is a mod-24 periodic feature with translation invariance, mirror aliases, context-length alias growth, period-pair tradeoffs, and exact small Fourier support. Stage 29 connects that theory to retrieval rows by auditing the Stage 11 period-pair grid on Stage 12 and Stage 22 non-phase-cued packets; the audit shows that period-pair swaps alone do not solve the fixed-score retrieval gap.

Open theory questions:

- which task distributions benefit from the 8/12 aliases and which are harmed by them;
- whether the score can be treated as a low-rank positional kernel;
- when a classical periodic feature map approximates the same behavior;
- whether other period pairs improve alias behavior under non-phase-cued retrieval;
- how PhaseWrap features should be combined with distance or content features without becoming an oracle label.

## Promotion Gate

PhaseWrap-RoPE can be described as a credible RoPE-replacement candidate only after a matched trained-transformer benchmark shows competitive performance against RoPE, ALiBI, sinusoidal, and no-position baselines on at least one non-PhaseWrap-labeled task, across multiple seeds, with confidence intervals and failed-run artifacts.

Until then, the supported claim remains narrower: PhaseWrap-RoPE is a compact, auditable phase-wrap positional scoring rule with reproducible classical analyses, bounded hardware readout witnesses, and mixed but useful toy downstream evidence.

## Researcher Use Context

The repository software is released under `AGPL-3.0-only`. Patent and IP-status notices are documented in `PATENTS.md` and `docs/publication/patent-status-note-v1.md`. Researchers should treat those notices as licensing and IP context, not as scientific evidence.
