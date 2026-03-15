# Q-RoPE E003 Position-Content Deeper Pair-Reindex Hardening Plan v1

Date: 2026-03-15
Stories: S1376-S1378

## BLUF
- The second structural packet survived cleanly.
- The next fixed hardening step is the closure packet `pair_reindex=7` only.
- No wider E003 perturbation expansion is active.

## Fixed Hardening Packet
- dataset: `synthetic_positional_content_gated_offset_selection_response`
- witness: `V_future_relational_witness_positional_content_gated_offset_selection`
- control: `V_control_symbolic_positional_content_gated_offset_selection_regressor`
- backend: `sim_quantum_statevector`
- pair reindex: `7`
- seeds: `42`, `123`, `777`

## Stop Rule
- Stop immediately if the bounded symbolic control matches or beats the witness on both mean `mae` and mean `rank_correlation`.
