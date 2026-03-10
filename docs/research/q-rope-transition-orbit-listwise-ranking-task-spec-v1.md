# Q-RoPE Transition Orbit Listwise Ranking Task Spec v1

Date: 2026-03-11
Story: S374

## Task ID
`synthetic_transition_orbit_listwise_ranking`

## Goal
Test whether the witness preserves within-state transition-orbit ordering better than bounded symbolic baselines when the model must rank a small candidate set instead of solving one binary comparison at a time.

## Construction
- Start from the same orbit-canonical dual-sample family used by the stopped pairwise-order branch.
- Partition rows by the same coarse orbit-transition state.
- For each coarse state, build fixed candidate lists of size `4`.
- Use the latent quantity `orbit_transition_band_delta` to define the hidden total order inside each list.
- Supervision target:
  - the ordered permutation of the four candidates from lowest to highest latent score
  - or an equivalent normalized rank vector over the same four candidates

## Required Properties
- every list contains only candidates from the same coarse orbit-transition state
- each list has non-degenerate internal order
- token identity remains nuisance-only
- coarse-state lookup alone should be near-null because the target varies entirely inside the same coarse state

## Shortcut Families To Defeat
- coarse state ranking lookup
- additive cross-direction ranking baseline
- quadratic ranking baseline
- orbit-permuted ranking baseline

## Branch Intent
This task preserves the only remaining signal from the stopped pairwise-order branch:
- ordering may still be represented better than decision-threshold classification

without reusing the failed pairwise binary framing.
