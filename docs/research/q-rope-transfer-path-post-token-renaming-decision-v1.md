# Q-RoPE Transfer Path Post-Token-Renaming Decision v1

Date: 2026-03-11
Stories: S861

## Decision
- keep the transfer-path branch active
- do not widen the symbolic family
- move to one bounded structural hardening step

## Why
- under the active rule, the branch only stops if the control matches or beats the witness on both:
  - `mae`
  - `rank_correlation`
- that did not happen here
- result is mixed, so the correct move is another bounded perturbation, not closure and not escalation

## Next Step
- fixed structural hardening:
  - `pair_reindex = 1`
- keep:
  - same task
  - same witness
  - same bounded symbolic control
  - same seeds
  - same backend
