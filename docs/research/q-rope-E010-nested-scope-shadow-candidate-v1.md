# Q-RoPE E010 Nested-Scope Shadow Successor Candidate v1

Date: 2026-03-17
Stories: S1575-S1577

## Candidate
- `synthetic_positional_nested_scope_shadow_selection_response`

## Intent
- Build a bounded synthetic task where:
  - one shared candidate memory is visible
  - two nested active scopes are declared
  - two candidates remain locally eligible under the same base positional-content rule
  - the correct answer is determined only by nearer-scope shadow precedence

## Fairness Direction
- one frozen symbolic family only
- no explicit scope-id lookup tables
- no slot-id shortcuts
- no token-id shortcuts
- no per-pattern shadow lookup families
