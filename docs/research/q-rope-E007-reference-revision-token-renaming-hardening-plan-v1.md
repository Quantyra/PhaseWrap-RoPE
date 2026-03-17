# Q-RoPE E007 Reference Revision Token-Renaming Hardening Plan v1

Date: 2026-03-16
Stories: S1486-S1489

## Next Step
- Run the fixed retained nuisance-hardening packet with `token_permutation=cdab`.

## Frozen Conditions
- Keep only:
  - `V_future_relational_witness_positional_reference_revision_selection`
  - `V_control_symbolic_positional_reference_revision_selection_regressor`
- Keep the same dataset and seed packet:
  - `synthetic_positional_reference_revision_selection_response`
  - `42`, `123`, `777`
- Stop immediately if the control matches or beats the witness on both mean `mae` and mean `rank_correlation`.
