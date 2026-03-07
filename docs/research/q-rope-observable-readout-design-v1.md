# Q-RoPE Observable/Readout Design v1

## Decision
Use a parity-contrast observable as the primary future observable candidate.

Conceptual target:
- measure parity on the constructive channel
- measure parity on the destructive channel
- take the contrast:
  - `O(i,j) := Parity_plus(i,j) - Parity_minus(i,j)`

## Why parity is the right starting point
From the paused local work:
- `weighted` was too compressive
- `parity` was the strongest general-purpose local readout candidate

That does not prove parity is sufficient.
It does make parity the most defensible starting observable for the future mechanism proposal.

## Why parity fits the new comparator
The future comparator is constructive-versus-destructive interference contrast.

Parity is a reasonable first observable for that because:
- it is sensitive to population redistribution across basis states
- it is not just a single-branch scalar probability on one qubit
- it has already shown better dynamic range than the old weighted readout

Most importantly:
- parity can be measured separately on `M_plus` and `M_minus`
- then contrasted directly

That aligns with the comparator definition rather than fighting it.

## Observable definition
Primary future observable target:
- `O(i,j) = Parity_plus(i,j) - Parity_minus(i,j)`

Where:
- `Parity_plus(i,j)` is parity measured on the constructive channel
- `Parity_minus(i,j)` is parity measured on the destructive channel

This is better than:
- single-branch weighted excitation
- single-qubit excitation probability
- plain parity on one branch only

Because the new observable is a channel contrast, not just a raw readout.

## Why this is not just another score shift proxy
This is the core requirement.

The discrimination argument is:
- a uniform score elevation should tend to affect both channels similarly
- a true relative-phase effect should rebalance constructive versus destructive outcomes

So the diagnostic quantity is not:
- “is the score larger?”

It is:
- “does constructive-versus-destructive parity balance change with relative offset?”

That is a materially stronger mechanism claim.

## Observable failure condition
Reject this observable before implementation if, on paper, it can still be reduced to:
- a monotone transform of similarity magnitude
- or a generic increase in activation with no channel-specific discrimination

The future implementation must explain why this reduction does not hold.

## Secondary observable posture
Keep `weighted` only as a shadow reference if a future implementation needs to demonstrate that the new observable is not merely exploiting a readout artifact.

Do not promote:
- `q2`
- `weighted`
- any single-branch observable

as the primary restart observable for this mechanism line.

## Constraint on the next story
The falsification packet memo must assume:
- branch structure is fixed
- comparator is fixed
- primary observable is parity contrast

The next story should therefore bind the synthetic packet directly to:
- `O(i,j) = Parity_plus(i,j) - Parity_minus(i,j)`

## Bottom line
The best observable for the future mechanism proposal is not parity alone.
It is:
- parity contrast across constructive and destructive channels

That is the first observable in this repo that is explicitly designed to distinguish relative-phase interference from uniform score elevation.
