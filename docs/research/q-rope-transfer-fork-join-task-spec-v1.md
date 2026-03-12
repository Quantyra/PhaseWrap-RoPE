# Q-RoPE Transfer Fork-Join Task Spec v1

Date: 2026-03-12
Stories: S910

## Task
`synthetic_symbolic_insufficiency_fork_join_response`

## Structure
Each sample contains:
- one source relational state
- two branch states derived from the source through distinct declared perturbation channels
- one rejoin state that depends on the relational interaction between the two branches

## Target Intent
The regression target should vary with:
- source-to-branch residual structure
- branch-to-branch reconciliation structure
- branch-to-rejoin residual structure

The target should not be reconstructable from:
- coarse fork state ids alone
- branch-local declared summaries alone
- a bounded additive/quadratic symbolic family over declared summaries only

## Required Generator Diagnostics
- `coarse_fork_state_null_pass`
- `within_fork_state_variation_pass`
- `latent_fork_diversity_pass`
- `branch_balance_pass`
- `rejoin_target_nontrivial_pass`
- `token_view_balance_pass`

## Packet
- backend:
  - `sim_quantum_statevector`
- seeds:
  - `42`, `123`, `777`
- metrics:
  - `mae`
  - `rank_correlation`
