# Q-RoPE Symbolic Insufficiency Standing Benchmark Memo v2

Date: 2026-03-11
Stories: S842

## Standing Internal Benchmark
- witness: `V_future_relational_witness_symbolic_insufficiency`
- task: `synthetic_symbolic_insufficiency_transition_response`
- benchmark packet metrics:
  - `mae`
  - `rank_correlation`

## Current Status
- the witness remains ahead of all bounded symbolic families implemented through:
  - stronger symbolic basis v2
  - shared-atlas
  - residual-atlas
  - dual-atlas
  - dual-atlas residual
  - dual-atlas bilinear
  - dual-atlas transition residual
  - dual-atlas transition bilinear
  - dual-atlas transition bilinear-plus
  - dual-atlas transition cubic
  - dual-atlas transition cubic-plus
  - dual-atlas transition quartic
  - dual-atlas transition quartic-plus
  - dual-atlas transition quintic
  - dual-atlas transition quintic-plus

## Use
- treat this witness result as the standing internal benchmark for any future fairness review on this line
- do not reopen code unless a materially stronger symbolic family is defined and gated first
