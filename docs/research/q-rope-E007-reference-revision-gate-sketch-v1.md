# Q-RoPE E007 Reference Revision Gate Sketch v1

Date: 2026-03-16

## BLUF
- The candidate is admissible only if stale/current validity can stay bounded and auditable.
- Reject it if it becomes a disguised lookup task or requires unbounded update bookkeeping.

## Gate Conditions
- the task must require genuine stale-versus-current discrimination
- stale and revised candidates must coexist in the active candidate memory
- one frozen symbolic family only
- bounded candidate count cap must remain explicit and small
- blocked by default:
  - token-id shortcuts
  - slot-id shortcuts
  - explicit stale/current lookup tables
  - per-revision-pattern symbolic families
  - transformer surrogates

## Required Diagnostics
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
