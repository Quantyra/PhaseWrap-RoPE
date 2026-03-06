# Q-RoPE V4b Local Comparison Packet v1

## Scope
- Backend: `sim_quantum_statevector`
- Variants: `V3`, `V4`, `V4b`
- Datasets: `yelp`, `imdb`, `amazon`
- Seeds: `42`, `123`, `777`

## Answer on what we are running
Yes.
This packet used local quantum simulation, not cloud hardware and not the `sim_local` naive-Bayes path.

Specifically:
- backend: `sim_quantum_statevector`
- execution mode: local statevector circuit simulation
- credit usage: `0` Quandela credits

## Raw packet summary

| Dataset | Variant | Mean Acc | Std Acc | Mean F1 | Std F1 | Worst Acc |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `amazon` | `V3` | 0.4583 | 0.1909 | 0.3278 | 0.0752 | 0.2500 |
| `amazon` | `V4` | 0.6250 | 0.0000 | 0.6032 | 0.0550 | 0.6250 |
| `amazon` | `V4b` | 0.5000 | 0.1250 | 0.3968 | 0.1531 | 0.3750 |
| `imdb` | `V3` | 0.3750 | 0.1250 | 0.2315 | 0.2228 | 0.2500 |
| `imdb` | `V4` | 0.5833 | 0.0722 | 0.4905 | 0.0861 | 0.5000 |
| `imdb` | `V4b` | 0.5000 | 0.1250 | 0.5704 | 0.1140 | 0.3750 |
| `yelp` | `V3` | 0.4167 | 0.1443 | 0.5000 | 0.1000 | 0.2500 |
| `yelp` | `V4` | 0.4167 | 0.1443 | 0.4111 | 0.0839 | 0.2500 |
| `yelp` | `V4b` | 0.4167 | 0.1443 | 0.1944 | 0.1735 | 0.2500 |

## Why this packet is not yet decision-grade
The current local statevector path is not reproducible across separate processes.

Verified probe:
- same backend
- same dataset
- same seed
- same variant
- two separate runs
- different output metrics

Example:
- `v3-yelp-reprocheck-a`: accuracy `0.375`, F1 `0.0000`
- `v3-yelp-reprocheck-b`: accuracy `0.375`, F1 `0.4444`

## Root cause
The local feature-angle mapping in [qsim.py](C:/Users/Dan/Desktop/Projects/QuantyraQRope/src/qrope/qsim.py) currently uses Python `hash(...)`.

That is process-salted by default, so separate process launches can produce different feature encodings even when:
- dataset is unchanged
- seed is unchanged
- variant is unchanged

This contaminates local stability comparisons.

## Current interpretation
- The packet is still useful as a diagnostic.
- It is not strong enough to authorize or reject a remote `V4b` wave.
- The correct next step is to fix deterministic local feature encoding first.

## Interim readout
If taken at face value:
- `V4` looked strongest on `amazon` and `imdb`
- `V4b` looked middling
- `yelp` remained unresolved

But that readout must be treated as provisional until the reproducibility bug is fixed.

## Go / No-Go
- Decision: `HOLD`

Reason:
- local screening backend is currently nondeterministic across separate process launches
- remote budget should not be allocated from a contaminated local gate

## Bottom line
We are running real local quantum simulations.
The immediate blocker is not lack of execution; it is local reproducibility.
