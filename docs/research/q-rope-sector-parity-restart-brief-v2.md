# Q-RoPE Sector-Parity Restart Brief v2

## Status
- `memo-only`
- `not approved`

## Candidate
- `V_future_sector_contrast_pairstate`

## Mechanism family
- `sector-contrast pair-state`

## Task
- `synthetic_sector_parity_binary`

### Label rule
- label `1`:
  - `P_small`
  - `N_large`
- label `0`:
  - `N_small`
  - `P_large`

This preserves relational sector structure while removing the direct sign-to-label shortcut that limited the archived pair-state branch.

## Required mechanism shape
The future candidate must:
- prepare explicit pair-state relational structure
- preserve sector resolution before aggregation
- compute task-relevant sector contrast rather than pooled scalar score only

## Required diagnostics
- per-sector responses
- task-relevant sector contrast
- anti-collapse proof that sector responses are not pooled before the decision statistic
- multi-seed summary over `42/123/777`

## Fixed packet
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- baseline: `V0`
- candidate: `V_future_sector_contrast_pairstate`
- scope: local-only, synthetic-only, zero-credit

## Success criteria
Approve only if the future candidate shows all of:
- better mean accuracy than `V0`
- better mean F1 than `V0`
- positive task-relevant sector separation on all three seeds
- no pooled-score-only explanation
- no reduction to sign recovery

## Failure criteria
Stop immediately if:
- gains appear in only one seed
- sector resolution is bypassed
- pooled-score drift explains the effect
- the mechanism can be reduced to a simpler shortcut than sector-parity relation

## Guardrails
- no remote execution
- no benchmark expansion
- no additional candidate branches
- no implementation without explicit approval

## Bottom line
The archive now contains a restart brief that is specific on:
- task
- family
- packet
- diagnostics
- pass/fail gates

It is ready for a refreshed approval gate, not for implementation.
