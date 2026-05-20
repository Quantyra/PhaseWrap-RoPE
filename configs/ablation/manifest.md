# Ablation Config Manifest

## Purpose
Single reference for the first PhaseWrap-RoPE ablation batch config files.

## Files
- `configs/ablation/base.yaml`
- `configs/ablation/V0.yaml`
- `configs/ablation/V1.yaml`
- `configs/ablation/V2.yaml`
- `configs/ablation/V3.yaml`
- `configs/ablation/V4.yaml`
- `configs/ablation/V4b.yaml`

## Variant map
- `V0`: no positional encoding
- `V1`: additive sinusoidal encoding
- `V2`: fixed-gate quantum positional encoding
- `V3`: PhaseWrap-RoPE relative-phase encoding
- `V4`: damped-and-clipped PhaseWrap-RoPE relative-phase encoding
- `V4b`: clipped ratio-controlled PhaseWrap-RoPE relative-phase encoding

## Execution reference
Use `docs/research/q-rope-ablation-runbook-v1.md` for canonical run commands and logging requirements.
