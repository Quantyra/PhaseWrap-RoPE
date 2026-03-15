# Q-RoPE Successor Dual-Anchor Offset-Consensus Deeper Pair-Reindex Hardening Plan v1

## BLUF
- The branch stayed intact under `slot_swap=1`.
- The next and final retained hardening step is `pair_reindex=7` only.
- This is the closure packet for the bounded hardening cycle.

## Fixed Hardening Packet
- dataset: `synthetic_positional_dual_anchor_offset_consensus_response`
- witness: `V_future_relational_witness_positional_dual_anchor_offset_consensus`
- control: `V_control_symbolic_positional_dual_anchor_offset_consensus_regressor`
- backend: `sim_quantum_statevector`
- pair reindex: `7`
- seeds: `42`, `123`, `777`

## Stop Rule
- Stop immediately if the bounded symbolic control matches or beats the witness on both mean `mae` and mean `rank_correlation`.
