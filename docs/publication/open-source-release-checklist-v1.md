# QRoPE open-source release checklist v1

Status: `PUBLIC_RELEASE_PUBLISHED`

Target repository: `https://github.com/Quantyra/QRoPE`

License: `AGPL-3.0-only`

Patent notice: patent pending; U.S. provisional patent application `64/068,121`.

## Required local artifacts

| Artifact | Status | Notes |
| --- | --- | --- |
| `README.md` | Prepared | Public-facing Quantyra/QRoPE positioning with claim boundary. |
| `LICENSE` | Prepared | GNU AGPL v3 text. |
| `NOTICE` | Prepared | Short public ownership and patent/IP-status notice. |
| `PATENTS.md` | Prepared | Patent-pending notice and license boundary. |
| `CITATION.cff` | Prepared | Repository citation metadata. |
| `docs/publication/patent-status-note-v1.md` | Prepared | Plain patent-pending status note. |
| `docs/publication/qrope-paper-v1.md` | Prepared | Standalone bounded repository-paper draft. |
| `docs/publication/references.bib` | Prepared | Formal references for Transformer, RoPE, IBM Runtime primitives, SamplerV2, and backend metadata. |
| `docs/publication/paper-gap-remediation-audit-v1.md` | Prepared | Checklist showing paper audit gaps remediated locally. |
| `docs/publication/external-review-response-v1.md` | Prepared | External review response and unresolved follow-up list. |
| `docs/publication/replication-plan-v1.md` | Prepared | Cross-backend/cross-date and entangling-witness replication plan. |
| `docs/publication/replication-ledger-v1.md` | Prepared | Completed-vs-blocked replication lane ledger. |
| `logs/automated_stage_gates/replication_lanes/replication-ledger.json` | Prepared | Machine-readable replication lane state. |
| `docs/publication/external-release-plan-v1.md` | Prepared | arXiv, OSF, and Zenodo release plan with blockers. |
| `.zenodo.json` | Prepared | Zenodo metadata override for first GitHub release DOI. |
| `.github/workflows/ci.yml` | Prepared | GitHub Actions pytest and coverage workflow. |
| `src/qrope/automated_stage_gates.py` | Prepared | Public implementation reference for formulas, packet generation, and hardware evaluation. |
| `scripts/verify_stage4_hardware_packet.py` | Prepared | Offline verifier for saved Stage 4 packet arithmetic. |
| `logs/automated_stage_gates/stage4_hardware_packet/*.json` | Prepared | Frozen packet, execution, evaluation, summary, and offline verification evidence. |
| `docs/publication/figures/qrope-method-schematic-v1.svg` | Prepared | Publication-grade method schematic. |
| `docs/publication/figures/qrope-product-state-circuit-v1.png` | Prepared | Circuit PNG for the published product-state witness family. |
| `docs/publication/figures/qrope-cx-witness-circuit-v1.png` | Prepared | Circuit PNG for the implemented CX witness variant. |
| `docs/publication/figures/qrope-validation-pipeline-v1.svg` | Prepared | Publication-grade validation pipeline diagram. |
| `docs/publication/figures/qrope-stage4-predictions-v1.png` | Prepared | Matplotlib chart generated from Stage 4 row-level prediction data. |
| `docs/publication/figures/qrope-stage4-metrics-v1.png` | Prepared | Matplotlib chart generated from Stage 4 summary metrics. |
| `docs/publication/figures/qrope-replication-status-v1.png` | Prepared | Matplotlib chart generated from the replication ledger. |
| `CONTRIBUTING.md` | Prepared | Evidence and claim-boundary contribution rules. |
| `SECURITY.md` | Prepared | Private reporting path for secrets and sensitive records. |
| `CODE_OF_CONDUCT.md` | Prepared | Research-collaboration conduct standard. |
| `docs/publication/manuscript-to-provisional-support-audit-v1.md` | Prepared | Support audit and prohibited claims list. |

## Publication gate

Proceed if all statements remain inside this boundary:

- patent-pending QRoPE status and application number;
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
