# Q-RoPE E003 Position-Content Implementation v1

Date: 2026-03-14
Stories: S1366-S1369

## BLUF
- Implemented `synthetic_positional_content_gated_offset_selection_response` inside the frozen `E003` scope.
- The task stays jointly gated by position and content; every active candidate set contains one joint target, one content-only distractor, and one position-only distractor.
- The witness and control both use one frozen family across candidate counts `3`, `4`, `5` and content classes `0`, `1`, `2`.

## Implemented Task
- dataset: `synthetic_positional_content_gated_offset_selection_response`
- witness: `V_future_relational_witness_positional_content_gated_offset_selection`
- control: `V_control_symbolic_positional_content_gated_offset_selection_regressor`

## Construction
- one query anchor
- active candidate counts `3`, `4`, `5`
- bounded content classes `0`, `1`, `2`
- exactly one correct candidate under the joint rule:
  - the candidate must match the query-relative offset rule, and
  - the candidate must match the bounded content-class rule
- every active set includes:
  - at least one content-only distractor
  - at least one position-only distractor

## Fairness Notes
- one frozen symbolic family spans all allowed candidate counts and content classes
- only declared query summaries, per-candidate content summaries, per-candidate offset summaries, and bounded aggregate ambiguity summaries are used
- no raw token-identity shortcuts, no slot-identity shortcuts, no count-specific or class-specific symbolic families

## Validation
- `PYTHONPATH=src python -m pytest tests/test_synthetic.py tests/test_qsim.py tests/test_run_real_mode.py`
- `336 passed`

## Outcome
- The bounded implementation held.
- `E003` remains admissible for one fixed three-seed packet only.
