# Q-RoPE Transition Orbit Slot-Invariant Top-K Pair-Order Drift Approval Candidate v1

Date: 2026-03-11
Status: approval-candidate
Story: S565

## Decision
- elevate the line to approval-candidate posture
- keep it memo-only in this step

## Why This Line Exists
- the stopped slot-invariant top-k pair-order stability branch failed cleanly against bounded symbolic controls
- this line makes pair-order drift magnitude primary instead of binary stability classification
- this is materially different from the stopped branch, not a relabel of the same objective

## Why It Is Not Yet Implementation-Approved
- the task still needs a dedicated implementation-approval gate
- the hard-stop diagnostics must be bound directly into that gate before code reopens
