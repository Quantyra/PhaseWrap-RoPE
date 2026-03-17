# Q-RoPE E008 Exception Arbitration Gate v1

Date: 2026-03-16

## BLUF
- `E008` passes only to bounded implementation planning review.
- Code and execution remain closed.
- The candidate fails immediately if it becomes explicit exception lookup, disguised revision-state selection, or a loose fairness contract.

## Frozen Task
- task:
  - `synthetic_positional_exception_conditioned_reference_selection_response`

## What Must Be True
- the task must contain:
  - one base-valid candidate under the default positional-content rule
  - one active exception trigger tied to a bounded candidate property
  - one final correct target that is selected only after the exception suppresses the default-valid candidate
- the exception must be decision-critical rather than decorative
- one frozen symbolic family only across all allowed candidate patterns

## Blocked By Default
- token-id shortcuts
- slot-id shortcuts
- explicit exception lookup tables
- direct stale/current revision-state shortcuts
- count-specific symbolic families
- per-exception-pattern symbolic families
- unrestricted higher-order candidate interactions
- transformer surrogates

## Required Hard-Stop Diagnostics
- `coarse_exception_arbitration_state_null_pass`
- `within_exception_arbitration_state_variation_pass`
- `base_rule_nontrivial_pass`
- `exception_trigger_nontrivial_pass`
- `base_only_null_pass`
- `exception_only_null_pass`
- `final_target_nontrivial_pass`
- `candidate_set_nontrivial_pass`
- `token_view_balance_pass`
- `bounded_candidate_count_pass`
- `exception_noncollapse_pass`

## Decision Rule
- Pass only to bounded implementation planning review.
- Stop immediately if the candidate cannot stay genuinely exception-conditioned under a single frozen symbolic family.
