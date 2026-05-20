# PhaseWrap-RoPE Stage 6 Downstream Attention v1

Date: `2026-05-20`

## Summary

Stage 6 adds a deterministic toy downstream attention benchmark. The task mixes token/content compatibility with phase-wrap positional signal so the target is not exactly recoverable from `(reference_delta - candidate_delta) mod 24` or direct `m8`/`m12`/`m8*m12` features alone.

This is still a toy synthetic benchmark. It does not establish production transformer superiority, full transformer-scale validation, or quantum advantage.

## Reproduce

```bash
python scripts/run_stage6_downstream_attention.py
```

The command writes:

- `logs/automated_stage_gates/stage6_downstream_attention/manifest.json`
- `logs/automated_stage_gates/stage6_downstream_attention/results.json`
- `logs/automated_stage_gates/stage6_downstream_attention/summary.csv`

## Task Definition

Each candidate row receives a downstream target:

```text
target = 0.10 + 0.50*content_score + 0.30*phase_label + 0.10*content_score*phase_label
```

`content_score` is a deterministic query-token/candidate-token compatibility score. `phase_label` is the existing phase-wrap attention label. The mixed target forces the benchmark to use content and position together, rather than allowing a delta-only lookup to recover the target exactly.

Leakage diagnostics over all splits:

| Diagnostic | Value |
| --- | ---: |
| `mod24_self_mae` | 0.011239 |
| `phase_feature_self_mae` | 0.029704 |
| `mod24_not_exact_pass` | `true` |
| `phase_features_not_exact_pass` | `true` |
| `token_pair_variation_present` | `true` |

## Results

| Method | Rows | Contexts | MAE | Rank corr | Top-1 | MRR | NDCG@4 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `phasewrap_rope_attention` | 152 | 38 | 0.000548 | 0.989696 | 1.000000 | 1.000000 | 1.000000 |
| `rope_attention` | 152 | 38 | 0.020949 | 0.857837 | 1.000000 | 1.000000 | 0.998627 |
| `alibi_attention` | 152 | 38 | 0.019757 | 0.855112 | 1.000000 | 1.000000 | 0.998627 |
| `sinusoidal_attention` | 152 | 38 | 0.371411 | 0.307640 | 0.394737 | 0.596491 | 0.948477 |
| `no_position_attention` | 152 | 38 | 0.019740 | 0.861826 | 1.000000 | 1.000000 | 0.998627 |
| `lookup_mod24_baseline` | 152 | 38 | 0.010998 | 0.968807 | 0.973684 | 0.986842 | 0.997057 |
| `classical_m8_m12_product_baseline` | 152 | 38 | 0.031147 | 0.900955 | 0.947368 | 0.973684 | 0.995152 |

## Interpretation

The PhaseWrap-RoPE attention variant has the lowest MAE on this toy downstream task. The mod-24 and direct phase-feature baselines no longer recover the target exactly, which addresses the Stage 5 limitation.

The result is evidence for a bounded toy downstream setting only. The no-position, RoPE, and ALiBI variants still rank the best candidate perfectly in this packet, so the strongest Stage 6 distinction is score calibration/MAE, not top-1 selection. Future work should increase the task difficulty and test additional seeds before making broader claims.

## Claim Boundary

Supported:

- reproducible toy downstream comparison across PhaseWrap-RoPE, RoPE, ALiBI, sinusoidal, no-position, and classical lookup/feature baselines;
- evidence that the Stage 6 target is not exactly recovered by mod-24 or direct phase features alone;
- bounded evidence that PhaseWrap-RoPE gives the best score calibration on this fixed packet.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- claims that this single synthetic packet generalizes to production language tasks.
