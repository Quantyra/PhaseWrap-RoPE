# PhaseWrap-RoPE Stage 5 Attention Baselines v1

Date: `2026-05-20`

## Summary

Stage 5 adds a deterministic, no-provider-credential attention-scoring benchmark over the existing `synthetic_transformer_phase_wrap_attention_selection` bundle. It compares the phase-wrap scoring rule against classical lookup, classical feature, shallow tree, RoPE-style, sinusoidal, and ALiBI-style scoring baselines on the same held-out candidate-ranking task.

This is not a transformer-scale experiment. It does not claim production transformer superiority, quantum advantage, or full downstream language-model validation.

## Reproduce

```bash
python scripts/run_stage5_attention_baselines.py
```

The command writes:

- `logs/automated_stage_gates/stage5_attention_baselines/manifest.json`
- `logs/automated_stage_gates/stage5_attention_baselines/results.json`
- `logs/automated_stage_gates/stage5_attention_baselines/summary.csv`

## Results

| Method | Rows | Contexts | MAE | Rank corr | Top-1 | MRR | NDCG@4 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `phase_wrap_formula` | 152 | 38 | 0.000000 | 1.000000 | 1.000000 | 1.000000 | 1.000000 |
| `lookup_mod24` | 152 | 38 | 0.000000 | 0.999652 | 1.000000 | 1.000000 | 1.000000 |
| `classical_m8_m12_product` | 152 | 38 | 0.000000 | 0.996015 | 1.000000 | 1.000000 | 1.000000 |
| `delta_regression_tree` | 152 | 38 | 0.018332 | 0.880971 | 0.868421 | 0.929825 | 0.997502 |
| `rope_attention` | 152 | 38 | 0.225643 | 0.119377 | 0.105263 | 0.429825 | 0.887883 |
| `sinusoidal_attention` | 152 | 38 | 0.230163 | -0.329817 | 0.026316 | 0.317982 | 0.855829 |
| `alibi_attention` | 152 | 38 | 0.241150 | 0.105991 | 0.289474 | 0.550439 | 0.915013 |

## Interpretation

The exact recovery by `lookup_mod24` and `classical_m8_m12_product` is expected for this synthetic task. The label is generated from wrapped mod-8/mod-12 residual structure, and the least-common-period lookup on `(reference_delta - candidate_delta) mod 24` exposes enough information to recover the same target.

This result is still useful because it closes the requested baseline gap: simple classical baselines are now present, machine-readable, and reviewer-verifiable. It also narrows the next scientific question. A future downstream task must avoid being reducible to the same exposed mod-24 or direct product features if it is intended to test broader attention-model value.

## Claim Boundary

Supported:

- deterministic comparison of the current phase-wrap scoring target against explicit classical and positional attention-scoring baselines;
- evidence that simple exposed-feature baselines can recover the current synthetic Stage 5 label;
- a clear next-step requirement for a less tautological downstream benchmark.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- claims that Stage 5 proves language-model quality improvement.
