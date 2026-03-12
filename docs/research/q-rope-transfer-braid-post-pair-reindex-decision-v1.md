# Q-RoPE Transfer Braid Post-Pair-Reindex Decision v1

Date: 2026-03-12
Stories: S948

## Decision
- keep the braid transfer branch active
- do not widen the task or symbolic family
- move to the next bounded structural hardening step

## Why
- the bounded symbolic control did not match or beat the witness on either declared packet metric
- the witness led on both:
  - `mae`
  - `rank_correlation`

## Next Step
- fixed structural hardening:
  - `slot_swap = 1`
- keep:
  - same task
  - same witness
  - same bounded symbolic control
  - same seeds
