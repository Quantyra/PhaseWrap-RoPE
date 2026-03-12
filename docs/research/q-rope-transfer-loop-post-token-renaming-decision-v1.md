# Q-RoPE Transfer Loop-Closure Post-Token-Renaming Decision v1

Date: 2026-03-11
Stories: S890

## Decision
- keep the transfer-loop branch active
- do not widen the task or symbolic family
- move to one bounded structural hardening step

## Why
- the bounded symbolic control did not match or beat the witness on both declared packet metrics
- the witness still led the fixed control on:
  - `mae`
  - `rank_correlation`
- however, the lead narrowed materially under token renaming, so the next correct step is structural rather than another nuisance-only check

## Next Step
- fixed structural hardening:
  - `pair_reindex = 1`
- keep:
  - same task
  - same witness
  - same bounded symbolic control
  - same seeds
