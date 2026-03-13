# Relay-Binding Post-Token-Renaming Decision v1

Decision: continue

Reason:
- Under `token_permutation=cdab`, the relay-binding witness remained ahead of the bounded symbolic control on both `mae` and `rank_correlation`.
- The perturbation changed the packet materially, so this counts as real nuisance hardening.

Next bounded step:
- `pair_reindex=1`
- keep only the relay witness and bounded symbolic control
- stop immediately if the control matches or beats the witness on both `mae` and `rank_correlation`
