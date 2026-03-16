# Q-RoPE E006 Multi-Hop Reference Gate v1

Date: 2026-03-15
Stories: S1450-S1451

## BLUF
- `E006` is admissible only if it stays genuinely multi-hop.
- The candidate fails immediately if the final target can be derived directly from the query without the intermediate candidate.
- Code and execution remain closed until bounded implementation planning is accepted.

## Frozen Task
- candidate:
  - `synthetic_positional_intermediate_pointer_selection_response`
- working interpretation:
  - bounded query -> intermediate -> target positional reference resolution

## Required Gate Conditions
- exactly one intermediate candidate per example under the first-hop rule
- exactly one final target per example under the second-hop rule
- the final target must not be directly derivable from the query-conditioned rule alone
- one frozen symbolic family across all allowed candidate counts
- bounded first-hop summaries and second-hop summaries only
- active distractors at both hop levels
- the intermediate hop must be decision-critical, not ornamental
- no token-id or slot-id shortcuts
- no latent pointer tables
- no per-pattern lookup families

## Required Diagnostics
- `coarse_multi_hop_state_null_pass`
- `within_multi_hop_state_variation_pass`
- `first_hop_nontrivial_pass`
- `second_hop_nontrivial_pass`
- `direct_target_null_pass`
- `intermediate_criticality_pass`
- `candidate_set_nontrivial_pass`
- `token_view_balance_pass`
- `bounded_candidate_count_pass`
- `multi_hop_noncollapse_pass`

## Immediate Reject Conditions
- task collapses into direct one-shot selection
- intermediate hop is recoverable from a direct query-to-target summary
- symbolic control requires latent pointer tables or per-pattern lookup families
- candidate count or hop depth expands beyond a small bounded cap
- fairness requires separate symbolic families by candidate count or hop pattern

## Gate Decision
- pass only to bounded implementation planning review if all conditions above remain satisfiable under one frozen symbolic family
- otherwise stop `E006` at memo level
