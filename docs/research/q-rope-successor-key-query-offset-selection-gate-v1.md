# Q-RoPE Successor Key-Query Offset Selection Gate v1

Date: 2026-03-14
Stories: S1266-S1267

## BLUF
- The key-query offset-selection candidate passes the memo bar only if it stays genuinely one-of-many and the symbolic control stays bounded.
- This gate does not approve implementation yet.
- It passes only to bounded implementation planning if the candidate-level fairness contract is frozen cleanly.

## Task
- `synthetic_positional_key_query_offset_selection_response`

## Witness
- `V_future_relational_witness_positional_key_query_offset_selection`

## Bounded Symbolic Control
- additive and bounded-quadratic regressor over declared query-anchor and candidate-set summaries only

## Frozen Declared Summary Scope
Allowed declared summaries may include only:
- query-anchor identity summary
- per-candidate relative-offset summaries
- per-candidate token-identity summaries
- per-candidate target-agreement summaries
- candidate-set confusability summary
- bounded aggregate summaries across the small candidate set

Not allowed:
- latent ids
- candidate lookup tables keyed by microstate identity
- unrestricted higher-order candidate interactions
- transformer surrogates or learned attention components

## Required Candidate-Level Admissibility Conditions
The candidate passes only if all are true:
- the label depends on selecting one correct key from a bounded candidate set
- at least three candidates are genuinely active in the scoring problem
- the candidate does not collapse into target-vs-distractor scoring only
- the symbolic control can be written as a frozen bounded family with explicit feature audit
- success or failure would still change whether successor-class validation should exist

## Required Hard-Stop Diagnostics For Any Later Implementation
If the candidate later reaches implementation planning, it must declare diagnostics for:
- `coarse_key_query_selection_state_null_pass`
- `within_key_query_selection_state_variation_pass`
- `candidate_set_nontrivial_pass`
- `target_selection_nontrivial_pass`
- `token_view_balance_pass`
- `bounded_candidate_count_pass`

## Required Audits For Any Later Implementation
- `allowed_key_query_selection_symbolic_basis_frozen_pass`
- `forbidden_key_query_selection_feature_family_absent_pass`

## Candidate-Level Stop Rule
Stop the candidate immediately if any of the following are true:
- the candidate cannot be specified with genuine one-of-many selection
- the symbolic control requires lookup blow-up or uncontrolled higher-order interactions
- the candidate needs larger candidate sets or longer sequences to work at all
- the candidate no longer provides decision leverage beyond `offset-retrieval`

## Gate Decision Rule
- Pass to bounded implementation planning only if the candidate specification remains clean under this gate.
- Otherwise stop the successor class and treat the current package as the practical evidence ceiling.
