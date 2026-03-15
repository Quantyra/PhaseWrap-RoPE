# Q-RoPE E002 Variable-Cardinality Post-Pair-Reindex Decision v1

Date: 2026-03-14
Stories: S1341-S1343

## BLUF
- `pair_reindex=1` strengthened the `E002` line rather than collapsing it.
- The witness stayed ahead on both mean `mae` and mean `rank_correlation`.
- The only valid next move is the fixed `slot_swap=1` structural hardening packet.

## Decision
- `CONTINUE`

## Why
- `pair_reindex=1` was a real perturbation and did not behave inertly.
- The witness kept a clear mean `mae` lead.
- The witness also kept a clear mean `rank_correlation` lead.
- The single-family symbolic contract remains intact across candidate counts `3`, `4`, and `5`.

## Next Step
- Run the fixed `slot_swap=1` packet only.
- Keep only the witness and bounded symbolic control in scope.
- Stop immediately if the control matches or beats the witness on both declared mean gate metrics.
