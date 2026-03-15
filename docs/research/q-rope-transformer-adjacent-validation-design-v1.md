# Q-RoPE Transformer-Adjacent Validation Design v1

Date: 2026-03-14
Stories: S1258-S1260

## BLUF
- The next admissible design target is one bounded transformer-adjacent positional validation task.
- It should test whether the current witness signal survives a more model-like positional selection problem without turning into an uncontrolled benchmark.
- This is still memo-level only. No execution is justified yet.

## Missing Question
- Can one bounded transformer-adjacent positional validation task be defined such that success would materially increase confidence that the witness signal is relevant to RoPE-like positional retrieval in a more model-like selection setting, while failure would justify treating the current realism-bridge result as the practical evidence ceiling?

## Decision Leverage
If the answer is `yes`:
- a new design gate becomes justified for a successor evidence class beyond realism-bridge.

If the answer is `no`:
- the current package should be treated as the practical evidence ceiling for the positional-relevance line.

## Why This Is The Right Next Evidence Class
- transfer evidence is already saturated
- abstract bridge evidence is already saturated
- realism-bridge produced one positive survivor: `offset-retrieval`
- another realism-bridge retrieval variant would likely add count, not decision leverage
- the missing decision is now whether the line can move one bounded step closer to model-like positional selection behavior

## Candidate Design Direction
Working candidate family:
- `synthetic_positional_key_query_offset_selection_response`

Proposed structure:
- one designated query anchor
- a small bounded candidate set
- one target candidate identified by a relative offset rule from the query anchor
- one or more distractor candidates that share token identity or coarse local statistics with the target
- final response depends on selecting the correct candidate under the declared relative-offset rule, not merely scoring one relation in isolation

## Why This Is Transformer-Adjacent
This is closer to transformer positional behavior because it introduces:
- query-conditioned selection
- bounded candidate competition
- retrieval of one correct positional relation from a small set

This is still bounded and local because it avoids:
- full learned attention stacks
- large-sequence language modeling
- uncontrolled benchmark data
- hardware execution

## Bounded Fairness Requirement
Any future execution design must still support:
- one witness family only
- one bounded symbolic control family only
- fixed packet seeds
- explicit declared-summary scope
- explicit stop rule on declared primary metrics

## Required Symbolic Control Scope
The control must be limited to declared summaries such as:
- query-anchor identity summary
- candidate-relative offset summaries
- candidate token-identity summaries
- target-offset agreement summaries
- candidate-confusability summaries
- bounded additive and bounded-quadratic interactions only

## Admissibility Checks
A task in this class is admissible only if all are true:
- it is materially more model-like than `offset-retrieval`
- it still admits a frozen bounded symbolic challenger
- it does not require training a transformer surrogate
- it does not collapse into a standard realism-bridge retrieval task with renamed fields
- success or failure would change whether successor-class validation should exist at all

## Inadmissibility Conditions
Reject the class if it becomes any of the following:
- just another anchor-to-target retrieval variant
- a disguised large benchmark
- a fairness contract too loose to audit
- a design that requires many candidates or deep sequence length to work
- a design whose positive result would still not change the escalation outlook

## Gate Ladder
- memo-level design note
- memo-level admissibility review
- successor-class gate memo
- bounded implementation plan if and only if the gate passes
- one bounded execution cycle if and only if the plan is accepted
- preserve or stop

## Stop Condition
If no clean bounded transformer-adjacent task can be defined without violating fairness or collapsing back into realism-bridge, stop the line here and treat the current package as the practical ceiling.

## VP-of-Research Judgment
- This is the right next planning target.
- It is not yet a justified execution target.
- The memo should be used to decide whether a successor evidence class even exists.
