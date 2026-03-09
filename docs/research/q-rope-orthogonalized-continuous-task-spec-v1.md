# Orthogonalized continuous task specification

## Task
- `synthetic_dual_orthogonalized_continuous_response`

## Purpose
Define one harder continuous target where coarse agreement tuples no longer carry useful standalone signal, so a bounded coarse lookup should be near-zero by construction.

## Core rule
Start from a bounded analog response built from within-state relational factors only, for example:
- `sector_magnitude_delta`
- `ordered_content_delta`
- optional centered analog coupling term

Then orthogonalize the target with respect to the coarse tuple:
- for each `(sign_agreement, content_agreement, orientation_agreement)` state,
- subtract the within-state mean target contribution,
- so the expected target conditioned on the coarse tuple is approximately zero.

## Anti-shortcut condition
Reject the task unless both are true on paper:
- `E[target | coarse_tuple] ~= 0`
- variation remains inside each coarse tuple after centering

## Expected control consequence
- a coarse lookup regressor should stay near a null baseline
- any future success would need to come from analog structure, not coarse-state identity alone
