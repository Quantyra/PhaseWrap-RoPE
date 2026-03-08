# Q-RoPE Relational Witness Head Memo v1

## Status
- `memo-only`
- `new approach`
- `not approved`

## Motivation
The repository has now falsified several approaches that shared one structural assumption:
- quantum state preparation plus a hand-designed scalar readout should be enough to expose useful relational structure

That assumption failed repeatedly.

What survived across the stronger branches was narrower:
- the quantum side could produce structured intermediate responses
- but the final scalar decision rule was too brittle, too aligned to a shortcut, or simply too weak

## New approach
Use the quantum system as a generator of structured relational evidence, but do not force the final decision into one handcrafted scalar contrast.

Instead:
- keep sector-first quantum diagnostics
- expose a small fixed set of sector-response features
- pass those features into a tiny constrained classical relational head

Working name:
- `relational witness head`

## Why this is materially different
This is not:
- another phase tweak
- another pair-state tweak
- another synthetic relabeling alone

It changes the responsibility split:
- quantum circuit: produce relationally structured signals
- small classical head: evaluate the task rule over those signals

That is a different hypothesis than “the quantum observable alone should already solve the task.”

## Core hypothesis
The quantum component may be useful as a relational feature generator even when direct scalar contrast is not a good end-to-end decision function.

If that is true, then the failure mode was not “no useful signal exists.”
It was:
- “the final observable/aggregation family was too restrictive.”

## Minimal future design
A future bounded restart under this angle would use:
- one alignment-safe synthetic task
- one quantum sector-response generator
- one tiny constrained head over:
  - sector means
  - signed differences
  - magnitude differences

Constraints on the head:
- very low capacity
- explicit input schema
- no token-identity shortcut inputs
- no absolute-position shortcut inputs

## Why this may be worth preserving
The archive now contains evidence that:
- direct pooled scalar paths fail
- direct hand-designed sector contrast can still fail on alignment-safe tasks

A relational witness head is the next clean place to look because it asks:
- was the problem absence of signal?
- or just an overly rigid final decision functional?

## Risks
This approach can become sloppy if unconstrained.

The restart bar must therefore require:
- fixed feature schema
- tiny head only
- explicit anti-shortcut rules
- strict baseline comparison

## Bottom line
The next materially different angle is:
- not “more quantum alone”
- not “more classical alone”
- but a tightly constrained hybrid relational witness head built on sector-first quantum responses
