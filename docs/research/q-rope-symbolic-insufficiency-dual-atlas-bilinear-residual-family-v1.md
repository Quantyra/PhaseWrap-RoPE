# Q-RoPE Symbolic Insufficiency Dual-Atlas Bilinear Residual Family v1

Date: 2026-03-11
Stories: S742

## Purpose
Define one materially stronger symbolic family than the dual-atlas residual-gating control while preserving full auditability and preventing hidden lookup behavior.

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
- stronger extension:
  - one bounded bilinear residual family over the same frozen 4x4 lattice
  - each lattice cell may gate exactly two bilinear residual channels:
    - `sector_times_orientation_minus_content`
    - `sector_times_orientation_plus_content`

## Allowed Additional Basis
- `cell_ij_kl` indicators over the frozen 4x4 lattice
- for each lattice cell, exactly these bilinear residual features:
  - `cell_ij_kl_sector_times_orientation_minus_content`
  - `cell_ij_kl_sector_times_orientation_plus_content`
- no additional cell-wise basis terms are allowed

## Frozen Bilinear Residual Definitions
- `orientation_minus_content = orientation_delta - ordered_content_delta`
- `orientation_plus_content = orientation_delta + ordered_content_delta`
- `sector_times_orientation_minus_content = sector_magnitude_delta * orientation_minus_content`
- `sector_times_orientation_plus_content = sector_magnitude_delta * orientation_plus_content`
- all must be derived only from declared analog summaries already allowed in the symbolic-insufficiency line

## Forbidden Additions
- latent path ids
- exact microstate keys
- hidden tuple lookups
- per-example chart refinement
- chart count growth beyond `4`
- lattice growth beyond `4 x 4`
- per-cell bespoke nonlinear transforms
- unrestricted higher-order basis growth after packet inspection

## Rationale
- the dual-atlas residual-gating family stayed materially weaker than the witness
- the next fairer symbolic challenge is not a larger lattice or more residual channels
- it is one narrowly bounded bilinear residual layer over the same frozen lattice
- this is materially stronger than plain residual gating while still auditable and mechanically frozen
