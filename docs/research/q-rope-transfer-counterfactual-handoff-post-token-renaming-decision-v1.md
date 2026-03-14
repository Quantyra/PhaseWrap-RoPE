# Q-RoPE Transfer Counterfactual-Handoff Post-Token-Renaming Decision v1

## Decision
- `CONTINUE`

## Reason
- The witness still beat the bounded symbolic control on both declared packet metrics:
  - `mae`
  - `rank_correlation`
- The line therefore remains active under the declared gate.
- Because the mean `rank_correlation` margin narrowed materially, the next valid step is structural hardening, not wider execution.

## Next Step
- Run fixed structural hardening with `pair_reindex=1`.
- Keep only the witness and bounded symbolic control.
- Stop the line immediately if the control matches or beats the witness on both declared packet metrics.
