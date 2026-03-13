# Q-RoPE Transfer Echo-Resolution Task Family Design v1

## Objective
Define a materially different transfer family that tests whether the witness can preserve relational signal through a delayed echo phase followed by a later resolution phase.

## Candidate Task
- `synthetic_symbolic_insufficiency_echo_resolution_response`

## Structural Shape
- `source -> echo -> echo -> resolve`
- Early source information is repeated in a lossy echo stage.
- The target depends on whether the later resolution aligns with the latent echo-consistent relation, not on any one local summary alone.

## Why This Is Different
- Not `path`: longer delayed recurrence with repeated intermediate stage.
- Not `loop-closure`: no return-to-origin closure objective.
- Not `fork-join`: no branch split/rejoin symmetry.
- Not `relay-binding`: not a single relay-mediated bind.
- Not `cascade-reconciliation`: not divergence followed by reconciliation.
- Not `braid` or `staggered-binding`: no crossing-style branch weave or staged bind chain.

## Expected Difficulty for Bounded Symbolic Control
A bounded additive/quadratic control over declared source/echo/resolve summaries should have difficulty if the task is built so that:
- coarse echo-state lookup is near-null,
- within-state variation remains high,
- latent echo-consistency determines the final target,
- shallow local summaries cannot fully reconstruct the delayed relation.
