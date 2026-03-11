# Q-RoPE Transition Orbit Slot-Invariant Top-K Pair-Order Signed Flip Reversion Task Spec v1

Date: 2026-03-11
Stories: S626

## Task
- `synthetic_transition_orbit_slot_invariant_topk_pair_order_signed_flip_reversion_binary`

## Goal
Test whether the ordered relational signal supports reversion after a signed flip under the same slot-invariance contract, rather than persistence of the same signed-flip state.

## Target
- binary label
- `1` iff the paired top-k pair-order state returns to the pre-flip directional orientation after the intermediate signed-flip perturbation
- `0` otherwise

## Required Generator Properties
- latent slot invariance must hold exactly
- coarse signed-flip reversion lookup must be near-null
- within-state signed-flip reversion variation must be present
- paired context diversity must be present
- label balance must be enforced

## Status
- memo-only
- no implementation approved
