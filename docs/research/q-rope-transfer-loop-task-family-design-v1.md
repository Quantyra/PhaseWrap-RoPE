# Q-RoPE Transfer Loop-Closure Task Family Design v1

Date: 2026-03-11
Stories: S877

## Goal
Define a second materially different transfer family from both the standing transition benchmark and the first path-local transfer line.

## Candidate Family
- `synthetic_symbolic_insufficiency_loop_closure_response`

## Design Intent
- preserve the same frozen symbolic-fairness discipline
- move from path-local accumulation to loop-closure consistency
- require the witness to model whether relational effects close coherently over a short cycle rather than along a one-way path

## Family Requirements
- no latent ids in emitted text
- no exact microstate keys in emitted text
- no hidden tuple lookup shortcuts
- coarse loop-state nullness by construction
- within-state latent variation by construction
- balanced token views across loop positions
- bounded symbolic family must be declared before implementation approval

## Why This Is Materially Different
- the standing benchmark is transition-local
- the first transfer family is path-local
- the second transfer family is cycle-local and closure-sensitive
- this tests whether witness advantage survives a relational topology change, not just longer composition on the same topology
