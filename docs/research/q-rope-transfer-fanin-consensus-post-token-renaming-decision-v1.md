# Q-RoPE Transfer Fan-In Consensus Post-Token-Renaming Decision v1

Decision: stop

Reason:
- Under `token_permutation=cdab`, the bounded symbolic control beat the witness on both:
  - `mae`
  - `rank_correlation`
- The nuisance perturbation was non-inert, so this is a real failure boundary rather than an artifact of an unchanged packet.

Next state:
- Archive `fanin-consensus` as a negative transfer boundary.
- Do not continue this line into structural hardening.
