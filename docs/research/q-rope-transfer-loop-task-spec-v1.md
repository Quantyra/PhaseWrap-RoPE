# Q-RoPE Transfer Loop-Closure Task Spec v1

Date: 2026-03-11
Stories: S878

## Task
- `synthetic_symbolic_insufficiency_loop_closure_response`

## Goal
Test whether the standing symbolic-insufficiency witness transfers from transition-local and path-local response prediction to short loop-closure response under the same bounded symbolic fairness discipline.

## Loop Structure
- each sample contains a short ordered cycle of linked relational steps
- target depends on closure consistency across the full loop, not any single edge response
- token identity remains a nuisance variable rather than a direct shortcut

## Required Construction Rules
- no latent ids in emitted text
- no exact microstate keys in emitted text
- no hidden tuple lookup shortcuts
- coarse loop-state nullness by construction
- within-state latent variation by construction
- balanced token views across loop positions
- bounded path-length and loop-size balance

## Preliminary Target Shape
- continuous response target
- derived from loop-closure mismatch or coherence across the ordered cycle
- not reducible to any one transition-local response or one-way path aggregate

## Required Generator Diagnostics
- `coarse_loop_state_null_pass`
- `within_loop_state_variation_pass`
- `latent_loop_diversity_pass`
- `token_view_balance_pass`
- `loop_length_balance_pass`
- `closure_target_nontrivial_pass`
