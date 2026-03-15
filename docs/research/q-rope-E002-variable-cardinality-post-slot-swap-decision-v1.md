# Q-RoPE E002 Variable-Cardinality Post-Slot-Swap Decision v1

Date: 2026-03-14
Stories: S1344-S1346

## BLUF
- `slot_swap=1` kept the `E002` line intact.
- The witness stayed ahead on both mean `mae` and mean `rank_correlation`.
- The only valid next move is the closure packet `pair_reindex=7`.

## Decision
- `CONTINUE`

## Why
- `slot_swap=1` was a real perturbation and did not behave inertly.
- The witness kept a clear mean `mae` lead.
- The witness also kept a clear mean `rank_correlation` lead.
- The single-family symbolic contract remains intact across candidate counts `3`, `4`, and `5`.

## Next Step
- Run the fixed `pair_reindex=7` packet only.
- Keep only the witness and bounded symbolic control in scope.
- Stop immediately if the control matches or beats the witness on both declared mean gate metrics.
