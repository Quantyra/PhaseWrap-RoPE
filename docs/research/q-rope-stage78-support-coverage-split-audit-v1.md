# PhaseWrap-RoPE Stage 78 Support Coverage Split Audit v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 78 tests whether the Stage 76/77 same-seed integrated support/copy failures are explained by the default phase-cued support split itself.

The audit compares held-out phase-cued test coverage under four support sources:

- `same_seed_train`
- `same_seed_train_validation`
- `cross_seed_train`
- `pooled_train`

For each seed, it measures whether the visible query-support key and its target support class are available before any learned copy-head is asked to recover them.

This is a split-coverage audit, not a transformer benchmark.

## Reviewer Command

```bash
python scripts/run_stage78_support_coverage_split_audit.py
```

This writes:

- `logs/automated_stage_gates/stage78_support_coverage_split_audit/manifest.json`
- `logs/automated_stage_gates/stage78_support_coverage_split_audit/results.json`
- `logs/automated_stage_gates/stage78_support_coverage_split_audit/summary.csv`
- `logs/automated_stage_gates/stage78_support_coverage_split_audit/per_run_results.csv`
- `logs/automated_stage_gates/stage78_support_coverage_split_audit/failed_runs.json`

## Result

Stage 78 records `SAME_SEED_SUPPORT_COVERAGE_SPLIT_EXPLAINS_STAGE77_FAILURE`.

| Support source | Seeds | Known query-mod fraction | Support-class fraction | Exact query-support fraction |
| --- | ---: | ---: | ---: | ---: |
| `cross_seed_train` | 5 | 1.000000 | 1.000000 | 1.000000 |
| `pooled_train` | 5 | 1.000000 | 1.000000 | 1.000000 |
| `same_seed_train_validation` | 5 | 0.250000 | 0.250000 | 0.250000 |
| `same_seed_train` | 5 | 0.000000 | 0.000000 | 0.000000 |

No runs failed.

## Interpretation

Stage 78 explains the Stage 77 support failure as a split-coverage failure under the default same-seed setup. The same-seed train rows provide zero held-out phase-cued query-support coverage, so the Stage 76/77 same-seed support head is asked to predict support classes that are absent from its available training support.

This also explains why Stage 74 and Stage 75 could recover phase-cued retrieval from cross-seed rows while Stage 76 and Stage 77 could not preserve that recovery under same-seed integrated training. Cross-seed and pooled train support sources have full held-out support coverage, but the same-seed train source has none.

The result does not promote PhaseWrap-RoPE. It narrows the failure mode: the next useful decoder experiment must either use a support-complete same-seed exposure design or deliberately test extrapolation to unseen support classes with a model capable of representing that extrapolation.

## Claim Boundary

Supported:

- evidence that Stage 76/77 same-seed phase-cued failure is explained by default split coverage;
- evidence that cross-seed and pooled support sources fully cover held-out phase-cued query-support rows;
- evidence that same-seed train+validation still covers only one quarter of held-out support rows.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- broad quantum advantage;
- a claim that PhaseWrap-RoPE replaces RoPE;
- a claim that support coverage alone validates a matched decoder-only transformer;
- a claim that cross-seed support availability is positional-method promotion evidence.

## Next Gate

The next gate should redesign the learned decoder path so the support exposure contract is explicit: either train under same-seed support-complete coverage before evaluating positional-method differences, or test unseen-support extrapolation as its own harder task rather than treating zero-coverage failure as an optimizer result.
