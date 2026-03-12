# Q-RoPE Theory Characterization Memo v1

Date: 2026-03-11
Stories: S874

## Scope
Characterize why the standing symbolic-insufficiency witness beats the frozen symbolic families and why that advantage transfers to the first path-local task.

## Standing Benchmark
- witness:
  - `V_future_relational_witness_symbolic_insufficiency`
- task:
  - `synthetic_symbolic_insufficiency_transition_response`
- means:
  - `mae = 0.119724`
  - `rank_correlation = 0.967399`
- frozen symbolic control means:
  - `mae = 0.262984`
  - `rank_correlation = 0.263411`

## Transfer Result
- witness:
  - `V_future_relational_witness_symbolic_insufficiency_path`
- task:
  - `synthetic_symbolic_insufficiency_path_response`
- base means:
  - `mae = 0.100666`
  - `rank_correlation = 0.501251`
- bounded path symbolic control means:
  - `mae = 0.149769`
  - `rank_correlation = -0.390044`

## Structural Difference
The witness and the symbolic controls are not doing the same job.

### Witness Side
The transition witness in [run.py](C:/Users/Dan/Desktop/Projects/QuantyraQRope/src/qrope/run.py) adds two latent-response terms beyond the declared summaries:
- `latent_transition_phase`
- `latent_transition_curvature`

Those are driven by:
- declared analog terms:
  - `sector_magnitude_delta`
  - `ordered_content_delta`
  - `orientation_delta`
- plus a latent transition index:
  - `symbolic_insufficiency_latent_ids(...)`

The path witness then composes those witness outputs into path-level latent interaction terms:
- `path_phase_mean`
- `path_phase_gap`
- `path_curvature_mean`
- `path_curvature_product`
- `path_latent_declared_mix`
- `path_latent_cross_curvature`

### Symbolic Side
The frozen symbolic families were allowed to use only:
- coarse transition indicators
- declared first-order analog summaries
- bounded low-order cross terms
- bounded atlas/chart expansions over those declared analog summaries

They were never allowed to use:
- latent path-state ids
- exact microstate keys
- hidden tuple lookups
- unrestricted basis growth

## Working Interpretation
The current evidence supports a narrow claim:
- the witness advantage is concentrated in latent-conditioned relational response structure that is not recoverable by the frozen declared-summary symbolic families we tested

This is stronger than saying "the witness is just higher-order polynomial." We tested progressively stronger polynomial/atlas families and they did not catch up.

## Limits
- This is still an internal mechanism characterization, not an external theory proof.
- The result is hardened on one benchmark family plus one transfer family, not broad generalization.
- The current memo does not claim that no stronger symbolic family exists.
- The memo does not claim hardware relevance.

## Practical Conclusion
- the witness is not winning by a tiny accident in one packet
- the strongest explanation in the repo is that the witness uses latent-conditioned relational response structure that the frozen symbolic families intentionally exclude
- that is enough to justify preserving the result and shifting effort from more same-family fairness loops to explanation and internal reporting
