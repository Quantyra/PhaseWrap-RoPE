# Transition Orbit Implementation Plan v1

## Writable scope
- `src/qrope/synthetic.py`
- `src/qrope/run.py`
- focused tests only

## Required implementation items
- generator for `synthetic_chart_transition_orbit_response`
- generator diagnostics for the orbit gate
- candidate backend: `V_future_relational_witness_transition_orbit`
- bounded orbit-additive symbolic control backend
- fixed first packet over seeds `42/123/777`

## Required packet
- candidate vs fixed five-control stack only
- no packet expansion
- no secondary task

## Required outputs
- implementation memo
- first packet memo
- summary CSV
- post-packet decision memo
