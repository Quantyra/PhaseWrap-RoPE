# Token-invariant scaffold binding memo

## Goal
Bind the latent-state invariance diagnostics directly into the preserved restart contract.

## What changed
- the restart scaffold now requires explicit paired latent-state render diagnostics
- the approval-candidate memo now uses those diagnostics as the only remaining implementation gate

## Why this matters
This removes interpretive slack. Any future approval decision now has to point to exact invariance fields instead of general claims about token nuisance status.
