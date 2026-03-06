# Q-RoPE Phase-to-Score Coupling Path Analysis v1

## Scope
This note analyzes where score dynamic range is lost in the local screening circuit.

Backend:
- `sim_quantum_statevector`

Credit status:
- `0` additional Quandela credits consumed

Diagnostic artifacts:
- `logs/diagnostics/phase_to_score_coupling_trace.json`
- `logs/diagnostics/phase_to_score_token_stage_deltas.json`

## Coupling path under inspection
Current local screening circuit:
1. per-qubit feature `RY`
2. per-qubit positional `RZ`
3. forward nearest-neighbor `CNOT` chain
4. global `RX(pi/4)` mixing layer
5. reverse `CNOT` chain
6. weighted mean-excitation readout

## Structural finding
`RZ` does not move the weighted-excitation observable directly.

Observed from the stage traces:
- `after_ry` and `after_rz` have identical mean excitation
- the phase information only becomes visible to the score after the global `RX` mixing layer

That means the effective phase-to-score coupling path is:
`RZ phase -> RX mixing -> reverse entangling -> weighted-excitation readout`

## Stage-delta result
Average absolute token-removal deltas:

### Yelp
- `V3`
  - `after_ry`: `0.2346`
  - `after_rx_mix`: `0.1556`
  - `final`: `0.0884`
- `V4`
  - `after_ry`: `0.2346`
  - `after_rx_mix`: `0.1449`
  - `final`: `0.0701`

### IMDb
- `V3`
  - `after_ry`: `0.2304`
  - `after_rx_mix`: `0.1387`
  - `final`: `0.0744`
- `V4`
  - `after_ry`: `0.2304`
  - `after_rx_mix`: `0.1298`
  - `final`: `0.0610`

### Amazon
- `V3`
  - `after_ry`: `0.2285`
  - `after_rx_mix`: `0.1380`
  - `final`: `0.0735`
- `V4`
  - `after_ry`: `0.2285`
  - `after_rx_mix`: `0.1274`
  - `final`: `0.0583`

## Interpretation
The attenuation pattern is consistent:
1. `V3` and `V4` are identical through:
   - feature loading
   - `RZ`
   - forward entangling
2. the first variant-sensitive divergence appears at the global `RX` mixing stage
3. the final weighted-excitation readout compresses dynamic range further for both variants
4. `V4` compresses the post-mixing signal more than `V3`

So the main source of lost discriminative dynamic range is not:
- token hashing
- feature loading
- threshold calibration

It is the combination of:
- weaker phase injection in `V4`
- a single fixed global mixing layer
- a compressive weighted-excitation observable

## Decision framework
### When is a new mechanism-level variant justified?
A future mechanism-level variant becomes justified if it explicitly targets one or both of:
1. stronger phase-to-amplitude conversion after `RZ`
2. a less compressive final observable than weighted mean excitation

### What is not justified now?
- more threshold tuning
- another `V4` local calibration pass
- a paid remote `V4` wave

## Recommended next zero-credit track
Stay local and inspect the readout path:
1. compare weighted mean excitation against alternative observables on the same local circuit
2. quantify whether the observable itself is the main compression bottleneck
3. only then decide whether the next future branch should be:
   - new observable
   - new mixing layer
   - or a genuinely new variant mechanism

## Bottom line
Dynamic range is being lost after phase injection, primarily across the `RX` mixing plus weighted-excitation readout path.
That is the real bottleneck to solve before another variant race or remote wave.
