# Q-RoPE Transfer Loop-Closure Post-Packet Decision v1

Date: 2026-03-11
Stories: S887

## Decision
- keep the transfer-loop branch active
- do not widen the task or symbolic family
- move to one bounded nuisance hardening step

## Why
- the bounded symbolic control did not match or beat the witness on either declared packet metric
- the witness led on both:
  - `mae`
  - `rank_correlation`
- the mean lead held with positive rank structure on all three seeds

## Next Step
- fixed nuisance hardening:
  - `token_permutation = cdab`
- keep:
  - same task
  - same witness
  - same bounded symbolic control
  - same seeds

## Disallowed
- no hardware execution
- no provider work
- no second transfer family
- no symbolic basis growth
