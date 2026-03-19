# Q-RoPE E011 Clause-Intersection Implementation Plan v1

Date: 2026-03-19
Stories: S1612-S1613

## BLUF
- E011 passes only to one bounded local implementation cycle.
- The plan freezes a single clause-intersection symbolic family across all allowed candidate patterns.
- Execution remains bounded to one fixed three-seed packet if implementation is reopened under this plan.

## Frozen Task
- task:
  - synthetic_positional_clause_intersection_reference_selection_response
- witness:
  - V_future_relational_witness_positional_clause_intersection_reference_selection
- bounded symbolic control:
  - V_control_symbolic_positional_clause_intersection_reference_selection_regressor

## Frozen Bounds
- candidate counts:
  - 4, 5
- clause count:
  - exactly 2
- content-class bound:
  - 3
- clause-one viability:
  - more than one candidate remains viable under the positional clause alone
- clause-two viability:
  - more than one candidate remains viable under the content-role clause alone
- final-valid candidates:
  - exactly 1 surviving target after clause intersection

## Symbolic Family Limit
- additive and bounded-quadratic regressor over:
  - declared query summaries
  - per-candidate bounded content summaries
  - per-candidate bounded positional summaries
  - bounded clause-ambiguity summaries
  - bounded aggregate intersection-conflict summaries only
- not allowed:
  - explicit clause ids
  - token-id shortcuts
  - slot-id shortcuts
  - clause-order-specific symbolic families
  - clause-pattern lookup features

## Writable Scope
- src/qrope/synthetic.py
- src/qrope/run.py
- 	ests/test_synthetic.py
- 	ests/test_run_real_mode.py

## Fixed Packet
- backend:
  - sim_quantum_statevector
- seeds:
  - 42, 123, 777

## Hard-Stop Conditions
Stop E011 immediately if implementation requires:
- explicit clause-pattern lookup tables
- symbolic-family branching by candidate count or clause pattern
- token-id shortcuts
- slot-id shortcuts
- candidate-count cap above 5
- content-class cap above 3
- more than two active clauses per example
- examples where either clause is sufficient alone
- examples where the joint intersection is not decision-critical
- content-only solvability by construction
- position-only solvability by construction
