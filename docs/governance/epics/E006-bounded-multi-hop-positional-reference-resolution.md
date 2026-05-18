# Epic

## Epic ID and title
E006 - Bounded multi-hop positional reference resolution

## Purpose
Test whether the Q-RoPE witness can survive a bounded task where correctness depends on two-stage positional reference resolution inside one candidate memory rather than direct one-shot selection or repeated independent query reuse.

## Why this epic exists
- The preserved package is now strong on one-shot bounded selection, robustness, position-content composition, and alias disambiguation.
- `E005` failed on repeated shared-memory multi-query reuse under retained nuisance hardening.
- The next materially different uncertainty is whether the line can survive bounded multi-hop relational reference resolution rather than another repeated-query reuse variant.

## Entry condition
- Memo-only until the missing question, candidate, and gate are written and accepted.

## Exit conditions
- preserve one bounded multi-hop survivor
- archive a negative boundary
- or reject the epic at memo/gate level if fairness cannot stay bounded
