# Q-RoPE Parity-Default Local Packet v1

## Scope
This step reran the local `V3` vs `V4` packet with `parity` as the default screening readout and compared it against the existing `weighted` reference packet.

Backend:
- `sim_quantum_statevector`

Credit status:
- `0` additional Quandela credits consumed

Run IDs:
- parity-default packet: `paritypkt-*`
- weighted reference: `obs-weighted-*`

## Packet
Variants:
- `V3`
- `V4`

Datasets:
- `yelp`
- `imdb`
- `amazon`

Seeds:
- `42`
- `123`
- `777`
- `2024`
- `9001`

## Result
### Yelp
`V3`
- weighted: mean acc `0.6250`, mean F1 `0.4467`
- parity: mean acc `0.6000`, mean F1 `0.5665`

`V4`
- weighted: mean acc `0.5750`, mean F1 `0.3976`
- parity: mean acc `0.5500`, mean F1 `0.4922`

### IMDb
`V3`
- weighted: mean acc `0.5250`, std acc `0.2151`, mean F1 `0.3721`
- parity: mean acc `0.4750`, std acc `0.1458`, mean F1 `0.4632`

`V4`
- weighted: mean acc `0.5250`, std acc `0.2151`, mean F1 `0.3721`
- parity: mean acc `0.5000`, std acc `0.1118`, mean F1 `0.4982`

### Amazon
`V3`
- weighted: mean acc `0.5500`, mean F1 `0.6542`
- parity: mean acc `0.4750`, mean F1 `0.3834`

`V4`
- weighted: mean acc `0.5000`, mean F1 `0.5600`
- parity: mean acc `0.5500`, mean F1 `0.5733`

## Interpretation
The parity-default packet confirmed the original promotion evidence rather than changing it.

What parity does well:
- improves local F1 signal on `yelp`
- improves local F1 signal and stability on `imdb`
- improves the `V4` readout on `amazon`

What parity does not solve:
- it is still materially worse than weighted for `V3` on `amazon`

So the correct interpretation is:
- parity is good enough to remain the default screening path
- but weighted is still needed as a shadow reference for important branch decisions

## Decision
- Keep `parity` as the provisional default local screening readout
- Keep `weighted` as a required reference comparator for major local branch decisions

## Next local path
Use parity by default in future local packets, but require weighted shadow comparison when:
- a branch decision changes materially
- `amazon` evidence is central to the decision
- a result would materially affect whether a future mechanism-level branch is opened

## Bottom line
The parity-default rerun validated the promotion, but not strongly enough to retire weighted as a reference baseline.
