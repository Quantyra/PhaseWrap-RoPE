# Q-RoPE Symbolic Insufficiency Dual-Atlas Family v1

Date: 2026-03-11
Stories: S722

## Purpose
Define one materially stronger symbolic family than the residual-atlas control without allowing hidden lookup structure.

## Family Definition
- base family remains fixed:
  - coarse transition indicators
  - first-order analog summaries
  - pairwise cross-direction summaries
  - exactly 4 global source-chart indicators
  - exactly 4 global destination-chart indicators
  - bounded source-chart x analog interactions
  - bounded destination-chart x analog interactions
- stronger extension:
  - one globally shared dual-atlas coupling family between source-chart and destination-chart views
  - coupling is only over the same frozen 4x4 chart lattice
  - coupling features may only use declared analog summaries:
    - `sector_magnitude_delta`
    - `ordered_content_delta`
    - `orientation_delta`

## Allowed Additional Basis
- `source_chart_ij` and `dest_chart_kl` indicators over the frozen 4-chart atlas
- one bounded coupling family:
  - `(source_chart,dest_chart)` indicator x declared analog summary
- no free per-cell regressors beyond those coupling interactions

## Forbidden Additions
- latent path ids
- exact microstate keys
- hidden tuple lookups
- per-example chart refinement
- chart count growth beyond 4
- uncontrolled lattice growth after packet inspection
- unrestricted higher-order spline or kernel basis

## Rationale
- the residual-atlas family stayed materially weaker than the witness
- the next fairer symbolic challenge is not more residual width on one atlas
- it is one globally shared coupling over a frozen source-destination atlas pair
- this is materially stronger while still auditable
