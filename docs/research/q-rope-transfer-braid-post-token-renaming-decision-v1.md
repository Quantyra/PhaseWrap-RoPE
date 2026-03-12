# Q-RoPE Transfer Braid Post-Token-Renaming Decision v1

Date: 2026-03-12
Stories: S945

## Decision
- keep the braid transfer branch active
- do not widen the task or symbolic family
- move to one bounded structural hardening step

## Why
- the bounded symbolic control did not match or beat the witness on both declared packet metrics
- the witness remained ahead on:
  - `mae`
  - `rank_correlation`
- the narrowed margin is enough to justify structural hardening next

## Next Step
- fixed structural hardening:
  - `pair_reindex = 1`
- keep:
  - same task
  - same witness
  - same bounded symbolic control
  - same seeds
