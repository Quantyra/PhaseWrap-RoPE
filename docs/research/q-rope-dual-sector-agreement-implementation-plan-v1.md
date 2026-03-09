# Q-RoPE Dual-Sector Agreement Implementation Plan v1

## Scope
- Story: `S177`
- Task: `synthetic_dual_sector_agreement_binary`
- Candidate: `V_future_relational_witness_dual`
- Control: `V_control_symbolic_dual_sector`

## Writable files
Only these paths may change in the first implementation phase:
- `src/qrope/synthetic.py`
- `src/qrope/run.py`
- focused tests only

No changes are allowed to:
- remote backends
- broader benchmark code
- unrelated variant paths

## Generator boundary
Add exactly one new synthetic generator mode:
- `synthetic_dual_sector_agreement_binary`

It must emit:
- train
- validation
- test
- generator diagnostics

And it must preserve:
- balanced class labels
- balanced sign-family frequency in both observation slots
- no token-identity-dependent labeling

## Candidate branch boundary
`V_future_relational_witness_dual` must remain conceptually aligned with the witness branch:
- sector-first relational representation
- compact contrast-oriented feature extraction
- tiny logistic-regression-equivalent head only

The implementation may add dual-observation witness features, but only features derived from the two relational observations.

## Allowed symbolic control boundary
`V_control_symbolic_dual_sector` must use only:
- one-hot `sector_a` block
- one-hot `sector_b` block
- the same logistic-regression-equivalent head

It may not use:
- cross terms
- hidden layers
- token identity
- numeric offsets
- handcrafted agreement indicators

## Required diagnostics
For both variants, emit:
- feature order
- coefficients
- intercept
- data-mode marker
- generator diagnostics

For the candidate branch, also emit:
- bounded-feature audit
- forbidden-input audit

## First execution packet
Exactly six runs:
- seeds `42`, `123`, `777`
- `V_future_relational_witness_dual`
- `V_control_symbolic_dual_sector`
- backend `sim_quantum_statevector`
- task `synthetic_dual_sector_agreement_binary`

## First execution decision rule
The branch remains alive only if:
- the candidate beats the symbolic control on mean accuracy and mean F1
- no single seed collapses the candidate below the control
- the audits remain clean

If not, stop the branch quickly.

## Bottom line
The next implementation phase is now fully bounded.
The code step should only build the fixed task, the fixed candidate, the fixed control, and the fixed six-run packet.
