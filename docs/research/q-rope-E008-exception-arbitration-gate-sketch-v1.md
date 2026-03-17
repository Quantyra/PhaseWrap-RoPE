# Q-RoPE E008 Exception Arbitration Gate Sketch v1

Date: 2026-03-16

## BLUF
- The gate must freeze a bounded exception family before any implementation begins.
- The candidate fails immediately if it becomes an explicit exception lookup task or a disguised stale/current revision task.

## Gate Sketch
- task:
  - `synthetic_positional_exception_conditioned_reference_selection_response`
- must require:
  - one base-valid candidate
  - one active exception condition
  - one final correct target chosen only after applying the exception rule
- blocked by default:
  - token-id shortcuts
  - slot-id shortcuts
  - explicit exception lookup tables
  - count-specific symbolic families
  - disguised revision-state shortcuts
  - transformer surrogates
- required diagnostics should include:
  - base-rule nontriviality
  - exception-trigger nontriviality
  - base-only null pass
  - exception-only null pass
  - final-target noncollapse pass
  - bounded candidate count pass
