# Q-RoPE Successor-Class Implementation Gate v1

Date: 2026-03-14
Stories: S1261-S1262

## BLUF
- A transformer-adjacent validation class may exist, but no specific candidate may open yet.
- The class passes only to bounded candidate specification, not to implementation.
- Execution remains closed until one candidate proves that it is more model-like than `offset-retrieval` while still preserving bounded fairness.

## Candidate Class
- bounded transformer-adjacent positional validation

## Working Direction
- `synthetic_positional_key_query_offset_selection_response`

## Gate Decision Standard
A successor-class candidate may advance only if all of the following are made explicit in a candidate memo:
- why the task is more model-like than `offset-retrieval`
- why the task is not just a renamed realism-bridge retrieval variant
- why the symbolic control remains bounded, auditable, and frozen
- what exact decision would change if the candidate succeeds or fails
- why theory-only work is lower value than this candidate now

## Frozen Fairness Requirements
Any candidate in this class must preserve all of the following:
- one witness family only
- one bounded symbolic control family only
- declared summary scope written before implementation
- fixed packet seeds if execution later opens
- fixed hard-stop rule on mean `mae` and mean `rank_correlation`
- explicit forbidden-feature audit

## Required Candidate-Level Declared Summary Scope
A future candidate must declare its allowed symbolic scope in advance, including only bounded summaries such as:
- query-anchor identity summary
- candidate-relative offset summaries
- candidate token-identity summaries
- target-offset agreement summaries
- candidate-confusability summaries
- bounded additive and bounded-quadratic interactions only

## Required Inadmissibility Checks
Reject a candidate immediately if any of the following are true:
- it collapses into another anchor-to-target retrieval task
- it requires many candidates or long sequence length to work
- it requires a transformer surrogate, attention training, or uncontrolled benchmark data
- its success would still not change the current escalation outlook
- its fairness contract cannot be written concisely and audited directly

## Required Stop Rule
If a clean candidate cannot be specified under this gate, stop the successor class here and treat the current package as the practical evidence ceiling.

## Gate Decision
- `PASS TO CANDIDATE SPECIFICATION ONLY`
- no implementation planning
- no execution
