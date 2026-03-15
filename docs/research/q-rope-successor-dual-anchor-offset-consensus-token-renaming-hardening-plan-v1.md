# Q-RoPE Successor Dual-Anchor Offset-Consensus Token-Renaming Hardening Plan v1

## BLUF
- The first packet survived.
- The next retained hardening step is `token_permutation=cdab` only.
- No wider perturbation expansion is active.

## Fixed Hardening Packet
- dataset: `synthetic_positional_dual_anchor_offset_consensus_response`
- witness: `V_future_relational_witness_positional_dual_anchor_offset_consensus`
- control: `V_control_symbolic_positional_dual_anchor_offset_consensus_regressor`
- backend: `sim_quantum_statevector`
- token permutation: `cdab`
- seeds: `42`, `123`, `777`

## Stop Rule
- Stop immediately if the bounded symbolic control matches or beats the witness on both mean `mae` and mean `rank_correlation`.
