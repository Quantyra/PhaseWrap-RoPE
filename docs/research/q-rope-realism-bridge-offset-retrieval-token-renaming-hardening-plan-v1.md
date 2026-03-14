# Q-RoPE Realism-Bridge Offset-Retrieval Token-Renaming Hardening Plan v1

## Next Packet
- perturbation: `token_permutation=cdab`
- retained models only:
  - `V_future_relational_witness_positional_offset_retrieval`
  - `V_control_symbolic_positional_offset_retrieval_regressor`

## Stop Rule
- Stop the line immediately if the bounded symbolic control matches or beats the witness on both mean `mae` and mean `rank_correlation`.
