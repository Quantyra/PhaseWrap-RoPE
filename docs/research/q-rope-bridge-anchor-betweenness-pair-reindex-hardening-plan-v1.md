# Q-RoPE Bridge Anchor-Betweenness Pair-Reindex Hardening Plan v1

## Next Valid Move
- Run the fixed `pair_reindex=1` hardening packet.
- Keep only:
  - `V_future_relational_witness_positional_anchor_betweenness`
  - `V_control_symbolic_positional_anchor_betweenness_regressor`
- Stop the line immediately if the bounded symbolic control matches or beats the witness on both mean `mae` and mean `rank_correlation`.
