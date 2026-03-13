# Q-RoPE Transfer Latch-Switch Task Family Design v1

Date: 2026-03-12
Stories: S1003

## BLUF
Proposed next transfer family: `latch-switch`.

## Core Idea
The target should depend on whether an early latent relay state is latched, then selectively switched by a later context before final readout. This is structurally different from:
- `path`: pure accumulation
- `loop-closure`: closure over a path
- `fork-join`: branch/rejoin composition
- `relay-binding`: delayed bind through an intermediate relay
- `braid`: crossing structure that collapsed under deeper reindexing

## Why This Is A Reasonable Next Candidate
### 1. Delayed relational dependence is essential
The task is not solvable from a local comparison alone. The final target depends on whether a retained latent state survives a later switch condition.

### 2. Intermediate state must persist
The early latch state must remain available when the later switch event occurs. That makes retained latent-conditioned state central rather than decorative.

### 3. It is not obviously another braid
The main risk with `braid` was deeper reindex compression into a compact symbolic recovery path. `latch-switch` is different because the crucial structure is not crossing order itself, but conditional persistence of a latent state through a later gate.

## Planned Internal Target Shape
- phase 1: establish a latent latch state from an early relational event
- phase 2: apply a later switch condition that either preserves or flips the contribution of the latched state
- phase 3: compute the final response from the interaction of latched state and switch outcome

## Intended Screening Question
Can a bounded symbolic summary of declared latch and switch features recover the final response, or does the witness still need latent-conditioned state persistence to stay ahead?
