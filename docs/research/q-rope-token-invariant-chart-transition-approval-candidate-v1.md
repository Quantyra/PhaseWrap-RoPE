# Token-invariant chart-transition approval-candidate memo

## Status
- approval-candidate
- not implementation-approved

## Why it is stronger than the failed branch
- it addresses the exact robustness failure that stopped the prior chart-transition task
- it removes token identity from the target by construction rather than trying to harden after the fact
- it preserves the strongest surviving mechanism idea from the chart-transition line: ordered transition geometry

## Remaining gate
- implementation approval should depend on explicit latent-state invariance diagnostics, not just a prose claim
