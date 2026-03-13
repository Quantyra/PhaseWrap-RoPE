# Relay-Binding Post-Slot-Swap Decision v1

Decision: continue

Reason:
- Under `slot_swap=1`, the relay-binding witness remained ahead of the bounded symbolic control on both `mae` and `rank_correlation`.
- The perturbation changed the packet materially, so this counts as real structural hardening.

Next bounded step:
- `pair_reindex=7`
- keep only the relay witness and bounded symbolic control
- stop immediately if the control matches or beats the witness on both `mae` and `rank_correlation`
