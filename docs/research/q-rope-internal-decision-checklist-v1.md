# Q-RoPE Internal Decision Checklist v1

Date: 2026-03-12
Stories: S1000

## Review Questions
- [ ] Is the standing benchmark still the correct internal reference?
- [ ] Are the four preserved transfer families sufficient for current internal confidence?
- [ ] Is `braid` being treated as a real boundary rather than an ignored exception?
- [ ] Is the non-compressibility screen strong enough to block weak future candidates?
- [ ] Is hardware still correctly out of scope?
- [ ] Is publication still correctly out of scope?

## Decision Options
### Preserve And Pause
Use if the current package is enough and no near-term candidate is worth screening.

### Continue At Low Intensity
Use if the package is strong enough to preserve, but one future memo-only candidate may still be worth evaluating later.

### Open One New Memo-Only Candidate Review
Use only if there is a candidate that clearly passes:
- intake template
- survivor-vs-braid comparison
- deep-reindex non-compressibility screen

## Do Not Approve
- hardware reopening
- publication push
- unscreened execution branch
- same-family symbolic escalation by inertia
