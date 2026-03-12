# Q-RoPE Transfer Path Post-Deeper-Pair-Reindex Decision v1

Date: 2026-03-11
Stories: S869

## Decision
- keep the transfer-path branch active
- stop automatic perturbation growth in this step

## Why
- the witness stayed ahead of the bounded symbolic control on both:
  - `mae`
  - `rank_correlation`
- `pair_reindex = 7` was the deepest bounded pairing perturbation planned for the first hardening cycle
- continuing to add perturbations by default would start another open-ended loop instead of closing a decision boundary
