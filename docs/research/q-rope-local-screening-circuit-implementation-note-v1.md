# Q-RoPE Local Screening Circuit Implementation Note v1

## Scope completed
- Implemented the redesigned local screening circuit in [qsim.py](C:/Users/Dan/Desktop/Projects/QuantyraQRope/src/qrope/qsim.py)
- Added a post-phase global `RX(pi/4)` mixing layer
- Added a reverse CNOT chain
- Replaced single-qubit readout with weighted mean excitation across all qubits

## What changed
Old local screening path:
- feature `RY`
- positional `RZ`
- forward CNOT chain
- score from `P(qubit_0 = 1)`

New local screening path:
- feature `RY`
- positional `RZ`
- forward CNOT chain
- global `RX(pi/4)` mixing layer
- reverse CNOT chain
- score from all-qubit weighted mean excitation

## Validation
- Focused tests passed: `30 passed`
- Local smoke run succeeded:
  - [v4b-yelp-screening-s42/metrics.json](C:/Users/Dan/Desktop/Projects/QuantyraQRope/logs/ablation_runs/v4b-yelp-screening-s42/metrics.json)

## Next step
- Rerun the deterministic `V3` vs `V4` vs `V4b` packet on the upgraded local screening gate
- Check whether the local gate is now discriminative
