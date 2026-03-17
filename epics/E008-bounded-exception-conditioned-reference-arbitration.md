# Epic

## Epic ID and title
E008 - Bounded exception-conditioned reference arbitration

## Purpose
Test whether the Q-RoPE witness can survive a bounded task where the correct target is determined by a base positional-content rule plus one bounded exception clause that suppresses an otherwise-valid candidate.

## Why this epic exists
- The preserved package is now strong on one-shot bounded selection, robustness, position-content composition, alias disambiguation, bounded multi-hop reference resolution, and bounded stale/current revision selection.
- `E005` failed on repeated shared-memory multi-query reuse.
- `E006` and `E007` succeeded on bounded reference depth and bounded revision validity.
- The next materially different uncertainty is whether the line can survive bounded rule arbitration where correctness depends on applying an exception condition rather than only selecting the most direct valid referent.

## Entry condition
- Memo-only until the missing question, candidate, and gate are written and accepted.

## Exit conditions
- preserve one bounded exception-arbitration survivor
- archive a negative boundary
- or reject the epic at memo/gate level if fairness cannot stay bounded
