# Q-RoPE Symbolic Insufficiency Dual-Atlas Transition-Bilinear-Plus First Packet v1

Date: 2026-03-11
Stories: S780

## Packet
- witness vs challenger
- dataset: `synthetic_symbolic_insufficiency_transition_response`
- backend: `sim_quantum_statevector`
- seeds:
  - `42`
  - `123`
  - `777`

## Means
- witness:
  - `mae = 0.119724`
  - `rank_correlation = 0.967399`
  - `calibration_slope = 0.000000`
- challenger:
  - `mae = 0.310545`
  - `rank_correlation = 0.173982`
  - `calibration_slope = 0.000000`

## Seed Detail
- witness:
  - `s42 -> mae 0.091881, rank_correlation 0.987491`
  - `s123 -> mae 0.140404, rank_correlation 0.950000`
  - `s777 -> mae 0.126887, rank_correlation 0.964706`
- challenger:
  - `s42 -> mae 0.317326, rank_correlation -0.063516`
  - `s123 -> mae 0.321861, rank_correlation 0.116434`
  - `s777 -> mae 0.292448, rank_correlation 0.469029`

## Artifact
- `logs/ablation_runs/summary/symbolic_insufficiency_dual_atlas_transition_bilinear_plus_v1.csv`
