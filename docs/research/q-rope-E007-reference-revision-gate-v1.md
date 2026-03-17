# Q-RoPE E007 Reference Revision Gate v1

Date: 2026-03-16

## BLUF
- The candidate is admissible only if stale/current validity can stay bounded and auditable.
- It passes only to bounded implementation planning review.
- It fails immediately if stale-versus-current discrimination collapses into token/slot lookup or unbounded revision bookkeeping.

## Task
- `synthetic_positional_reference_revision_selection_response`

## Admissibility Conditions
- the task must require genuine stale-versus-current discrimination inside one bounded candidate memory
- at least one stale candidate and one revised candidate must coexist in every active candidate set
- exactly one candidate may satisfy the declared current-validity rule
- one frozen symbolic family only across all allowed candidate sets
- the task must not collapse to simple content-only or position-only solvability by construction

## Allowed Symbolic Family
- additive and bounded-quadratic terms over:
  - declared query summaries
  - per-candidate bounded content summaries
  - per-candidate bounded positional summaries
  - bounded aggregate stale/current ambiguity summaries

## Blocked By Default
- token-id shortcuts
- slot-id shortcuts
- explicit stale/current lookup tables
- per-revision-pattern symbolic families
- unbounded update bookkeeping
- transformer surrogates

## Required Hard-Stop Diagnostics
- `coarse_reference_revision_state_null_pass`
- `within_reference_revision_state_variation_pass`
- `stale_current_competition_nontrivial_pass`
- `stale_only_null_pass`
- `current_only_null_pass`
- `revision_target_nontrivial_pass`
- `candidate_set_nontrivial_pass`
- `token_view_balance_pass`
- `bounded_candidate_count_pass`
- `revision_noncollapse_pass`

## Decision
- `PASS_TO_BOUNDED_IMPLEMENTATION_PLANNING_REVIEW`
