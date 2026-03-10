# Q-RoPE Transition Orbit Channel-Order Post Deeper Pair-Reindex Decision v1

Date: 2026-03-10
Stories: S468

## Decision
- keep the branch active
- stop using pair-reindex escalation as the next hardening family on this task

## Why
- both `pair_reindex=1` and `pair_reindex=7` were valid but inert at the branch level
- repeated reindexing is no longer a useful pressure test on this generator
- the next bounded perturbation should change the branch through a different axis

## Consequence
- keep the task and retained control family fixed
- move to `slot_swap=1` as the next bounded hardening step
