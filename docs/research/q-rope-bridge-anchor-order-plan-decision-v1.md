# Q-RoPE Bridge Anchor-Order Plan Decision v1

## Decision
- `PASS TO ONE BOUNDED IMPLEMENTATION CYCLE`

## Reason
- The bridge-task line now has:
  - explicit task identity,
  - explicit witness/control identities,
  - frozen diagnostics,
  - frozen fairness contract,
  - frozen writable scope,
  - fixed packet shape.
- That is sufficient to permit one bounded local implementation cycle only.

## Next Step
- Reopen code only inside the frozen writable scope.
- Run one fixed three-seed packet.
- Stop the line immediately if the bounded control matches or beats the witness on both declared packet metrics.
