# PhaseWrap-RoPE Stage 9 Trained Transformer Ablation Plan v1

Date: `2026-05-20`

Status: `planned`

## Purpose

Stage 9 is the next evidence milestone for the RoPE-replacement research lane. Its goal is to test PhaseWrap-RoPE inside trained small decoder-only transformers where the only intended experimental variable is the positional mechanism.

Stage 9 is not a hardware experiment. It should run without quantum-provider credentials.

## Claim Boundary

Stage 9 may support a narrow statement that a PhaseWrap positional mechanism is competitive on the tested small trained-transformer tasks if the results support that conclusion.

Stage 9 must not be reported as:

- proof that PhaseWrap-RoPE replaces RoPE;
- production language-model superiority;
- broad context-length generalization;
- quantum advantage;
- evidence that the Stage 4 hardware witness improves model performance.

## Model Variants

The minimum comparison set is:

| Variant | Positional mechanism |
| --- | --- |
| `no_position` | no explicit positional signal |
| `sinusoidal` | fixed sinusoidal position features |
| `alibi` | ALiBI-style attention bias |
| `rope` | rotary query/key position mechanism |
| `phasewrap_bias` | PhaseWrap-derived attention bias |
| `phasewrap_adapter` | learned adapter around PhaseWrap features |

The PhaseWrap variants should be implemented as real positional mechanisms rather than scalar oracle labels. Acceptable forms include a positional attention bias, a query/key rotation analogue, or a learned adapter around PhaseWrap features.

## Training Controls

All variants should use matched:

- model size and parameter budget, allowing only clearly reported positional-mechanism parameters;
- tokenizer or synthetic vocabulary;
- optimizer, scheduler, batch size, and gradient clipping;
- training token count;
- context-length curriculum;
- random seeds;
- hyperparameter budget.

The minimum seed count is five. Failed, diverged, or underperforming runs should be retained in the artifact tree and included in summaries.

## Tasks

The benchmark set should include both synthetic and less target-engineered tasks:

| Task class | Examples | Reason |
| --- | --- | --- |
| Standard retrieval | Needle-in-Haystack, passkey retrieval, multi-needle retrieval | Tests location-sensitive recall without defining the answer by the PhaseWrap score. |
| RULER-style tasks | multi-hop retrieval, aggregation, variable tracking | Tests compositional long-context behavior. |
| Small language-modeling or QA task | compact natural-language QA or controlled text corpus | Checks whether the positional mechanism survives a non-synthetic setting. |
| Synthetic diagnostics | phase-cued retrieval and adversarial alias tests | Keeps interpretability, but cannot be the sole success criterion. |

Train-short/test-long splits are required. At minimum, train at one shorter context length and evaluate at longer context lengths that were not used for training.

## Metrics

Report at least:

- validation loss or perplexity;
- retrieval top-1 accuracy;
- mean reciprocal rank;
- target probability or calibration-sensitive score;
- expected calibration error or a comparable calibration statistic if available;
- confidence intervals over seeds.

Do not choose the winning method from a single metric without reporting tradeoffs across the other metrics.

## Artifact Requirements

Stage 9 should publish:

- manifest with model variants, training settings, seeds, tasks, and commit hash;
- per-run configuration files;
- per-run metrics;
- failed-run logs;
- aggregate summary with confidence intervals;
- verifier or summarizer script that rebuilds the public tables from saved metrics.

## Promotion Gate

Stage 9 can promote PhaseWrap-RoPE from "worth testing in broader RoPE-facing settings" to "competitive in the tested small trained-transformer setting" only if PhaseWrap variants are competitive against RoPE, ALiBI, sinusoidal, and no-position baselines under matched training controls across multiple seeds and at least one task whose target is not constructed from the PhaseWrap formula.
