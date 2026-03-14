# Q-RoPE Bridge Anchor-Span-Membership Implementation Gate v1

## Task
- `synthetic_positional_anchor_span_membership_response`

## Witness
- `V_future_relational_witness_positional_anchor_span_membership`

## Bounded Symbolic Control
- additive and bounded-quadratic regressor over declared anchor-relative span-membership summaries only

## Hard-Stop Diagnostics
Do not interpret any packet unless all of the following are true:
- `coarse_anchor_span_membership_state_null_pass = true`
- `within_anchor_span_membership_state_variation_pass = true`
- `latent_anchor_span_membership_diversity_pass = true`
- `token_view_balance_pass = true`
- `anchor_span_membership_length_balance_pass = true`
- `anchor_span_membership_target_nontrivial_pass = true`

## Frozen Fairness Contract
Allowed symbolic basis:
- declared coarse anchor-relative span-membership indicators
- declared first-order analog summaries for anchor-relative span-membership
- bounded quadratic interactions over declared anchor-span-membership summaries only

Forbidden feature families:
- latent ids
- exact microstate lookup tables
- hidden tuple caches
- uncontrolled basis growth after packet review

## Decision Rule
- Keep the line memo-only until the hard-stop diagnostics, bounded symbolic family, and stop rule are all frozen.
- If later execution opens, stop the line immediately if the bounded control matches or beats the witness on both:
  - `mae`
  - `rank_correlation`

## Scope
- local only
- no hardware
- no publication work
- no additional challengers in this gate
