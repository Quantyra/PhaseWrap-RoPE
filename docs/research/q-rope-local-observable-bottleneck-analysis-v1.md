# Q-RoPE Local Observable Bottleneck Analysis v1

## Scope
This note compares the current weighted-excitation readout against alternative observables on the same final local circuit state.

Backend:
- `sim_quantum_statevector`

Credit status:
- `0` additional Quandela credits consumed

Diagnostic artifact:
- `logs/diagnostics/observable_bottleneck_compare.json`

## Observables compared
- `weighted`: weighted mean excitation
- `q0`, `q1`, `q2`: single-qubit excitation probabilities
- `parity`: even-vs-odd population parity mapped to `[0, 1]`
- `topheavy`: probability mass on basis states with Hamming weight `>= 2`

Metrics:
- score standard deviation
- class-mean gap
- score range

## Aggregate result
### Yelp
For both `V3` and `V4`:
- `weighted` is the most compressive observable among the candidates
- `q2` and `parity` have materially larger score spread and range
- class gaps remain small for all observables

Representative `V3` values:
- `weighted`: std `0.0773`, gap `-0.0020`, range `0.3693`
- `q2`: std `0.1500`, gap `0.0112`, range `0.6497`
- `parity`: std `0.1561`, gap `-0.0155`, range `0.5585`

### IMDb
The same structure holds:
- `weighted` is more compressive than `q2` or `parity`
- richer observables expand dynamic range
- class gaps are still near zero

Representative `V3` values:
- `weighted`: std `0.0658`, gap `-0.0096`, range `0.3371`
- `q2`: std `0.1483`, gap `-0.0143`, range `0.6620`
- `parity`: std `0.1547`, gap `0.0008`, range `0.5698`

### Amazon
Again:
- `weighted` is the most compressive readout
- alternatives increase spread
- discrimination remains weak

Representative `V3` values:
- `weighted`: std `0.0632`, gap `-0.0056`, range `0.3050`
- `q0`: std `0.1041`, gap `0.0134`, range `0.3998`
- `q2`: std `0.1310`, gap `-0.0201`, range `0.6492`

## Interpretation
Two things are true at once:

1. The current weighted-excitation observable is a real compression bottleneck.
2. It is not the only bottleneck.

Why:
- replacing the observable with `q2` or `parity` increases dynamic range substantially
- but those alternatives still do not generate a decisive class-mean separation

So the current local screening problem is not:
- observable only

It is:
- a compressive observable
- plus a circuit/state structure that does not produce strong class separation even under less compressive readouts

## Decision framework
### Should a future branch target observable design?
`Yes`, potentially.

Observable redesign is justified because the current weighted-excitation readout clearly compresses the signal more than alternatives.

### Should a future branch target only observable design?
`No`

That would be too narrow because richer observables still do not create strong class gaps by themselves.

### What is the right implication?
If a future mechanism-level branch is opened, it should consider:
- observable redesign
- and stronger post-phase mixing / state separation together

## Next zero-credit local track
Stay local and identify whether a richer observable improves token sensitivity and class separation enough to justify a local screening-path redesign.

The most relevant candidates to inspect next are:
1. `q2`
2. `parity`

## Bottom line
Weighted mean excitation is indeed a compression bottleneck.
But the deeper issue is broader: the local circuit also fails to produce strong class separation under less compressive observables.
