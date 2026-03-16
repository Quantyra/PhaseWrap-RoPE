# Q-RoPE E006 Multi-Hop Reference Pair-Reindex Hardening Plan v1

Date: 2026-03-16
Stories: S1458-S1460

## BLUF
- `token_permutation=cdab` was non-inert and the witness still led on mean `mae` while mean `rank_correlation` tied.
- The next packet is the fixed structural hardening step `pair_reindex=1` only.
- No wider `E006` expansion is active.

## Fixed Hardening Packet
- dataset: `synthetic_positional_intermediate_pointer_selection_response`
- witness: `V_future_relational_witness_positional_intermediate_pointer_selection`
- control: `V_control_symbolic_positional_intermediate_pointer_selection_regressor`
- backend: `sim_quantum_statevector`
- pair reindex: `1`
- seeds: `42`, `123`, `777`

## Stop Rule
- Stop immediately if the bounded symbolic control matches or beats the witness on both mean `mae` and mean `rank_correlation`.
