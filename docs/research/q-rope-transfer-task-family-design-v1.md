# Q-RoPE Transfer Task Family Design v1

Date: 2026-03-11
Stories: S846

## Goal
Define the first transfer family that is materially different from `synthetic_symbolic_insufficiency_transition_response` while preserving the same fairness discipline.

## Candidate Family
- `synthetic_symbolic_insufficiency_path_response`

## Design Intent
- preserve bounded symbolic fairness review
- change the problem from one-step transition response to short relational path response
- require the witness to model path-level structure rather than a single transition-local target

## Family Requirements
- no latent ids
- no exact microstate keys
- no hidden tuple lookup
- coarse path-state nullness by construction
- within-state latent variation by construction
- fixed bounded symbolic basis must be declared before implementation approval

## Why This Is Materially Different
- the current benchmark is transition-local
- the transfer family is path-local across multiple linked relational steps
- this tests whether the witness advantage is transportable, not merely overfit to one transition geometry
