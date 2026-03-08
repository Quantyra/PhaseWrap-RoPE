# Q-RoPE Relational Witness Validity Hardening Plan v1

## Decision
- one hardening step only:
  - `split-rotation robustness`

## Why this is the right next test
The first positive packet already established:
- multi-seed success
- feature-schema compliance
- anti-collapse compliance

The main remaining risk is that the result could depend too heavily on one particular deterministic split realization.

So the smallest meaningful hardening step is:
- keep the same task
- keep the same candidate
- keep the same seeds
- rotate which samples fill train/validation/test slots within each balanced bucket

## What this tests
It tests whether the witness result survives:
- alternate but still deterministic split assignments

It does not test:
- new tasks
- new variants
- remote robustness
- benchmark transfer

## Hardening gate
The branch remains healthy only if the witness candidate:
- stays ahead of `V0` in mean accuracy and mean F1
- remains coefficient-auditable
- keeps anti-collapse and forbidden-input guarantees
- does not collapse under the rotated split policy

## Scope limits
- no new datasets
- no new features
- no new head family
- no hyperparameter tuning

## Next step
Implement one split-rotation control and run the same three-seed packet under that alternate split.
