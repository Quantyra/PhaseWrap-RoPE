# PhaseWrap-RoPE Stage 9 Trained Transformer Ablation Plan v1

Date: `2026-05-20`

Status: `first_executable_subset_complete`

## Purpose

Stage 9 is the next evidence milestone for the RoPE-replacement research lane. Its goal is to test PhaseWrap-RoPE inside trained small decoder-only transformers where the only intended experimental variable is the positional mechanism.

Stage 9 is not a hardware experiment. It should run without quantum-provider credentials.

The current repository includes the first executable subset:

```bash
python scripts/run_stage9_trained_transformer_ablation.py
```

This subset trains decoder-style positional attention mechanisms under matched seeds, data budget, optimizer, and epochs. It now includes one phase-cued lane and one exact-offset passkey lane whose answer is not selected by the PhaseWrap score. It is useful evidence for the RoPE-facing research lane, but it is still narrower than the full trained small decoder-only transformer benchmark described below.

## Claim Boundary

Stage 9 may support a narrow statement that a PhaseWrap positional mechanism is competitive on the tested small trained-transformer tasks if the results support that conclusion.

The current executable subset supports only narrower statements: on the synthetic phase-cued train-short/test-long retrieval packet, the learned `phasewrap_adapter` mechanism has the best mean MRR and top-1 accuracy among the tested positional attention variants; on the exact-offset passkey packet, `rope_relative` is strongest.

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

The current executable subset includes `phasewrap_bias` and `phasewrap_adapter`. The adapter is trained over PhaseWrap-derived positional features; it is not given the target position or target label.

## Current Executable Result

Artifacts:

- `logs/automated_stage_gates/stage9_trained_transformer_ablation/manifest.json`
- `logs/automated_stage_gates/stage9_trained_transformer_ablation/results.json`
- `logs/automated_stage_gates/stage9_trained_transformer_ablation/summary.csv`
- `logs/automated_stage_gates/stage9_trained_transformer_ablation/per_seed_results.csv`
- `logs/automated_stage_gates/stage9_trained_transformer_ablation/failed_runs.json`

Current phase-cued summary:

| Method | Mean test top-1 | Mean test MRR | Mean test loss | Failed runs |
| --- | ---: | ---: | ---: | ---: |
| `phasewrap_adapter` | `0.668750` | `0.745096` | `2.110092` | `0` |
| `sinusoidal` | `0.281250` | `0.331624` | `3.798228` | `0` |
| `alibi` | `0.000000` | `0.086369` | `5.221903` | `0` |
| `no_position` | `0.000000` | `0.086369` | `5.888817` | `0` |
| `rope_relative` | `0.006250` | `0.044751` | `5.760238` | `0` |
| `phasewrap_bias` | `0.000000` | `0.006330` | `5.618299` | `0` |

Current exact-offset passkey summary:

| Method | Mean test top-1 | Mean test MRR | Mean test loss | Failed runs |
| --- | ---: | ---: | ---: | ---: |
| `rope_relative` | `1.000000` | `1.000000` | `0.097265` | `0` |
| `phasewrap_adapter` | `1.000000` | `1.000000` | `1.418350` | `0` |
| `sinusoidal` | `0.081250` | `0.266650` | `2.446665` | `0` |
| `no_position` | `0.000000` | `0.013187` | `5.888817` | `0` |
| `alibi` | `0.000000` | `0.013187` | `5.907809` | `0` |
| `phasewrap_bias` | `0.000000` | `0.006132` | `5.621320` | `0` |

The result is intentionally reported as a trained positional-attention ablation, not as a full language-model result. The passkey lane is especially important because it shows a task where the RoPE-relative baseline is better calibrated and lower-loss than the PhaseWrap adapter.

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

The current executable subset satisfies these artifact requirements for its synthetic positional-attention tasks. The remaining gap is the broader task/model scope: full small decoder-only transformer runs, non-synthetic retrieval or QA tasks, and richer calibration reporting.

The current next-benchmark promotion gate is maintained in `docs/research/q-rope-next-transformer-benchmark-roadmap-v1.md`. That roadmap supersedes this Stage 9 note for future task scope while preserving the Stage 9 executable subset as historical evidence.

## Stage 10 Small Decoder-Only Transformer Ablation

The repository now includes an autograd-backed first full-transformer sanity check for the small decoder-only transformer milestone:

```bash
python scripts/run_stage10_small_decoder_transformer.py
```

Current artifact paths:

- `logs/automated_stage_gates/stage10_small_decoder_transformer/manifest.json`
- `logs/automated_stage_gates/stage10_small_decoder_transformer/results.json`
- `logs/automated_stage_gates/stage10_small_decoder_transformer/summary.csv`
- `logs/automated_stage_gates/stage10_small_decoder_transformer/per_seed_results.csv`
- `logs/automated_stage_gates/stage10_small_decoder_transformer/failed_runs.json`

The current Stage 10 result is near chance across the tested phase-cued retrieval, exact-offset passkey, and tiny text-fact QA lanes. It should be cited as a completed first small-transformer sanity check with negative or inconclusive evidence, not as a PhaseWrap advantage.

## Promotion Gate

Stage 9 can promote PhaseWrap-RoPE from "worth testing in broader RoPE-facing settings" to "competitive in the tested small trained-transformer setting" only if PhaseWrap variants are competitive against RoPE, ALiBI, sinusoidal, and no-position baselines under matched training controls across multiple seeds and at least one task whose target is not constructed from the PhaseWrap formula.
