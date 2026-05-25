# PhaseWrap-RoPE external release plan v1

Status: `NEGATIVE_RESULTS_PUBLICATION_TRACK`

Date: `2026-05-25`

## Scope

This plan records external release options. The standalone replacement paper draft is withdrawn from the current public branch. The release target is now one essential negative-results methodology paper, with score theory as appendix or optional short note and evidence hygiene as an optional follow-on note.

Primary planning references:

- [PhaseWrap research program decision](phasewrap-research-program-decision-v1.md)
- [Methodology paper draft](phasewrap-methodology-paper-v1.md)
- [Negative results publication roadmap](negative-results-publication-roadmap-v1.md)

## arXiv

Recommended action:

- Draft the retrieval-benchmark methodology paper first, carrying the full Stage 67-96 methodology arc.
- Submit only after the manuscript clearly states that the positive replacement line is closed.
- Candidate category: `cs.LG` for the retrieval-benchmark methodology paper. `quant-ph` remains appropriate only if a later evidence-hygiene hardware-audit note is drafted.
- Add the arXiv identifier to `CITATION.cff`, `README.md`, and this file after acceptance.

Blocking items:

- Author account access.
- Endorsement/category eligibility if required by arXiv.
- Final PDF/LaTeX package.
- Essential negative-results manuscript needs final editorial review.

## OSF

Recommended action:

- Create an OSF project for PhaseWrap-RoPE negative results.
- Upload the evidence package, figures, Stage 4 packet files, Stage216-218 full IBM Fez replacement artifacts, Stage 11 score-theory artifacts, Stage 70 synthesis artifacts, Stage 80/81 support-routing artifacts, and repository snapshot.
- Link the OSF project from README after public posting.

Blocking items:

- OSF account owner confirmation.
- Project title/description approval.
- Choice of whether OSF is primary preprint host or supplemental archive.

## Zenodo

Recommended action:

- Keep the current Zenodo concept DOI associated with the bounded evidence archive.
- Create the next GitHub release only after the negative-results framing, verifier, and reviewer fast path are stable.
- Let Zenodo archive that release and mint a version DOI.
- Add the version DOI metadata to README and `CITATION.cff` after release.

Prepared artifact:

- `.zenodo.json`
- [Release notes for v0.3.0-negative-results](release-notes-v0.3.0-negative-results.md)

Blocking items:

- Zenodo account access.
- Zenodo GitHub integration enabled for the repository.
- GitHub release tag decision.
- explicit owner approval to publish the currently private/unpublished repository state.

## Release tag recommendation

Use a conservative negative-results tag for the reframed evidence package:

```text
v0.3.0-negative-results
```

Do not use `v1.0.0` until a venue-ready negative-results preprint exists.
