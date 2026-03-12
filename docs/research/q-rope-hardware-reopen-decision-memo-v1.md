# Q-RoPE Hardware Reopen Decision Memo v1

Date: 2026-03-12
Stories: S907

## BLUF
Do not reopen real-quantum hardware execution from the current state.
The current package is strong enough for internal mechanism preservation and internal review, but not strong enough to justify hardware confounds.

## Current Evidence Base
### Standing Benchmark
- witness:
  - `V_future_relational_witness_symbolic_insufficiency`
- task:
  - `synthetic_symbolic_insufficiency_transition_response`
- means:
  - `mae = 0.119724`
  - `rank_correlation = 0.967399`

### Bounded Transfer Result 1
- witness:
  - `V_future_relational_witness_symbolic_insufficiency_path`
- task:
  - `synthetic_symbolic_insufficiency_path_response`
- bounded hardening cycle cleared

### Bounded Transfer Result 2
- witness:
  - `V_future_relational_witness_symbolic_insufficiency_loop`
- task:
  - `synthetic_symbolic_insufficiency_loop_closure_response`
- bounded hardening cycle cleared

## Decision
- `NO-GO` for hardware reopening now.

## Why
1. The result is still a mechanism result.
- It shows bounded separation from frozen symbolic families.
- It does not yet show robustness under execution noise, compilation constraints, or backend translation.

2. Cross-task evidence is still bounded.
- We now have one benchmark plus two materially different transfer families.
- That is enough for internal preservation.
- It is not enough to justify hardware as the highest-value next experiment.

3. Hardware would add confounds before it adds clarity.
- backend translation differences
- queue/runtime variation
- shot-noise effects
- calibration drift
- provider-specific execution constraints

4. The next scientific bottleneck is explanation, not hardware stress.
- The standing question is why the witness beats the frozen symbolic families.
- Hardware would test a different question before that one is fully exploited.

## Reopen Conditions
Hardware should be reconsidered only if at least one of the following happens:
1. a third materially different transfer family also holds under bounded hardening
2. a theory-backed note narrows the expected hardware-relevant mechanism enough to justify the confounds
3. a sponsor-level decision explicitly prioritizes hardware exploration over further scientific de-risking

## What This Memo Enables
- internal program review
- prioritization against other Quantyra research lines
- explicit refusal of premature hardware escalation

## What This Memo Does Not Enable
- hardware campaign approval
- NISQ usefulness claim
- publication claim
- external superiority claim
