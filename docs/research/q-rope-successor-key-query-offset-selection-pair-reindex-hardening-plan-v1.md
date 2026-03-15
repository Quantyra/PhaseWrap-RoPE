# Q-RoPE Successor Key-Query Offset Selection Pair-Reindex Hardening Plan v1

## BLUF
- The next retained structural hardening step is fixed.
- Keep only the witness and the bounded symbolic control.
- Stop the line immediately if the control matches or beats the witness on both mean `mae` and mean `rank_correlation`.

## Fixed Hardening Packet
- dataset: `synthetic_positional_key_query_offset_selection_response`
- perturbation: `pair_reindex=1`
- witness: `V_future_relational_witness_positional_key_query_offset_selection`
- control: `V_control_symbolic_positional_key_query_offset_selection_regressor`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
