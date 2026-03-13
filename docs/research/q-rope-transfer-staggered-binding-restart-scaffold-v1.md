# Q-RoPE Transfer Staggered Binding Restart Scaffold v1

Date: 2026-03-13
Stories: S1015

## Candidate
- Witness: `V_future_relational_witness_symbolic_insufficiency_staggered_binding`

## First Bounded Control
- `staggered-binding` additive and bounded-quadratic regressor over declared source/stage/bind summaries only

## Allowed Symbolic Basis
- coarse staged-state indicators
- declared source-to-stage analog summaries
- declared stage-to-stage analog summaries
- declared stage-to-bind analog summaries
- one bounded quadratic layer over those declared summaries only

## Forbidden Family
- latent staged-state ids
- exact microstate keys
- hidden stage tuple lookups
- uncontrolled basis growth

## Fixed First Packet
- backend: `sim_quantum_statevector`
- seeds: `42`, `123`, `777`
- metrics: `mae`, `rank_correlation`
