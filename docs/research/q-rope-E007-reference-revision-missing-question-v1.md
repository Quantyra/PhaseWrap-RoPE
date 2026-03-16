# Q-RoPE E007 Reference Revision Missing Question v1

Date: 2026-03-16

## BLUF
- The next missing question is whether the witness can survive bounded revision pressure, not another static reference variant.
- Specifically: can the witness select the currently valid candidate when stale and revised candidates coexist under the same bounded memory?
- Success or failure would change the current interpretation ceiling.

## Missing Question
- Can the witness survive a bounded task where the correct target is defined by a valid revision rule over a candidate memory containing both stale and updated reference candidates, without collapsing to slot heuristics, token identity, or explicit stale/current lookup shortcuts?

## Why This Is Missing
- The preserved package covers static one-shot selection, bounded multi-hop composition, and several bounded robustness/composition layers.
- It does not yet test bounded validity updating inside the candidate set itself.
- `E005` showed that repeated shared-memory reuse is fragile; `E006` showed that bounded two-hop reference can survive. The unresolved gap is bounded stale-versus-current disambiguation.

## Decision Leverage
- A survivor would extend the package from static and multi-hop reference into bounded revision-aware reference validity.
- A failure would clarify that the current ceiling remains at static/multi-hop structure rather than bounded update handling.
