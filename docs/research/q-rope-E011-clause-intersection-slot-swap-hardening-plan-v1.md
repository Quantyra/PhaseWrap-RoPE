# Q-RoPE E011 Clause-Intersection Slot-Swap Hardening Plan v1

Date: 2026-03-19
Stories: S1621-S1623

## Next Step
- Run the fixed second structural hardening packet with `slot_swap=1`.

## Frozen Conditions
- Keep only:
  - `V_future_relational_witness_positional_clause_intersection_reference_selection`
  - `V_control_symbolic_positional_clause_intersection_reference_selection_regressor`
- Keep the same dataset and seed packet:
  - `synthetic_positional_clause_intersection_reference_selection_response`
  - `42`, `123`, `777`
- Stop immediately if the control matches or beats the witness on both mean `mae` and mean `rank_correlation`.
