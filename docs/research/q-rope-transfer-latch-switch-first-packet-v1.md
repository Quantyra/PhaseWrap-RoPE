# Q-RoPE Transfer Latch-Switch First Packet v1

## Packet
- Witness runs:
  - `latchswitch-witness-s42`
  - `latchswitch-witness-s123`
  - `latchswitch-witness-s777`
- Control runs:
  - `latchswitch-control-s42`
  - `latchswitch-control-s123`
  - `latchswitch-control-s777`

## Mean Results
- Witness:
  - `mae = 0.083242`
  - `rank_correlation = 0.178431`
  - `calibration_slope = 0.065008`
- Control:
  - `mae = 0.082541`
  - `rank_correlation = 0.041177`
  - `calibration_slope = 0.040224`

## Interpretation
- The witness kept the stronger rank structure.
- The control kept the better primary `mae`.
- Under the declared two-metric gate, this is mixed leadership rather than a keep decision.

## Artifacts
- Summary CSV: `logs/ablation_runs/summary/transfer_latchswitch_v1.csv`
- Witness metrics:
  - `logs/ablation_runs/latchswitch-witness-s42/metrics.json`
  - `logs/ablation_runs/latchswitch-witness-s123/metrics.json`
  - `logs/ablation_runs/latchswitch-witness-s777/metrics.json`
- Control metrics:
  - `logs/ablation_runs/latchswitch-control-s42/metrics.json`
  - `logs/ablation_runs/latchswitch-control-s123/metrics.json`
  - `logs/ablation_runs/latchswitch-control-s777/metrics.json`
