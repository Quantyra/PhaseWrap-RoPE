# Q-RoPE Transfer Relay-Binding Task Family Design v1

Date: 2026-03-12
Stories: S961

## Purpose
Define one materially different fifth transfer family that must pass the transfer survivability filter before any execution reopens.

## Family Name
- `relay-binding`

## Proposed Task
- `synthetic_symbolic_insufficiency_relay_binding_response`

## Core Structural Idea
A sample contains three ordered relational segments:
- `source`
- `relay`
- `bind`

The target is not a local function of any single segment and not a simple path average.
The task is designed so that:
- `source` creates a latent relational cue
- `relay` transforms or preserves that cue
- `bind` resolves whether the transformed cue still matches a later declared relation

The key structural property is delayed relational binding.
The output should depend on whether an early relational state survives through a middle transformation and resolves consistently at the final step.

## Why This Is Materially Different
### Not `path`
- `path` aggregates sequential relational effects directly.
- `relay-binding` requires a delayed consistency check, not just path-local accumulation.

### Not `loop-closure`
- `loop-closure` depends on cyclic reconciliation.
- `relay-binding` depends on one directional carry-and-bind mechanism.

### Not `fork-join`
- `fork-join` depends on branch divergence and rejoin comparison.
- `relay-binding` depends on ordered relay persistence without a branch merge.

### Not `braid`
- `braid` depended on crossing reconciliation and failed deeper reindexing.
- `relay-binding` is intended to depend on a carried latent relation that should remain meaningful under deeper pairing perturbation if the family is well formed.

## Candidate Declared Summaries
The eventual bounded symbolic control should only see declared summaries such as:
- source analog summaries
- relay analog summaries
- bind analog summaries
- bounded cross-step declared interactions

It must not receive:
- latent relay-state ids
- exact hidden microstate keys
- explicit carry-state lookup tables

## Desired Internal Property
A good relay-binding task should make the target sensitive to whether the same coarse declared summary can correspond to different latent carried states after the relay step.
That is the main reason this family may survive deeper reindexing better than `braid`.

## Early Failure Mode To Avoid
If the target can be reconstructed from shallow aggregates over:
- source local summary
- relay local summary
- bind local summary
- plus low-order cross products
then this family should be rejected before implementation.

## Output Of This Story
- the family is now explicit enough for survivability review
- implementation remains closed
