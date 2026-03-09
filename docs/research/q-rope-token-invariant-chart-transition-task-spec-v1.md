# Token-invariant chart-transition task specification

## Task id
- `synthetic_chart_transition_token_invariant_response`

## Goal
Define a chart-transition residual task whose target depends only on transition geometry and not on token naming.

## Construction rules
- preserve the dual-observation chart-transition setting
- preserve ordered chart-transition families
- preserve the existing chart-transition analog factors
- randomize token identities independently of the target rule
- ensure the target is computed from chart-transition geometry only
- require token-permutation invariance in dataset diagnostics

## Required nuisance treatment
- token identities are nuisance variables by construction
- fixed token permutations must leave target values unchanged for the same underlying chart-transition state
- content labels may still exist for rendering, but they cannot enter the target rule or diagnostics pass criteria

## Fixed first evaluation posture
- local-only
- zero-credit
- seeds `42`, `123`, `777`
- witness vs bounded symbolic controls only

## Rejection rule
- reject the task immediately if target statistics change under a fixed token permutation on the same underlying latent chart-transition state
