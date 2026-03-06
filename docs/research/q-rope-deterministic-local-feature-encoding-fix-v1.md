# Q-RoPE Deterministic Local Feature Encoding Fix v1

## Problem
The local statevector screening backend was not reproducible across separate process launches.

Root cause:
- feature-angle generation in [qsim.py](C:/Users/Dan/Desktop/Projects/QuantyraQRope/src/qrope/qsim.py) used Python `hash(...)`
- Python hash is process-salted by default
- identical runs launched in separate processes could produce different feature encodings

## Fix
- replaced process-salted hashing with a deterministic SHA-256-based token hash
- kept the existing angle-shaping structure intact
- changed only the token-to-integer mapping

## Validation
- focused tests passed: `27 passed`
- repeated identical local runs now match across separate process launches:
  - [v3-yelp-reprocheck-c/metrics.json](C:/Users/Dan/Desktop/Projects/QuantyraQRope/logs/ablation_runs/v3-yelp-reprocheck-c/metrics.json)
  - [v3-yelp-reprocheck-d/metrics.json](C:/Users/Dan/Desktop/Projects/QuantyraQRope/logs/ablation_runs/v3-yelp-reprocheck-d/metrics.json)

## Effect on protocol
- the local `sim_quantum_statevector` gate is now usable again for decision-grade screening
- prior provisional `V4b` comparison results should not be treated as final because they were generated before this fix

## Next step
- rerun the local `V3` vs `V4` vs `V4b` packet on the deterministic simulator path
