# Q-RoPE E011 Clause-Intersection Deeper Pair-Reindex Hardening Plan v1

Date: 2026-03-19
Stories: S1624-S1626

## Next Step
- Run the fixed closure packet with `pair_reindex=7`.

## Frozen Conditions
- Keep only:
  - `V_future_relational_witness_positional_clause_intersection_reference_selection`
  - `V_control_symbolic_positional_clause_intersection_reference_selection_regressor`
- Keep the same dataset and seed packet:
  - `synthetic_positional_clause_intersection_reference_selection_response`
  - `42`, `123`, `777`
- Stop immediately if the control matches or beats the witness on both mean `mae` and mean `rank_correlation`.
