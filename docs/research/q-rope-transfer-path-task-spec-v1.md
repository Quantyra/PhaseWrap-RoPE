# Q-RoPE Transfer Path Task Spec v1

Date: 2026-03-11
Stories: S848

## Task
- `synthetic_symbolic_insufficiency_path_response`

## Goal
Test whether the standing symbolic-insufficiency witness transfers from one-step transition response to short relational path response under the same bounded symbolic fairness discipline.

## Path Structure
- each sample contains a short ordered path of linked relational steps
- target depends on path-level composition, not any single transition-local response
- the path must preserve token identity as a nuisance variable rather than a direct shortcut

## Required Construction Rules
- no latent ids in emitted text
- no exact microstate keys in emitted text
- no hidden tuple lookup shortcuts
- coarse path-state nullness by construction
- within-state latent variation by construction
- balanced token views across source and destination roles

## Preliminary Target Shape
- continuous response target
- derived from composed path-level relational effects across multiple linked steps
- not reducible to a single transition-local target reused over the path

## Required Generator Diagnostics
- `coarse_path_state_null_pass`
- `within_path_state_variation_pass`
- `latent_path_diversity_pass`
- `token_view_balance_pass`
- `path_length_balance_pass`
