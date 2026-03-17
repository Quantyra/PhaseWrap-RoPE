# Q-RoPE E009 Scope-Masking Gate Sketch v1

Date: 2026-03-16
Stories: S1543-S1545

## Gate Intent
- Freeze a bounded task where local scope membership is decision-critical and cannot be replaced by token identity, slot heuristics, or explicit scope lookup shortcuts.

## Must Hold
- one bounded candidate memory
- one active local scope and one inactive outer region
- at least one out-of-scope distractor with stronger apparent base match than the final in-scope target
- exactly one final valid in-scope target
- one frozen symbolic family only

## Must Fail Fast If Needed
- explicit scope-id lookup tables
- token-id shortcuts
- slot-id shortcuts
- count-specific symbolic families
- scope-pattern-specific symbolic families
- fairness blow-up beyond a small declared candidate cap
