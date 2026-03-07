# Q-RoPE Synthetic Score-vs-Offset Diagnostics v1

## Scope
- dataset: `synthetic_offset_binary`
- backend: `sim_quantum_statevector`
- readout: `parity`
- mixing preset: `mix_v0`
- variants:
  - `V0`
  - `V3`
- seeds:
  - `42`
  - `123`
  - `777`

Raw diagnostic artifact:
- [synthetic_v0_v3_score_vs_offset.json](\\?\C:\Users\Dan\Desktop\Projects\QuantyraQRope\logs\diagnostics\synthetic_v0_v3_score_vs_offset.json)

## Aggregate offset curves
`V0` mean score by offset:
- `-4`: `0.515432`
- `-3`: `0.490035`
- `-2`: `0.499679`
- `-1`: `0.466789`
- `+1`: `0.535958`
- `+2`: `0.470921`
- `+3`: `0.508243`
- `+4`: `0.530175`

`V3` mean score by offset:
- `-4`: `0.542445`
- `-3`: `0.514658`
- `-2`: `0.518067`
- `-1`: `0.496161`
- `+1`: `0.541134`
- `+2`: `0.497772`
- `+3`: `0.535381`
- `+4`: `0.554178`

## Key comparison
Aggregate positive-minus-negative mean score:
- `V0`: `0.018341`
- `V3`: `0.014284`

Aggregate overall score level:
- `V0`: `0.502154`
- `V3`: `0.524975`

## Decision
- `PAUSE` the synthetic salvage path

## Why
The final diagnostic question was:
- does `V3` show a clearer relative-offset response than `V0`?

The answer is:
- `no`

What the diagnostic shows instead:
- `V3` tends to raise the overall score surface
- but it does not improve signed-offset separation relative to `V0`
- the aggregate positive-minus-negative gap is slightly weaker under `V3`

That means the current `V3` implementation still does not demonstrate the intended theorem-to-mechanism behavior clearly enough to justify more restart work.

## Interpretation
The synthetic restart was the fairest remaining rescue path for the initiative.
It did not produce a positive result.

This does not prove the abstract Q-RoPE idea is impossible.
It does mean:
- this implementation line is not currently showing the intended inductive bias cleanly
- further iteration is no longer justified without a materially new mechanism hypothesis

## Program implication
Set the project to:
- internal archive
- restartable only under a future new mechanism hypothesis

Do not continue with:
- more synthetic packet expansion
- more local tuning
- more remote spend

## Bottom line
The salvage path was tested fairly and failed to recover a clear positive signal.
The correct protocol move is to pause the initiative again.
