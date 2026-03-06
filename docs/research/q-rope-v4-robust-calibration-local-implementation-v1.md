# Q-RoPE V4 Robust Calibration Local Implementation v1

## Scope
This step implemented the fixed robust local calibration rule defined in `S054` and reran the local `V3` vs `V4` packet on the variant-sensitive local statevector backend.

Backend:
- `sim_quantum_statevector`

Credit status:
- `0` additional Quandela credits consumed

## Implemented rule
The local quantum runner now uses:
1. a deterministic stratified split of the train partition into:
   - subtrain
   - validation
2. threshold selection on the validation subset only
3. deterministic threshold ranking with:
   - primary objective: macro-F1
   - secondary objective: balanced accuracy
   - tertiary tie-break: lower predicted-positive-rate drift from the validation label prior
   - final tie-break: smaller distance from the validation score mean

This rule is applied consistently in the local statevector screening backend so `V3` and `V4` are evaluated under the same calibration protocol.

## Zero-credit rerun packet
Rerun IDs:
- `robustcal-v3-*`
- `robustcal-v4-*`

Packet:
- datasets: `yelp`, `imdb`, `amazon`
- seeds: `42`, `123`, `777`, `2024`, `9001`
- variants: `V3`, `V4`
- backend: `sim_quantum_statevector`

## Aggregate result
### Yelp
- `V3`: mean accuracy `0.6250`, std `0.1118`, mean F1 `0.4467`
- `V4`: mean accuracy `0.5750`, std `0.1000`, mean F1 `0.3976`

### IMDb
- `V3`: mean accuracy `0.5250`, std `0.2151`, mean F1 `0.3721`
- `V4`: mean accuracy `0.5250`, std `0.2151`, mean F1 `0.3721`

### Amazon
- `V3`: mean accuracy `0.5500`, std `0.1696`, mean F1 `0.6542`
- `V4`: mean accuracy `0.5000`, std `0.1581`, mean F1 `0.5600`

## Interpretation
The robust validation-based calibration rule removed the earlier signal that `V4` was uniquely worse than `V3` on `imdb`.

But the stronger conclusion is not that `V4` wins. The stronger conclusion is:
- the prior `imdb` blocker was at least partly calibration-induced
- under a fixed robust calibration rule, `V4` does not show a clean cross-dataset advantage over `V3`
- `V4` still does not justify a new remote execution wave

Under this rule:
- `imdb` becomes effectively tied between `V3` and `V4`
- `yelp` shifts modestly toward `V3`
- `amazon` shifts clearly toward `V3`

## Decision
- `NO-GO` for a paid remote `V4` wave
- `HOLD` on promoting `V4` as the active superior variant
- next correct step: reassess whether `V4` stays active, or whether the protocol should return to `V3` as the primary reference while treating `V4` as calibration-sensitive exploratory work

## Bottom line
The robust calibration protocol improved evaluation discipline and neutralized the strongest `imdb`-specific objection.
It did not produce a stronger empirical case for `V4`.
