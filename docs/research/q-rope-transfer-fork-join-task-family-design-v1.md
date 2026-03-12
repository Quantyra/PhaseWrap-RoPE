# Q-RoPE Transfer Fork-Join Task Family Design v1

Date: 2026-03-12
Stories: S909

## Goal
Open a third materially different transfer family that tests whether the standing witness advantage survives a branched relational topology rather than a simple path or loop topology.

## Why Fork-Join
The current transfer evidence covers:
- path-local composition
- loop-closure composition

The next materially different topology should require:
- one source state branching into two relational channels
- one downstream rejoin operation that depends on the relative behavior of both channels

That is stricter than a path and structurally different from a loop.

## Design Principle
The target should depend on relational consistency across the two branched channels and their downstream reconciliation, while remaining resistant to a bounded symbolic family over declared fork-join summaries.

## Planned Line
- task family:
  - `fork_join`
- first exact task:
  - `synthetic_symbolic_insufficiency_fork_join_response`
- witness candidate:
  - `V_future_relational_witness_symbolic_insufficiency_fork_join`
- bounded control family:
  - fork-join additive and bounded-quadratic regressor over declared fork-join summaries only
