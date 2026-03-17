# Q-RoPE E008 Exception Arbitration Candidate v1

Date: 2026-03-16

## BLUF
- Candidate direction:
  - `synthetic_positional_exception_conditioned_reference_selection_response`
- The task should require one default-valid candidate and one exception-qualified suppressor so that the final target is the next bounded-valid candidate under the exception rule.
- This candidate is memo-only until the gate freezes the fairness contract.

## Candidate Shape
- one query anchor
- one bounded candidate memory
- one default-valid candidate under the base positional-content rule
- one active exception trigger tied to a bounded candidate property
- one final correct target selected only after applying the exception clause

## Admissibility Rationale
- materially different from:
  - direct one-shot bounded selection
  - multi-hop reference resolution
  - stale/current revision discrimination
- closer to bounded rule arbitration than any preserved line currently in the package
