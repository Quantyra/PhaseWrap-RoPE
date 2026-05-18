# E010 Bounded Nested-Scope Shadow Resolution

Date: 2026-03-17
Status: memo-only

## BLUF
- `E010` asks whether the witness can survive bounded reference selection when multiple scope-consistent candidates remain locally eligible and the correct answer is determined only by nearer-scope shadow precedence.
- This is materially different from `E009`, which tested simple local-scope masking against stronger out-of-scope distractors.
- Execution remains closed until the gate and bounded plan are accepted.

## Missing Question
- Can the witness survive bounded candidate selection when two candidates satisfy the base positional-content rule inside nested active scopes, but only the candidate in the nearer active scope is valid after shadow precedence is applied?

## Candidate Direction
- `synthetic_positional_nested_scope_shadow_selection_response`

## Why This Epic Exists
- `E009` preserved bounded local-scope eligibility masking.
- The next gap is not flat in-scope versus out-of-scope filtering.
- The next materially different question is bounded hierarchical precedence among multiple locally eligible scoped candidates.
