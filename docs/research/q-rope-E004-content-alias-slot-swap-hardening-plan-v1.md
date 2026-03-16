# Q-RoPE E004 Content-Alias Slot-Swap Hardening Plan v1

Date: 2026-03-15
Stories: S1405-S1407

## BLUF
- `pair_reindex=1` was non-inert and the witness still led on both gate metrics.
- The next packet is the fixed structural hardening step `slot_swap=1` only.
- No wider `E004` expansion is active.

## Fixed Hardening Packet
- dataset: `synthetic_positional_content_alias_disambiguation_response`
- witness: `V_future_relational_witness_positional_content_alias_disambiguation`
- control: `V_control_symbolic_positional_content_alias_disambiguation_regressor`
- backend: `sim_quantum_statevector`
- slot swap: `1`
- seeds: `42`, `123`, `777`

## Stop Rule
- Stop immediately if the bounded symbolic control matches or beats the witness on both mean `mae` and mean `rank_correlation`.
