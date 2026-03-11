# Q-RoPE Symbolic Insufficiency Dual-Atlas Transition-Bilinear Family v1

Date: 2026-03-11
Stories: S762

## Purpose
Define one materially stronger symbolic family beyond the dual-atlas transition-residual control while preserving auditability and preventing hidden lookup behavior.

## Family Definition
- base family remains fixed:
  - coarse transition indicators
  - first-order analog summaries
  - pairwise cross-direction summaries
  - exactly 4 global source-chart indicators
  - exactly 4 global destination-chart indicators
  - one frozen 4x4 source-destination coupling lattice
  - lattice-cell x declared analog summary interactions
  - one bounded residual-gating family:
    - `orientation_minus_content`
    - `orientation_plus_content`
  - one bounded bilinear residual family:
    - `sector_times_orientation_minus_content`
    - `sector_times_orientation_plus_content`
  - one bounded directional transition-residual family:
    - `source_to_dest_orientation_minus_content`
    - `dest_to_source_orientation_minus_content`
- stronger extension:
  - one bounded directional transition-bilinear family over the same frozen 4x4 lattice
  - each lattice cell may gate exactly two transition-bilinear channels:
    - `source_to_dest_sector_times_orientation_minus_content`
    - `dest_to_source_sector_times_orientation_minus_content`

## Allowed Additional Basis
- `cell_ij_kl` indicators over the frozen 4x4 lattice
- for each lattice cell, exactly these transition-bilinear features:
  - `cell_ij_kl_source_to_dest_sector_times_orientation_minus_content`
  - `cell_ij_kl_dest_to_source_sector_times_orientation_minus_content`
- no additional cell-wise feature types are allowed

## Frozen Transition-Bilinear Definitions
- `orientation_minus_content = orientation_delta - ordered_content_delta`
- `sector_times_orientation_minus_content = sector_magnitude_delta * orientation_minus_content`
- `source_sign = +1` iff source chart is in `{10,11}`, else `-1`
- `dest_sign = +1` iff destination chart is in `{10,11}`, else `-1`
- `source_to_dest_sector_times_orientation_minus_content = source_sign * sector_times_orientation_minus_content`
- `dest_to_source_sector_times_orientation_minus_content = dest_sign * sector_times_orientation_minus_content`
- all must be derived only from declared analog summaries and frozen chart identities already allowed in the symbolic-insufficiency line

## Forbidden Additions
- latent path ids
- exact microstate keys
- hidden tuple lookups
- per-example chart refinement
- chart count growth beyond `4`
- lattice growth beyond `4 x 4`
- per-cell bespoke nonlinear transforms
- unrestricted higher-order basis growth after packet inspection
- any directional transition-bilinear feature beyond the two frozen definitions

## Rationale
- the dual-atlas transition-residual family stayed materially weaker than the witness
- the next fairer symbolic challenge is not a larger lattice or more charts
- it is one narrowly bounded directional transition-bilinear layer over the same frozen lattice
- this is materially stronger than plain transition-residual gating while still auditable and mechanically frozen
