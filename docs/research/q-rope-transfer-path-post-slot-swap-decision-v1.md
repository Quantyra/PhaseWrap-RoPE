# Q-RoPE Transfer Path Post-Slot-Swap Decision v1

Date: 2026-03-11
Stories: S867

## Decision
- keep the transfer-path branch active
- preserve the current transfer result as the active bounded line
- do not auto-open another perturbation family in this step

## Why
- the witness stayed ahead of the bounded symbolic control on both:
  - `mae`
  - `rank_correlation`
- the branch is already stronger than the first nuisance packet and the first structural packet
- the next move should be chosen deliberately, not by reflex
