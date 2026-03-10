# Q-RoPE Transition Orbit Pairwise Order Task Spec v1

Date: 2026-03-11
Story: S365

## Task ID
`synthetic_transition_orbit_pairwise_order_binary`

## Goal
Measure whether the witness captures within-state ordinal ordering better than bounded symbolic controls when absolute target magnitude is removed from the task.

## Construction
- Start from the same orbit-canonical dual-sample family used in the stopped rank-band branch.
- Restrict pair formation to samples that share the same coarse orbit-transition state.
- For each coarse state, form ordered comparison pairs `(u, v)`.
- Define the latent order score with the same hidden quantity previously used to rank bands:
  - `orbit_transition_band_delta(u)`
  - `orbit_transition_band_delta(v)`
- Label rule:
  - `1` iff `orbit_transition_band_delta(u) > orbit_transition_band_delta(v)`
  - `0` otherwise

## Required Properties
- coarse transition state must be identical on both sides of the comparison pair
- token identity remains nuisance-only
- absolute scalar target values are not supervised directly
- a coarse-state lookup alone should be near-null by construction because labels vary inside the same coarse state

## Intended Advantage
This task preserves the only signal that survived the stopped rank-band branch:
- stronger witness ordering structure

while removing the exact failure mode that killed that branch:
- magnitude-regression leadership by bounded symbolic controls

## Bounded Shortcut Families To Defeat
- coarse state order lookup
- cross-direction additive order regressor
- quadratic within-state order regressor
- orbit-permuted transition-family order regressor
