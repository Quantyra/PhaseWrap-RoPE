# Q-RoPE Transfer Loop-Closure Post-Slot-Swap Decision v1

Date: 2026-03-11
Stories: S896

## Decision
- keep the transfer-loop branch active
- do not widen the task or symbolic family
- move to one deeper structural hardening step

## Why
- the bounded symbolic control did not match or beat the witness on both declared packet metrics
- the witness still led the fixed control on:
  - `mae`
  - `rank_correlation`
  in the packet mean
- the slot-swap packet was structurally real, so the branch now has one nuisance and two structural hardening packets behind it

## Next Step
- fixed deeper structural hardening:
  - `pair_reindex = 7`
- keep:
  - same task
  - same witness
  - same bounded symbolic control
  - same seeds
