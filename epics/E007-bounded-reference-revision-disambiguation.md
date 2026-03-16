# Epic

## Epic ID and title
E007 - Bounded reference revision disambiguation

## Purpose
Test whether the Q-RoPE witness can survive a bounded task where candidate memory contains stale and revised reference candidates, and correctness depends on selecting the currently valid revision rather than a static referent.

## Why this epic exists
- The preserved package is now strong on one-shot bounded selection, robustness, position-content composition, alias disambiguation, and bounded multi-hop reference resolution.
- `E005` failed on repeated shared-memory multi-query reuse.
- `E006` succeeded on two-stage reference composition.
- The next materially different uncertainty is whether the line can survive bounded revision pressure where stale and updated candidates coexist in the same candidate memory.

## Entry condition
- Memo-only until the missing question, candidate, and gate are written and accepted.

## Exit conditions
- preserve one bounded revision-disambiguation survivor
- archive a negative boundary
- or reject the epic at memo/gate level if fairness cannot stay bounded
