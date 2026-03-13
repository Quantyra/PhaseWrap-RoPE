# Q-RoPE Transfer Fan-In Consensus Post-Packet Decision v1

## Decision
- `CONTINUE`

## Reason
- The witness beat the bounded symbolic control on both declared packet metrics:
  - `mae`
  - `rank_correlation`
- The packet remains fragile because both means for `rank_correlation` are negative.
- That is enough to justify one bounded nuisance hardening step, but not enough to justify any broader branch expansion.

## Next Step
- Run fixed token-renaming hardening with `token_permutation=cdab`.
- Keep only the witness and bounded symbolic control.
- Stop the line immediately if the control matches or beats the witness on both declared packet metrics.
