# Q-RoPE E004 Content-Alias Implementation v1

Date: 2026-03-15
Stories: S1398-S1401

## BLUF
- Implemented `synthetic_positional_content_alias_disambiguation_response` inside the frozen `E004` scope.
- The task keeps alias pressure real: every active candidate set contains a same-class distractor that must be disambiguated by position.
- The witness and control both use one frozen family across candidate counts `3`, `4`, `5`, content classes `0`, `1`, `2`, and active alias patterns.

## Implemented Task
- dataset: `synthetic_positional_content_alias_disambiguation_response`
- witness: `V_future_relational_witness_positional_content_alias_disambiguation`
- control: `V_control_symbolic_positional_content_alias_disambiguation_regressor`

## Construction
- one query anchor
- active candidate counts `3`, `4`, `5`
- bounded content classes `0`, `1`, `2`
- exactly one correct candidate under the joint rule:
  - the candidate must match the query-relative offset rule, and
  - the candidate must match the bounded target content class
- every active set includes:
  - at least one same-class alias distractor that is position-wrong
  - at least one position-only distractor
- target and alias slots rotate across the active support

## Fairness Notes
- one frozen symbolic family spans all allowed candidate counts and alias patterns
- only declared query summaries, per-candidate content summaries, per-candidate offset summaries, and bounded aggregate alias-ambiguity summaries are used
- no raw token-identity shortcuts, no slot-identity shortcuts, no count-specific or alias-pattern-specific symbolic families

## Outcome
- The bounded implementation held.
- `E004` remains admissible for one fixed three-seed packet only.
