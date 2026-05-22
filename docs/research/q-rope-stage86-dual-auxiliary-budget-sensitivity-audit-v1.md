# PhaseWrap-RoPE Stage 86 Dual-Auxiliary Budget Sensitivity Audit v1

Date: `2026-05-21`

Status: `completed`

## Purpose

Stage 86 tests whether the Stage 85 negative result is mainly a short-budget artifact. It reruns the dual support/target-attention auxiliary pointer-generator path at practical `10` and `20` epoch budgets under the same fair RoPE, ALiBI, sinusoidal, no-position, and PhaseWrap comparison frame.

This is not a claim-expansion benchmark. It is a sensitivity check for the current support-to-token blocker.

## Reviewer Command

```bash
python scripts/run_stage86_dual_auxiliary_budget_sensitivity_audit.py
```

This writes:

- `logs/automated_stage_gates/stage86_dual_auxiliary_budget_sensitivity_audit/manifest.json`
- `logs/automated_stage_gates/stage86_dual_auxiliary_budget_sensitivity_audit/results.json`
- `logs/automated_stage_gates/stage86_dual_auxiliary_budget_sensitivity_audit/summary.csv`

## Result

Stage 86 records `DUAL_AUXILIARY_BUDGET_WITHOUT_RETRIEVAL_GENERALIZATION`.

Default run summary:

| epochs | task | best method | best top-1 | best target probability |
| ---: | --- | --- | ---: | ---: |
| `10` | `phase_cued_retrieval` | `sinusoidal` | `0.050000` | `0.029205` |
| `10` | `exact_offset_passkey` | `sinusoidal` | `0.416667` | `0.058441` |
| `20` | `phase_cued_retrieval` | `phasewrap_bias` | `0.050000` | `0.023295` |
| `20` | `exact_offset_passkey` | `sinusoidal` | `0.100000` | `0.046235` |

Additional decision fields:

- `generalization_top1_threshold`: `0.5`
- `generalized_original_retrieval_tasks`: `[]`
- `phasewrap_retrieval_generalized_tasks`: `[]`
- `failed_run_count`: `0`

## Interpretation

The Stage 85 negative result is not explained by a short practical training budget. Increasing the dual-auxiliary budget from `10` to `20` epochs does not repair held-out retrieval. Phase-cued retrieval remains at top-1 `0.050000`, and exact-offset passkey drops from top-1 `0.416667` to `0.100000`.

The current blocker remains learned held-out support-to-token routing, not merely missing training epochs in the dual-auxiliary pointer-generator path.

## Claim Boundary

Supported:

- a no-credential budget-sensitivity audit for the Stage 85 dual-auxiliary pointer-generator path;
- evidence about whether Stage 85's below-threshold exact-offset result is explained by a short training budget;
- fair RoPE/ALiBI/sinusoidal/no-position/PhaseWrap comparisons with failed-run retention.

Excluded:

- production transformer superiority;
- full transformer-scale validation;
- a claim that PhaseWrap-RoPE replaces RoPE;
- a claim that budget tuning alone establishes positional-method promotion;
- a claim that auxiliary-supervised diagnostics are standard free decoder-only language modeling;
- broad quantum advantage.

## Next Gate

The next useful gate should change the decoder mechanism itself rather than add another auxiliary loss or modest training-budget increase. The claim boundary should remain bounded until a matched decoder learns held-out support-to-token routing without evaluation-time metadata.
