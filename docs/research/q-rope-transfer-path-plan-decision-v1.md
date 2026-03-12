# Q-RoPE Transfer Path Plan Decision v1

Date: 2026-03-11
Stories: S855

## Decision
- the transfer-path line is specific enough for one bounded implementation cycle
- implementation is now the next valid move

## Why
- task is explicit
- symbolic family is frozen
- hard-stop diagnostics are explicit
- writable scope is narrow
- hardware remains out of scope

## Next Valid Move
- implement the transfer-path generator and control family inside the frozen scope
- run exactly one fixed three-seed packet
- decide the branch from `mae` and `rank_correlation`
