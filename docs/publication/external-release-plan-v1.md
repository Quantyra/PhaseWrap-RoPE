# PhaseWrap-RoPE external release plan v1

Status: `PAPER_WITHDRAWN_PENDING_REFRAME`

Date: `2026-05-25`

## Scope

This plan records external release options. The standalone paper draft is withdrawn from the current public branch pending a shorter reframed manuscript.

## arXiv

Recommended action:

- Draft a shorter manuscript from the evidence package before any arXiv submission.
- Submit as a methods/evidence preprint only after the scalar-score framing, full IBM Fez replacement comparison, calibration limitations, and claim boundary remain explicit in the manuscript.
- Candidate categories: `quant-ph` or `cs.LG`, with final category choice made by the submitting author.
- Add the arXiv identifier to `CITATION.cff`, `README.md`, and this file after acceptance.

Blocking items:

- Author account access.
- Endorsement/category eligibility if required by arXiv.
- Final PDF/LaTeX package.
- Replacement manuscript not yet drafted.

## OSF

Recommended action:

- Create an OSF project for PhaseWrap-RoPE.
- Upload only the evidence package, figures, Stage 4 packet files, Stage216-218 full IBM Fez replacement artifacts, completed comparison report, and repository snapshot until a replacement manuscript is ready.
- Link the OSF project from README after public posting.

Blocking items:

- OSF account owner confirmation.
- Project title/description approval.
- Choice of whether OSF is primary preprint host or supplemental archive.

## Zenodo

Recommended action:

- Enable Zenodo GitHub integration for `Quantyra/PhaseWrap-RoPE`.
- Create a GitHub release after the external-review fixes settle.
- Let Zenodo archive the GitHub release and mint a DOI.
- Add the DOI badge and DOI metadata to README and `CITATION.cff`.

Prepared artifact:

- `.zenodo.json`

Blocking items:

- Zenodo account access.
- Zenodo GitHub integration enabled for the repository.
- GitHub release tag decision.

## Release tag recommendation

Use a conservative Stage216-219 update tag for the completed full replacement evidence and bounded RoPE-substitution gate release:

```text
v0.2.44
```

Do not use `v1.0.0` until independent replication or a venue-ready preprint exists.
