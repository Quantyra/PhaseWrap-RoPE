# Epic

## Epic ID and title
E009 - Bounded scope-conditioned reference masking

## Purpose
Test whether the Q-RoPE witness can survive a bounded task where the correct target is determined not just by positional-content fit, but by whether the candidate lies inside one active local scope while stronger global distractors remain visible outside that scope.

## Why this epic exists
- The preserved package is now strong on direct bounded selection, robustness, position-content composition, alias disambiguation, multi-hop reference resolution, reference revision, and exception-conditioned arbitration.
- `E005` failed on repeated shared-memory multi-query reuse.
- `E008` succeeded on bounded exception-conditioned rule suppression.
- The next materially different uncertainty is whether the line can survive bounded scope masking where eligibility depends on a local active region rather than only on direct validity, revision status, or exception override.

## Entry condition
- Memo-only until the missing question, candidate, and gate are written and accepted.

## Exit conditions
- preserve one bounded scope-masking survivor
- archive a negative boundary
- or reject the epic at memo/gate level if bounded scope fairness cannot stay clean
