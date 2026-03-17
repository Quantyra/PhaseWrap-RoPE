# Q-RoPE E008 Exception Arbitration Missing Question v1

Date: 2026-03-16

## BLUF
- The next missing question is whether the witness can survive bounded candidate selection when one base-valid candidate must be rejected by an explicit exception condition and a second candidate becomes the correct answer.
- This is materially different from `E007`, which tested stale-versus-current validity, not bounded rule arbitration.
- Execution should remain closed until the gate freezes a bounded exception family and diagnostics.

## Missing Question
- Can the witness survive a bounded task where the correct target depends on composing:
  - a base positional-content selection rule
  - with one bounded exception clause that suppresses an otherwise-valid candidate
- without collapsing to slot heuristics, token identity, or explicit exception lookup shortcuts?

## Why This Matters
- The current package is strong on direct bounded selection, multi-hop reference, and revision-validity selection.
- It is not yet strong on bounded conflict arbitration where an exception overrides the default valid referent.
- Success or failure here would change whether the current package can be read as having any bounded rule-arbitration capability rather than only direct validity selection.
