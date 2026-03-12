# Q-RoPE Executive Summary v1

Date: 2026-03-11
Stories: S876

## BLUF
Quantyra now has one credible internal positive result in the Q-RoPE program:
- the `symbolic-insufficiency` witness branch beat the frozen symbolic-family ladder on the standing benchmark
- and it survived one bounded transfer cycle on a materially different path-local task

This is enough to preserve as an internal benchmark and research reference.
It is not enough for hardware execution, publication, or product claims.

## What Held Up
- standing benchmark:
  - `V_future_relational_witness_symbolic_insufficiency`
  - mean `mae = 0.119724`
  - mean `rank_correlation = 0.967399`
- bounded transfer result:
  - `V_future_relational_witness_symbolic_insufficiency_path`
  - base means `mae = 0.100666`, `rank_correlation = 0.501251`
  - first hardening cycle cleared:
    - `token_permutation = cdab`
    - `pair_reindex = 1`
    - `slot_swap = 1`
    - `pair_reindex = 7`

## Why This Matters
- The program is no longer in the state where every branch collapses immediately under bounded symbolic controls.
- The current witness result survived a long fairness ladder and one transfer-family hardening cycle.
- That makes it a defensible internal mechanism result.

## What It Does Not Mean
- not a NISQ advantage claim
- not a hardware-readiness claim
- not an external/publication-ready superiority claim
- not broad generalization beyond the current benchmark plus one transfer family

## Recommended Decision
- preserve this as the standing internal benchmark
- do not default into more same-family fairness escalation
- only open new execution if there is either:
  - a materially different second transfer family, or
  - a theory-backed reason to test hardware later
