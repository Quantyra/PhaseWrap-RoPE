# Q-RoPE E010 Nested-Scope Shadow Token-Renaming Hardening Plan v1

Date: 2026-03-17
Stories: S1582-S1585

## Next Step
- Run the fixed retained nuisance-hardening packet with `token_permutation=cdab`.

## Frozen Conditions
- Keep only:
  - `V_future_relational_witness_positional_nested_scope_shadow_selection`
  - `V_control_symbolic_positional_nested_scope_shadow_selection_regressor`
- Keep the same dataset and seed packet:
  - `synthetic_positional_nested_scope_shadow_selection_response`
  - `42`, `123`, `777`
- Stop immediately if the control matches or beats the witness on both mean `mae` and mean `rank_correlation`.
