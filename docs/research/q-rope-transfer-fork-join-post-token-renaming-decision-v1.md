# Q-RoPE Transfer Fork-Join Post-Token-Renaming Decision v1

Date: 2026-03-12
Stories: S920

## Decision
- keep the transfer fork-join branch active
- do not widen the task or symbolic family
- move to one bounded structural hardening step

## Why
- the bounded symbolic control did not match or beat the witness on both declared packet metrics
- the witness still led in the mean on:
  - `mae`
  - `rank_correlation`
- one seed favored the control on both metrics, so the branch should move to structural hardening next instead of claiming stability too early

## Next Step
- fixed structural hardening:
  - `pair_reindex = 1`
- keep:
  - same task
  - same witness
  - same bounded symbolic control
  - same seeds

## Disallowed
- no hardware execution
- no provider work
- no second fork-join control family
- no symbolic basis growth
