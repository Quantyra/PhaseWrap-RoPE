# Q-RoPE E005 Shared-Memory Multi-Query Gate v1

Date: 2026-03-15
Stories: S1427-S1428

## BLUF
- The shared-memory multi-query candidate passes the memo bar only if both queries genuinely reuse one bounded candidate memory and the symbolic control remains one frozen family across query positions.
- This gate does not approve implementation yet.
- It passes only to bounded implementation planning if shared-memory reuse remains real and per-query decomposition stays blocked.

## Task
- `synthetic_positional_shared_memory_multi_query_selection_response`

## Candidate Intent
- one bounded candidate memory per example
- exactly two query prompts over that same memory
- each query specifies a bounded position-content retrieval rule
- each query has exactly one correct candidate in the shared memory
- at least one active distractor remains relevant across both queries
- correctness of the example requires answering both queries correctly under one frozen fairness contract

## Bounded Symbolic Control
- additive and bounded-quadratic regressor over declared shared-memory summaries, per-candidate summaries, per-query summaries, and bounded aggregate cross-query ambiguity summaries only

## Frozen Declared Summary Scope
Allowed declared summaries may include only:
- shared candidate-memory summaries
- per-candidate bounded content summaries
- per-candidate bounded offset summaries relative to each query
- bounded query-position summary for query one versus query two
- bounded candidate-count summary
- bounded aggregate within-query ambiguity summaries
- bounded aggregate cross-query conflict or overlap summaries

Not allowed:
- raw token identity
- slot identity
- latent ids
- per-query lookup tables
- query-order-specific symbolic families
- count-specific symbolic families
- unrestricted higher-order candidate interactions
- transformer surrogates
- basis expansion that scales with query-by-candidate lookup structure

## Required Candidate-Level Admissibility Conditions
The candidate passes only if all are true:
- the same candidate memory is genuinely reused across both queries
- answering query one does not trivially determine query two by construction
- the task does not decompose into two unrelated single-query packets
- content-only bounded control cannot solve both queries by construction
- position-only bounded control cannot solve both queries by construction
- the paired target is nontrivial under bounded distractor pressure
- the query count stays fixed and small at `2`
- the candidate-count cap stays explicit and small
- the symbolic control can be written as one frozen bounded family across both query positions and all allowed candidate counts
- success or failure would change whether the package extends beyond one-shot bounded selection into shared-memory repeated access

## Required Hard-Stop Diagnostics
The candidate may advance only if the design can support these diagnostics cleanly:
- `coarse_shared_memory_state_null_pass`
- `within_shared_memory_state_variation_pass`
- `query_pair_nontrivial_pass`
- `query_one_only_null_pass`
- `query_two_only_null_pass`
- `joint_query_target_nontrivial_pass`
- `shared_candidate_set_nontrivial_pass`
- `token_view_balance_pass`
- `bounded_candidate_count_pass`
- `bounded_query_count_pass`
- `cross_query_noncollapse_pass`
- `shared_memory_reuse_pass`

## Candidate-Level Stop Rule
Stop the candidate immediately if any are true:
- the two queries can be solved independently by separate bounded lookup families
- query order becomes a disguised slot-identity shortcut
- shared memory is nominal rather than necessary
- content-only summaries solve the task by construction
- position-only summaries solve the task by construction
- the symbolic control requires query-specific or count-specific families
- the task reduces to a renamed one-shot successor line
- the task no longer provides decision leverage beyond the preserved one-shot package

## Gate Decision Rule
- Pass to bounded implementation planning only if the candidate specification remains clean under this gate.
- Otherwise stop `E005` and treat the current package as the practical ceiling for one-shot bounded selection evidence.
