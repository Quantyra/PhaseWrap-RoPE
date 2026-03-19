# E011 Bounded Clause-Intersection Reference Selection

Date: 2026-03-18
Status: proposed

## BLUF
- E011 asks whether the Q-RoPE witness can survive bounded candidate selection when no single query clause is sufficient and only the intersection of two bounded clauses identifies the valid target.
- This is materially different from shared-memory repeated multi-query reuse, exception arbitration, and nested-scope precedence.
- The epic begins in memo-only candidate design mode.

## Missing Question
- Can the witness survive a bounded task where one clause constrains positional eligibility, a second clause constrains content-role eligibility, and only their intersection yields the correct referent?

## Why This Epic Exists
- The preserved package is now strong on bounded direct selection, reference control, revision, exception handling, and scope precedence.
- It is not yet strong on bounded conjunctive clause intersection where each clause is individually insufficient.
- Success or failure here would change whether the current package should be read as supporting bounded intersection-style query composition rather than only single-rule arbitration.
