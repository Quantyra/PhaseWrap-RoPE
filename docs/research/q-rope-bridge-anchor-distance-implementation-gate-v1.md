# Q-RoPE Bridge Anchor-Distance Implementation Gate v1

## Task
- `synthetic_positional_anchor_distance_response`

## Witness
- `V_future_relational_witness_positional_anchor_distance`

## Bounded Symbolic Control
- additive and bounded-quadratic regressor over declared anchor-relative distance summaries only

## Hard-Stop Diagnostics
Do not interpret any packet unless all of the following are true:
- `coarse_anchor_distance_state_null_pass = true`
- `within_anchor_distance_state_variation_pass = true`
- `latent_anchor_distance_diversity_pass = true`
- `token_view_balance_pass = true`
- `anchor_distance_length_balance_pass = true`
- `anchor_distance_target_nontrivial_pass = true`

## Frozen Fairness Contract
Allowed symbolic basis:
- declared coarse anchor-relative distance indicators
- declared first-order analog summaries for anchor-relative distance
- bounded quadratic interactions over declared anchor-distance summaries only

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
