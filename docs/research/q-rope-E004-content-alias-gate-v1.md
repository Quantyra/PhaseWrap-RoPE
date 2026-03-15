# Q-RoPE E004 Content-Alias Gate v1

Date: 2026-03-15
Stories: S1394-S1395

## BLUF
- `synthetic_positional_content_alias_disambiguation_response` passes only to bounded implementation planning review.
- The task must stay genuinely alias-disambiguative: at least two active candidates must share the target content class and only one may satisfy the positional rule.
- Code and execution remain closed.

## Frozen Task
- task:
  - `synthetic_positional_content_alias_disambiguation_response`
- target rule:
  - exactly one active candidate satisfies both the bounded target content class and the bounded positional offset rule
- alias pressure:
  - at least one active distractor must share the target content class while remaining position-wrong

## Bounded Symbolic Family
The symbolic control may use only:
- declared query summaries
- per-candidate bounded content summaries
- per-candidate bounded offset summaries
- bounded aggregate alias-ambiguity summaries

The symbolic control may not use:
- raw token identity
- slot identity
- latent ids
- per-slot lookup tables
- class-specific symbolic families
- unrestricted higher-order candidate interactions
- transformer surrogates

## Hard-Stop Diagnostics
- `coarse_content_alias_state_null_pass`
- `within_content_alias_state_variation_pass`
- `alias_pressure_nontrivial_pass`
- `content_only_null_pass`
- `position_only_null_pass`
- `joint_target_nontrivial_pass`
- `candidate_set_nontrivial_pass`
- `token_view_balance_pass`
- `bounded_content_class_pass`
- `bounded_candidate_count_pass`
- `alias_slot_rotation_pass`
- `joint_noncollapse_pass`

## Rejection Conditions
Reject the candidate immediately if:
- content match alone identifies the target by construction
- slot identity can identify the target by construction
- alias distractors are not active in every candidate set
- different symbolic families are needed by candidate count or alias pattern
- content classes or candidate counts exceed the frozen bounded caps

## Decision Standard
- success at this gate means only that bounded implementation planning is justified
- it does not authorize code or execution
