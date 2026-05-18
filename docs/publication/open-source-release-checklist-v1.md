# QRoPE open-source release checklist v1

Status: `PUBLIC_RELEASE_PUBLISHED`

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
| `docs/publication/qrope-paper-v1.md` | Prepared | Standalone bounded repository-paper draft. |
| `docs/publication/references.bib` | Prepared | Formal references for Transformer, RoPE, IBM Runtime primitives, SamplerV2, and backend metadata. |
| `docs/publication/paper-gap-remediation-audit-v1.md` | Prepared | Checklist showing paper audit gaps remediated locally. |
| `docs/publication/figures/qrope-method-schematic-v1.svg` | Prepared | Publication-grade method schematic. |
| `docs/publication/figures/qrope-validation-pipeline-v1.svg` | Prepared | Publication-grade validation pipeline diagram. |
| `docs/publication/figures/qrope-stage4-metrics-v1.svg` | Prepared | Publication-grade Stage 4 witness/control metric chart. |
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

## Remote publication record

The public repository has been created and published:

| Step | Status |
| --- | --- |
| Confirm target GitHub owner and repository name: `Quantyra/QRoPE`. | Done |
| Create or connect the public GitHub repository. | Done |
| Push the prepared local repository. | Done |
| Confirm the public repository metadata. | Done |
| Tag the first public release after final manuscript approval. | Pending |
