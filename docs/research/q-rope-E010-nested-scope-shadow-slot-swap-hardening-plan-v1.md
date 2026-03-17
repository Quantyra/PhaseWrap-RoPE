# Q-RoPE E010 Nested-Scope Shadow Slot-Swap Hardening Plan v1

Date: 2026-03-17
Stories: S1589-S1591

## Next Step
- Run the fixed second structural hardening packet with `slot_swap=1`.

## Frozen Conditions
- Keep only:
  - `V_future_relational_witness_positional_nested_scope_shadow_selection`
  - `V_control_symbolic_positional_nested_scope_shadow_selection_regressor`
- Keep the same dataset and seed packet:
  - `synthetic_positional_nested_scope_shadow_selection_response`
  - `42`, `123`, `777`
- Stop immediately if the control matches or beats the witness on both mean `mae` and mean `rank_correlation`.
