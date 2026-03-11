# Q-RoPE Symbolic Insufficiency Dual-Atlas Transition-Cubic Family v1

Date: 2026-03-11
Stories: S782

## Objective
Define one materially stronger symbolic family beyond transition-bilinear-plus without permitting lookup behavior or uncontrolled basis growth.

## Frozen Lattice
- source atlas chart count fixed at `4`
- destination atlas chart count fixed at `4`
- coupling lattice fixed at `4 x 4`

## Frozen Prior Families Retained
- base dual-atlas coupling family
- residual family
- bilinear family
- transition-residual family
- transition-bilinear family
- transition-bilinear-plus family

## New Cubic Channels
- `source_to_dest_sector_times_orientation_times_content = source_sign * sector_magnitude_delta * orientation_delta * ordered_content_delta`
- `dest_to_source_sector_times_orientation_times_content = dest_sign * sector_magnitude_delta * orientation_delta * ordered_content_delta`

## Constraints
- no latent ids
- no hidden tuple lookup
- no chart growth beyond `4`
- no lattice growth beyond `4 x 4`
- no uncontrolled higher-order family beyond the two declared cubic channels
