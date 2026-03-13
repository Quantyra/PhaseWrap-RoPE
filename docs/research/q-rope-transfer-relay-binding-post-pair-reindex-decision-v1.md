# Relay-Binding Post-Pair-Reindex Decision v1

Decision: continue

Reason:
- Under `pair_reindex=1`, the relay-binding witness remained ahead of the bounded symbolic control on both `mae` and `rank_correlation`.
- The packet was structurally non-inert, so this counts as real hardening evidence.

Next bounded step:
- `slot_swap=1`
- keep only the relay witness and bounded symbolic control
- stop immediately if the control matches or beats the witness on both `mae` and `rank_correlation`
