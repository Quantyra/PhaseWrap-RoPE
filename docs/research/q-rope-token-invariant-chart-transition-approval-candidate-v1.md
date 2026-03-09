# Token-invariant chart-transition approval-candidate memo

## Status
- approval-candidate
- not implementation-approved

## Why it is stronger than the failed branch
- it addresses the exact robustness failure that stopped the prior chart-transition task
- it removes token identity from the target by construction rather than trying to harden after the fact
- it preserves the strongest surviving mechanism idea from the chart-transition line: ordered transition geometry

## Hardened remaining gate
Implementation approval is blocked until the task specification, scaffold, and eventual generator contract all require the following latent-state diagnostics on paired token-permuted renders of the same latent states:
- `latent_target_invariance_pass = true`
- `latent_target_max_abs_delta = 0`
- `token_view_balance_pass = true`

## Consequence
- still memo-only
- still no implementation
- next valid move is an implementation-approval gate memo that references this invariance contract directly
