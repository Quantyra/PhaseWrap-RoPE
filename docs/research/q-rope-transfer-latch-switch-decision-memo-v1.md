# Q-RoPE Transfer Latch-Switch Decision Memo v1

## Decision
- `STOP`

## Reason
- The latch-switch witness did not clear the declared packet gate.
- It preserved the stronger `rank_correlation` signal.
- It lost the primary `mae` metric to the bounded symbolic control.
- Mixed leadership is not enough to keep the branch active.

## Outcome
- Archive the latch-switch execution line.
- Preserve a memo-only next angle rather than opening hardening on a line that already failed the base gate.

## Preserved Boundary
- Latch-switch remains useful as a negative transfer boundary.
- It does not join the positive transfer portfolio.
