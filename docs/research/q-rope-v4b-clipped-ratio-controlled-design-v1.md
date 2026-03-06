# Q-RoPE V4b Clipped Ratio-Controlled Design v1

## Objective
Define a stronger successor to the damped-only `V4` that directly targets positional-phase dominance without collapsing expressivity.

## Why `V4` failed
The damped-only `V4` reduced the global phase base from `0.24` to `0.14`.
That changed magnitude, but not mechanism.

Observed result on the meaningful local backend:
- `imdb`: improved
- `yelp`: regressed
- `amazon`: regressed

Interpretation:
- the instability is not explained by “phase too strong everywhere”
- the model needs local control over positional contribution, not just a smaller global constant

## `V4b` definition
`V4b` = clipped relative-phase Q-RoPE with light feature/phase ratio control

Core idea:
- keep a moderate positional base
- clip the relative positional term before it becomes dominant
- scale positional strength against feature magnitude so the position signal stays subordinate

## Proposed shared formulation
Let:
- `f_i` be the feature-loading angle for qubit `i`
- `p_i` be the raw positional phase for qubit `i`
- `r_i` be the backend-effective positional phase for qubit `i`

Use:
- moderate base phase: `base = 0.18`
- raw phase schedule: `p_i = base * (i + 1)`
- clip threshold: `phase_clip = 0.22`
- ratio factor: `rho = 0.35`

Then:
1. raw relative phase:
- `delta_i = clip(p_i, -phase_clip, phase_clip)`

2. feature-aware cap:
- `cap_i = rho * max(abs(f_i), 0.05)`

3. effective positional phase:
- `r_i = sign(delta_i) * min(abs(delta_i), cap_i)`

This keeps the positional term bounded by both:
- a global clip
- a local feature-relative cap

## Why this is better than damped-only `V4`
- it still reduces positional aggressiveness
- it does so adaptively instead of uniformly
- it preserves moderate positional signal when feature loading is strong
- it suppresses positional dominance when feature loading is weak

## Backend translation policy
Apply the same shared effective phase logic first, then translate to each backend:

### Statevector / local quantum path
- use `r_i` directly in `RZ` gates

### Photonic path
- derive raw `theta_left` / `theta_right` from features as before
- derive photonic relative phase from the clipped ratio-controlled effective phase
- keep current `effective_theta` bounding logic unchanged in the first pass

### IBM path
- use the same clipped ratio-controlled phase aggregate instead of the current plain `phases[0] + 0.5 * phases[1]`

## Recommended implementation shape
Keep implementation small by introducing shared helpers in [qsim.py](C:/Users/Dan/Desktop/Projects/QuantyraQRope/src/qrope/qsim.py):
- `raw_variant_phases(variant, n_qubits)`
- `effective_variant_phases(variant, feature_angles)`

Rules:
- `V0-V4` can keep current behavior
- `V4b` uses the new clipped ratio-controlled path

## Zero-credit validation plan
Backends:
- `sim_quantum_statevector`
- optional `sim_qiskit_aer`

Datasets:
- `yelp`, `imdb`, `amazon`

Seeds:
- `42`, `123`, `777`

Comparators:
- `V3`
- `V4`
- `V4b`

## Promotion gate
`V4b` qualifies for any remote budget only if:
1. std accuracy improves or stays flat on at least two datasets vs `V3`
2. mean accuracy does not regress materially on more than one dataset
3. worst-seed accuracy does not collapse vs `V3`
4. results are directionally cleaner than damped-only `V4`

## Risks
- the ratio control may over-constrain the position signal and collapse back toward `V2`-like behavior
- the current local datasets are still small, so even a better `V4b` may require later larger-sample confirmation

## Bottom line
`V4b` is the right next redesign because it changes the positional mechanism, not just the global scale.
