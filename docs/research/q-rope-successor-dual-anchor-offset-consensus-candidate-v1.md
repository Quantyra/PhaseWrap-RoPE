# Q-RoPE Successor Dual-Anchor Offset Consensus Candidate v1

Date: 2026-03-14
Stories: S1295-S1297

## BLUF
- Candidate: `synthetic_positional_dual_anchor_offset_consensus_response`
- This candidate is admissible at memo level because it is materially different from `key-query-offset-selection`.
- It is still not approved for implementation.

## Core Structure
- two bounded query anchors
- one small bounded candidate key set
- exactly one correct key that satisfies a declared relative-offset rule with respect to both anchors simultaneously
- one or more candidates that satisfy only one anchor rule or match local token statistics while failing the consensus rule
- final response depends on selecting the one candidate that satisfies the dual-anchor positional consensus

## Why This Is Materially Different
`key-query-offset-selection` tested one-of-many selection under one query-relative positional rule.

This candidate would test:
- bounded compositional positional agreement
- across two anchor-relative constraints
- inside one bounded candidate-selection problem

That is not just a harder version of the same task. It changes the type of positional reasoning required.

## Why This Could Matter
If this candidate survives bounded fairness review later:
- it would suggest the witness signal is not limited to single-anchor bounded selection.

If it fails at memo or gate stage:
- it may show the current successor package is already near the useful complexity ceiling for this line.

## Main Risks
- the candidate may collapse into disguised single-anchor scoring
- the symbolic control may need uncontrolled higher-order interactions across anchors and candidates
- the task may become too close to an unbounded attention surrogate

## Current Decision
- `ADMISSIBLE FOR MEMO-LEVEL GATE DESIGN ONLY`
