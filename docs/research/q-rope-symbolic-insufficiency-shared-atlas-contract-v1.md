# Q-RoPE Symbolic Insufficiency Shared-Atlas Contract v1

Date: 2026-03-10
Stories: S702

## Goal
Turn the shared-atlas symbolic family into a concrete memo-level contract that can be audited before any implementation approval.

## Fixed Chart Count
- exactly `4` global charts

## Fixed Chart Construction Rule
- charts are derived only from declared analog summaries:
  - `sector_magnitude_delta`
  - `ordered_content_delta`
  - `orientation_delta`
- chart assignment is determined by two fixed binary thresholds:
  - `sector_magnitude_delta >= 0`
  - `ordered_content_delta >= 0`
- `orientation_delta` may affect regression features inside a chart but may not define new charts

## Allowed Shared-Atlas Feature Family
- declared coarse transition indicators
- declared first-order analog summaries
- declared pairwise cross-direction summaries
- one-hot chart indicators for the 4 fixed global charts
- one bounded chart-indicator times analog interaction family using only declared analog summaries

## Explicitly Forbidden
- chart definitions learned from latent structure
- chart counts greater than `4`
- chart definitions that use hidden tuple ids or microstate keys
- chart-specific free parameters that activate only for hidden latent groups
- spline, kernel, or arbitrary partition growth beyond the 4-chart rule

## Fairness Rule
- if the charting cannot be written down before execution, the review is invalid
- if the same chart rule is not reused for every seed and every sample, the review is invalid
