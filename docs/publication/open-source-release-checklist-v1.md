# QRoPE open-source release checklist v1

Status: `LOCAL_RELEASE_ARTIFACTS_PREPARED`

Target repository: `https://github.com/Quantyra/QRoPE`

License: `AGPL-3.0-only`

Patent notice: U.S. provisional patent application `64/068,121`, filed `2026-05-18`.

## Required local artifacts

| Artifact | Status | Notes |
| --- | --- | --- |
| `README.md` | Prepared | Public-facing Quantyra/QRoPE positioning with claim boundary. |
| `LICENSE` | Prepared | GNU AGPL v3 text. |
| `NOTICE` | Prepared | Short public ownership and patent-pending notice. |
| `PATENTS.md` | Prepared | Patent-pending notice and license boundary. |
| `CITATION.cff` | Prepared | Repository citation metadata. |
| `CONTRIBUTING.md` | Prepared | Evidence and claim-boundary contribution rules. |
| `SECURITY.md` | Prepared | Private reporting path for secrets and sensitive records. |
| `CODE_OF_CONDUCT.md` | Prepared | Research-collaboration conduct standard. |
| `docs/publication/manuscript-to-provisional-support-audit-v1.md` | Prepared | Support audit and prohibited claims list. |

## Publication gate

Proceed if all statements remain inside this boundary:

- patent-pending QRoPE method;
- phase-wrap mod-8/mod-12 scoring;
- deterministic validation packets;
- raw-count and metadata-backed hardware evidence;
- bounded Stage 4 real-hardware result.

Do not proceed if the manuscript or repository front matter claims:

- broad quantum advantage;
- production transformer superiority;
- general cross-backend robustness;
- unsupported commercial performance claims.

## Remote publication steps

These steps are intentionally separate from local preparation because publishing to GitHub is a public state change:

1. Confirm the target GitHub owner and repository name: `Quantyra/QRoPE`.
2. Create or connect the public GitHub repository.
3. Push the prepared local repository.
4. Confirm the public page renders the license, citation, patent notice, and support audit.
5. Tag the first public release after the remote is visible.
