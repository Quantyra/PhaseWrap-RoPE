# Q-RoPE E004 Content-Alias Token-Renaming Hardening Plan v1

Date: 2026-03-15
Stories: S1398-S1401

## BLUF
- The first packet survived.
- The next retained hardening step is `token_permutation=cdab` only.
- No wider `E004` perturbation expansion is active.

## Fixed Hardening Packet
- dataset: `synthetic_positional_content_alias_disambiguation_response`
- witness: `V_future_relational_witness_positional_content_alias_disambiguation`
- control: `V_control_symbolic_positional_content_alias_disambiguation_regressor`
- backend: `sim_quantum_statevector`
- token permutation: `cdab`
- seeds: `42`, `123`, `777`

## Stop Rule
- Stop immediately if the bounded symbolic control matches or beats the witness on both mean `mae` and mean `rank_correlation`.
