# Q-RoPE Transfer Path Symbolic Family v1

Date: 2026-03-11
Stories: S849

## Purpose
Freeze the first bounded symbolic fairness family for the transfer-path line before any approval-candidate review.

## Allowed Symbolic Basis
- coarse path-state indicators only
- first-order single-step analog summaries only
- first-order path-aggregated analog summaries only
- one bounded quadratic layer over declared path analog summaries only

## Explicitly Allowed Path Features
- per-step `sector_magnitude_delta`
- per-step `ordered_content_delta`
- per-step `orientation_delta`
- bounded path aggregates:
  - mean
  - signed sum
  - max absolute value
  - adjacent-step difference summary
- no higher-order path basis beyond one frozen quadratic layer over the declared aggregates

## Forbidden Feature Family
- latent path-state ids
- exact microstate keys
- hidden tuple lookups
- full path lookup tables
- unrestricted recurrent/state-machine features
- uncontrolled higher-order path basis growth after packet inspection

## Reason
This keeps the transfer line comparable to the current symbolic-insufficiency benchmark while materially changing the task from transition-local to path-local.
