# Q-RoPE E002 Variable-Cardinality Pair-Reindex Hardening Plan v1

Date: 2026-03-14
Stories: S1338-S1340

## BLUF
- `token_permutation=cdab` was non-inert and the witness still led on both gate metrics.
- The next packet is the fixed structural hardening step `pair_reindex=1` only.
- No wider `E002` expansion is active.

## Fixed Hardening Packet
- dataset: `synthetic_positional_variable_cardinality_offset_selection_response`
- witness: `V_future_relational_witness_positional_variable_cardinality_offset_selection`
- control: `V_control_symbolic_positional_variable_cardinality_offset_selection_regressor`
- backend: `sim_quantum_statevector`
- pair reindex: `1`
- seeds: `42`, `123`, `777`

## Stop Rule
- Stop immediately if the bounded symbolic control matches or beats the witness on both mean `mae` and mean `rank_correlation`.
