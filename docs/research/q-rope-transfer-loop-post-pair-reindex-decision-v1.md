# Q-RoPE Transfer Loop-Closure Post-Pair-Reindex Decision v1

Date: 2026-03-11
Stories: S893

## Decision
- keep the transfer-loop branch active
- do not widen the task or symbolic family
- move to one bounded structural hardening step

## Why
- the bounded symbolic control did not match or beat the witness on both declared packet metrics
- the witness still led on:
  - `mae`
  - `rank_correlation`
- the lead held after the first non-nuisance structural perturbation

## Next Step
- fixed structural hardening:
  - `slot_swap = 1`
- keep:
  - same task
  - same witness
  - same bounded symbolic control
  - same seeds
