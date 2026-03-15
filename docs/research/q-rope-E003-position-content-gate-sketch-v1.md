# Q-RoPE E003 Position-Content Gate Sketch v1

## BLUF
- `E003` should only proceed if one bounded task can keep both position and content decision-relevant without fairness blow-up.
- The symbolic control must remain frozen, bounded, and auditable across the entire candidate family.
- If the task collapses into content lookup or position-only scoring, stop `E003` immediately.

## Gate Questions
- Is the correct candidate impossible to recover from bounded content summaries alone?
- Is the correct candidate impossible to recover from bounded positional summaries alone?
- Can one bounded symbolic family cover the task without token-id, slot-id, or latent-id shortcuts?
- Does success or failure still change a real program decision?
- Is this task more model-like than the current position-only survivor set without becoming an uncontrolled benchmark surrogate?

## Default Rejection Conditions
- content labels become disguised token identifiers
- position becomes incidental rather than necessary
- symbolic fairness requires count-specific or class-specific lookup families
- the candidate reduces to a renamed version of an existing successor or `E002` line

## If Passed
- write one explicit memo-level gate only
- keep execution closed until a bounded implementation plan exists
