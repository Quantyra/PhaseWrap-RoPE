# PhaseWrap-RoPE Stage 7 Toy Transformer Ablation v1

Date: `2026-05-20`

## Purpose

This stage adds a small no-credential downstream ablation requested during external review: swap the PhaseWrap positional score into a four-layer attention-only toy transformer and compare it with RoPE, ALiBI, sinusoidal, and no-position variants on a synthetic length-extrapolation retrieval task.

The task is intentionally small and synthetic. It is useful for reviewer intuition about downstream behavior, but it is not evidence of production transformer superiority or full transformer-scale validation.

## Artifact Paths

- Manifest: `logs/automated_stage_gates/stage7_toy_transformer_ablation/manifest.json`
- Results: `logs/automated_stage_gates/stage7_toy_transformer_ablation/results.json`
- Summary CSV: `logs/automated_stage_gates/stage7_toy_transformer_ablation/summary.csv`
- Runner: `scripts/run_stage7_toy_transformer_ablation.py`
- Implementation: `src/qrope/stage7_toy_transformer_ablation.py`
- Tests: `tests/test_stage7_toy_transformer_ablation.py`

## Task

Each example contains a deterministic token sequence and a final query position. The model must select the farthest prior token with the requested mod-8/mod-12 phase relation. Training examples use lengths `16` and `24`; validation uses length `32`; the reported test set uses lengths `48` and `64`.

The toy stack has four attention-only layers. The only changed component across variants is the positional term added to the attention logits.

## Result

| Method | Layers | Scale | Rows | Test lengths | Target prob MAE | Mean target prob | Top-1 | MRR |
| --- | ---: | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| `phasewrap_rope_4layer` | 4 | 0.5 | 40 | 48-64 | 0.962992 | 0.037008 | 1.000000 | 1.000000 |
| `rope_4layer` | 4 | 4.0 | 40 | 48-64 | 0.895771 | 0.104229 | 0.400000 | 0.700000 |
| `alibi_4layer` | 4 | 1.0 | 40 | 48-64 | 0.971458 | 0.028542 | 0.050000 | 0.212083 |
| `sinusoidal_4layer` | 4 | 4.0 | 40 | 48-64 | 0.945480 | 0.054520 | 0.050000 | 0.304167 |
| `no_position_4layer` | 4 | 0.0 | 40 | 48-64 | 0.961044 | 0.038956 | 0.300000 | 0.600000 |

The PhaseWrap variant has the best top-1 and MRR on this fixed packet. Its absolute target probability remains low because the toy stack spreads probability mass across many phase-compatible distractors. This result should therefore be read as a ranking/selection ablation, not as a calibrated probability result.

## Claim Boundary

Supported:

- a deterministic synthetic length-extrapolation ablation for a four-layer toy attention stack;
- evidence that the PhaseWrap positional term can improve target ranking on this fixed toy packet;
- a no-hardware, no-provider-credential reproducibility path.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- general cross-backend robustness.

## Open Questions

The result motivates harder downstream tasks with additional seeds and less phase-aligned construction. It does not replace independent model-scale evaluation.
