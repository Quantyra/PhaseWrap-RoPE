# PhaseWrap-RoPE open-source release checklist v1

Status: `PUBLIC_RELEASE_PUBLISHED`

Target repository: `https://github.com/Quantyra/PhaseWrap-RoPE`

License: `AGPL-3.0-only`

Patent notice: USPTO provisional submission received `2026-05-18`; Electronic Acknowledgement Receipt lists application `64/068,121`; final Filing Receipt pending.

## Required local artifacts

| Artifact | Status | Notes |
| --- | --- | --- |
| `README.md` | Prepared | Public-facing Quantyra/PhaseWrap-RoPE positioning with claim boundary. |
| `LICENSE` | Prepared | GNU AGPL v3 text. |
| `NOTICE` | Prepared | Short public ownership and patent/IP-status notice. |
| `PATENTS.md` | Prepared | USPTO acknowledgement-receipt notice and license boundary. |
| `CITATION.cff` | Prepared | Repository citation metadata. |
| `docs/publication/patent-status-note-v1.md` | Prepared | Conservative acknowledgement-receipt status note and timeline. |
| `docs/publication/quickstart-results-summary-v1.md` | Prepared | One-page reviewer entry point with verifier commands, active hardware table, claim boundary, and roadmap. |
| `docs/publication/qrope-paper-v1.md` | Prepared | Standalone bounded repository-paper draft. |
| `docs/publication/references.bib` | Prepared | Formal references for Transformer, RoPE, IBM Runtime primitives, SamplerV2, and backend metadata. |
| `docs/publication/paper-gap-remediation-audit-v1.md` | Prepared | Checklist showing paper audit gaps remediated locally. |
| `docs/publication/external-review-response-v1.md` | Prepared | External review response and unresolved follow-up list. |
| `docs/publication/replication-plan-v1.md` | Prepared | Cross-backend/cross-date and entangling-witness replication plan. |
| `docs/publication/external-release-plan-v1.md` | Prepared | arXiv, OSF, and Zenodo release plan with blockers. |
| `.zenodo.json` | Prepared | Zenodo metadata override for first GitHub release DOI. |
| `.github/workflows/ci.yml` | Prepared | GitHub Actions pytest and coverage workflow. |
| `src/qrope/automated_stage_gates.py` | Prepared | Public implementation reference for formulas, packet generation, and hardware evaluation. |
| `scripts/verify_stage4_hardware_packet.py` | Prepared | Offline verifier for saved Stage 4 packet arithmetic. |
| `scripts/verify_stage4_hardware_sweep.py` | Prepared | Provider-aware offline verifier for the Stage 4 sweep manifest; verifies active committed hardware evidence and keeps deferred/unavailable targets out of the required verifier path. |
| `logs/automated_stage_gates/stage4_hardware_packet/*.json` | Prepared | Default single-packet verifier path for the original IBM Fez product-state pass. |
| `logs/automated_stage_gates/stage4_hardware_packet_ibm_fez_20260517_pass/*.json` | Prepared | Immutable named copy of the IBM Fez 2026-05-17 product-state pass used by the sweep manifest. |
| `docs/publication/figures/qrope-method-schematic-v1.svg` | Prepared | Publication-grade method schematic. |
| `docs/publication/figures/qrope-validation-pipeline-v1.svg` | Prepared | Publication-grade validation pipeline diagram. |
| `docs/publication/figures/qrope-stage4-comparison-v1.svg` | Prepared | Publication-grade Stage 4 hardware comparison chart. |
| `CONTRIBUTING.md` | Prepared | Evidence and claim-boundary contribution rules. |
| `SECURITY.md` | Prepared | Private reporting path for secrets and sensitive records. |
| `CODE_OF_CONDUCT.md` | Prepared | Research-collaboration conduct standard. |
| `docs/publication/manuscript-to-provisional-support-audit-v1.md` | Prepared | Support audit and prohibited claims list. |

## Publication gate

Proceed if all statements remain inside this boundary:

- USPTO-receipted PhaseWrap-RoPE submission status with final Filing Receipt pending;
- phase-wrap mod-8/mod-12 scoring;
- deterministic validation packets;
- raw-count and metadata-backed hardware evidence;
- bounded Stage 4 real-hardware result.
- open questions framed as future work unless backed by current artifacts.

Do not proceed if the manuscript or repository front matter claims:

- broad quantum advantage;
- production transformer superiority;
- general cross-backend robustness;
- unsupported commercial performance claims.

## Remote publication record

The public repository has been created and published:

| Step | Status |
| --- | --- |
| Confirm target GitHub owner and repository name: `Quantyra/PhaseWrap-RoPE`. | Done |
| Create or connect the public GitHub repository. | Done |
| Push the prepared local repository. | Done |
| Confirm the public repository metadata. | Done |
| Tag the first public release after final manuscript approval. | Pending |
| Enable Zenodo integration and mint the release DOI. | Pending |
