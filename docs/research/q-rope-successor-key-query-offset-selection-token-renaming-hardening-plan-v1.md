# Q-RoPE Successor Key-Query Offset Selection Token-Renaming Hardening Plan v1

## BLUF
- The next retained-model nuisance-hardening step is fixed.
- Keep only the witness and the bounded symbolic control.
- Stop the line immediately if the control matches or beats the witness on both mean `mae` and mean `rank_correlation`.

## Fixed Hardening Packet
- dataset: `synthetic_positional_key_query_offset_selection_response`
- perturbation: `token_permutation=cdab`
- witness: `V_future_relational_witness_positional_key_query_offset_selection`
- control: `V_control_symbolic_positional_key_query_offset_selection_regressor`
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
