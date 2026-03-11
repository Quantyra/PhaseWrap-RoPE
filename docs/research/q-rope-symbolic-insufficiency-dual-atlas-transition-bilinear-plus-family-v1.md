# Q-RoPE Symbolic Insufficiency Dual-Atlas Transition-Bilinear-Plus Family v1

Date: 2026-03-11
Stories: S772

## Purpose
Define one materially stronger symbolic family beyond the dual-atlas transition-bilinear control while preserving auditability and preventing hidden lookup behavior.

## Family Definition
- base family remains fixed through the dual-atlas transition-bilinear contract
- stronger extension:
  - one bounded directional transition-bilinear-plus family over the same frozen `4 x 4` lattice
  - each lattice cell may gate exactly two additional channels:
    - `source_to_dest_sector_times_orientation_plus_content`
    - `dest_to_source_sector_times_orientation_plus_content`

## Frozen Additional Definitions
- `orientation_plus_content = orientation_delta + ordered_content_delta`
- `sector_times_orientation_plus_content = sector_magnitude_delta * orientation_plus_content`
- `source_to_dest_sector_times_orientation_plus_content = source_sign * sector_times_orientation_plus_content`
- `dest_to_source_sector_times_orientation_plus_content = dest_sign * sector_times_orientation_plus_content`

## Forbidden Additions
- latent path ids
- exact microstate keys
- hidden tuple lookups
- per-example chart refinement
- chart count growth beyond `4`
- lattice growth beyond `4 x 4`
- per-cell bespoke nonlinear transforms
- any transition-bilinear-plus channel beyond the two frozen definitions
- uncontrolled basis growth after packet inspection
