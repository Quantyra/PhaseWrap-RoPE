# Q-RoPE E003 Position-Content Gate v1

Date: 2026-03-14
Stories: S1362-S1363

## BLUF
- The position-content candidate passes the memo bar only if both position and content are genuinely necessary and the symbolic control remains bounded under one frozen family.
- This gate does not approve implementation yet.
- It passes only to bounded implementation planning if the fairness contract stays clean and neither dimension collapses into a shortcut.

## Task
- `synthetic_positional_content_gated_offset_selection_response`

## Candidate Intent
- one query anchor with a bounded content-key class
- a small bounded candidate set
- each candidate has:
  - a bounded content class
  - a bounded relative-offset relation to the query anchor
- exactly one candidate is correct because it jointly satisfies:
  - the declared content-key relevance rule
  - the declared positional offset rule
- distractors must be constructed so that:
  - some satisfy content only
  - some satisfy position only
  - some satisfy neither
- correctness must require the conjunction, not either dimension alone

## Bounded Symbolic Control
- additive and bounded-quadratic regressor over declared query summaries, per-candidate content summaries, per-candidate offset summaries, and bounded aggregate ambiguity summaries only

## Frozen Declared Summary Scope
Allowed declared summaries may include only:
- query content-key summary
- candidate content-class summary
- candidate relative-offset summary to the query anchor
- bounded candidate-count summary
- bounded aggregate content-confusability summaries across the active set
- bounded aggregate offset-confusability summaries across the active set
- bounded aggregate conjunction-ambiguity summaries across the active set

Not allowed:
- raw token identity
- slot identity
- latent ids
- per-class lookup tables
- count-specific symbolic families
- unrestricted higher-order candidate interactions
- transformer surrogates
- basis expansion that scales with content-class or candidate-count product

## Required Candidate-Level Admissibility Conditions
The candidate passes only if all are true:
- bounded content classes are genuinely active in defining task difficulty
- bounded positional offsets are genuinely active in defining task difficulty
- the correct candidate cannot be recovered from a content-only bounded control by construction
- the correct candidate cannot be recovered from a position-only bounded control by construction
- exactly one candidate remains correct under the declared conjunction rule
- the candidate-count cap stays explicit and small
- the symbolic control can be written as one frozen bounded family across the allowed candidate family
- success or failure would still change whether the package goes beyond position-only bounded evidence

## Required Hard-Stop Diagnostics
The candidate may advance only if the design can support these diagnostics cleanly:
- `coarse_position_content_state_null_pass`
- `within_position_content_state_variation_pass`
- `content_only_null_pass`
- `position_only_null_pass`
- `joint_target_nontrivial_pass`
- `candidate_set_nontrivial_pass`
- `token_view_balance_pass`
- `bounded_content_class_pass`
- `bounded_candidate_count_pass`
- `joint_noncollapse_pass`

## Candidate-Level Stop Rule
Stop the candidate immediately if any are true:
- content labels become disguised token identifiers
- position becomes incidental rather than necessary
- the task is solvable by bounded content-only summaries by construction
- the task is solvable by bounded position-only summaries by construction
- the symbolic control requires count-specific or class-specific lookup families
- the candidate reduces to a renamed version of an existing successor or `E002` line
- the task no longer provides decision leverage beyond the preserved position-only package

## Gate Decision Rule
- Pass to bounded implementation planning only if the candidate specification remains clean under this gate.
- Otherwise stop `E003` and treat the current package as the practical ceiling for bounded position-only evidence.
