# QRoPE external release plan v1

Status: `READY_FOR_ACCOUNT_OWNER_ACTION`

Date: `2026-05-18`

## Scope

This plan prepares the repo for external citable release. It does not claim that arXiv, OSF, or Zenodo submission is complete.

## arXiv

Recommended action:

- Convert `docs/publication/qrope-paper-v1.md` to the target arXiv PDF/LaTeX bundle.
- Submit as a methods/evidence preprint only after the patent-status note and product-state witness boundary remain in the manuscript.
- Candidate categories: `quant-ph` or `cs.LG`, with final category choice made by the submitting author.
- Add the arXiv identifier to `CITATION.cff`, `README.md`, and this file after acceptance.

Blocking items:

- Author account access.
- Endorsement/category eligibility if required by arXiv.
- Final PDF/LaTeX package.

## OSF

Recommended action:

- Create an OSF project for QRoPE.
- Upload the paper, figures, Stage 4 packet files, and repository snapshot.
- Link the OSF project from README after public posting.

Blocking items:

- OSF account owner confirmation.
- Project title/description approval.
- Choice of whether OSF is primary preprint host or supplemental archive.

## Zenodo

Recommended action:

- Enable Zenodo GitHub integration for `Quantyra/QRoPE`.
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

Use a conservative first public review tag:

```text
v0.1.0-review
```

Do not use `v1.0.0` until independent replication or a venue-ready preprint exists.
