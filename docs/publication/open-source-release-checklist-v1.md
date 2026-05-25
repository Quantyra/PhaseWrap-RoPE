# PhaseWrap-RoPE open-source release checklist v1

Status: `NEGATIVE_RESULTS_RELEASE_PREP`

Target repository: `https://github.com/Quantyra/PhaseWrap-RoPE`

License: `AGPL-3.0-only`

Patent notice: low-prominence legal mention only; patent status is not part of the scientific claim, and receipt-specific identifiers or confirmation numbers are not published.

## Required local artifacts

| Artifact | Status | Notes |
| --- | --- | --- |
| `README.md` | Prepared | Public-facing Quantyra/PhaseWrap-RoPE negative-results positioning with claim boundary. |
| `LICENSE` | Prepared | GNU AGPL v3 text. |
| `NOTICE` | Prepared | Short public ownership and patent/IP-status notice. |
| `PATENTS.md` | Prepared | Low-prominence patent/IP notice and license boundary. |
| `CITATION.cff` | Prepared | Repository citation metadata. |
| `docs/publication/patent-status-note-v1.md` | Prepared | Low-prominence legal mention and claim-separation boundary. |
| `docs/publication/quickstart-results-summary-v1.md` | Prepared | One-page reviewer entry point with verifier commands, active hardware table, claim boundary, and roadmap. |
| `docs/publication/references.bib` | Prepared | Formal references for Transformer, RoPE, IBM Runtime primitives, SamplerV2, and backend metadata. |
| `docs/publication/external-review-response-v1.md` | Prepared | External review response and unresolved follow-up list. |
| `docs/roadmap.md` | Prepared | Public review roadmap for framing, API, structure, benchmark, and publication follow-up. |
| `docs/publication/replication-plan-v1.md` | Prepared | Cross-backend/cross-date and entangling-witness replication plan. |
| `docs/publication/external-release-plan-v1.md` | Prepared | arXiv, OSF, and Zenodo release plan with blockers. |
| `docs/publication/negative-results-publication-roadmap-v1.md` | Prepared | Negative-results publication roadmap with one essential methodology paper and optional follow-ons. |
| `docs/publication/phasewrap-methodology-paper-v1.md` | Prepared | Essential negative-results methodology paper draft carrying the Stage 67-96 arc. |
| `docs/publication/phasewrap-execution-freeze-v1.md` | Prepared | Execution guardrail freezing PhaseWrap-positive stage churn unless a reopen gate is predeclared. |
| `docs/publication/phasewrap-decision-execution-audit-v1.md` | Prepared | Requirement-by-requirement audit of decision-memo execution, with external release held pending approval. |
| `docs/publication/release-notes-v0.3.0-negative-results.md` | Prepared | Conservative release notes for the negative-results release tag, not yet published. |
| `.zenodo.json` | Prepared | Zenodo metadata override for first GitHub release DOI. |
| `.github/workflows/ci.yml` | Prepared | GitHub Actions pytest and coverage workflow. |
| `src/qrope/automated_stage_gates.py` | Prepared | Public implementation reference for formulas, packet generation, and hardware evaluation. |
| `scripts/verify_stage4_hardware_packet.py` | Prepared | Offline verifier for saved Stage 4 packet arithmetic. |
| `scripts/verify_stage4_hardware_sweep.py` | Prepared | Provider-aware offline verifier for the Stage 4 sweep manifest; verifies active committed hardware evidence and keeps deferred/unavailable targets out of the required verifier path. |
| `scripts/verify_publication_package.py` | Prepared | One-command local publication package verifier for Stage216-218 evidence, links, figures, claim strings, and secret-fragment hygiene. |
| `logs/automated_stage_gates/stage4_hardware_packet/*.json` | Prepared | Default single-packet verifier path for the original IBM Fez product-state pass. |
| `logs/automated_stage_gates/stage4_hardware_packet_ibm_fez_20260517_pass/*.json` | Prepared | Immutable named copy of the IBM Fez 2026-05-17 product-state pass used by the sweep manifest. |
| `docs/publication/figures/qrope-method-schematic-v1.svg` | Prepared | Publication-grade method schematic. |
| `docs/publication/figures/qrope-validation-pipeline-v1.svg` | Prepared | Publication-grade validation pipeline diagram. |
| `docs/publication/figures/qrope-stage4-comparison-v1.svg` | Prepared | Publication-grade Stage 4 hardware comparison chart. |
| `docs/publication/figures/qrope-full-replacement-metrics-v1.png` | Prepared | Publication-grade Stage216-218 full IBM Fez replacement metric chart. |
| `CONTRIBUTING.md` | Prepared | Evidence and claim-boundary contribution rules. |
| `SECURITY.md` | Prepared | Private reporting path for secrets and sensitive records. |
| `CODE_OF_CONDUCT.md` | Prepared | Research-collaboration conduct standard. |
| `docs/publication/manuscript-to-provisional-support-audit-v1.md` | Prepared | Support audit and prohibited claims list. |

## Negative-results publication gate

Proceed if all statements remain inside this boundary:

- low-prominence provisional-filing mention without publishing receipt-specific identifiers or confirmation numbers;
- phase-wrap mod-8/mod-12 scoring;
- deterministic validation packets;
- raw-count and metadata-backed hardware evidence;
- bounded Stage 4 real-hardware results, including Stage216-218 full IBM Fez replacement comparison.
- Stage 11 fixed-score aliasing and Fourier-support limits.
- Stage 80/81 method-nonspecific support-routing repairs.
- closed positive replacement thesis and explicit negative-results framing.
- low-prominence patent/IP posture separated from scientific claims.
- open questions framed as future work unless backed by current artifacts.

Do not proceed if the manuscript or repository front matter claims:

- broad quantum advantage;
- production transformer superiority;
- general cross-backend robustness;
- RoPE replacement;
- PhaseWrap-specific success for repairs that also solve with `no_position`;
- unsupported commercial performance claims.

## Remote publication record

The public repository has been created and published:

| Step | Status |
| --- | --- |
| Confirm target GitHub owner and repository name: `Quantyra/PhaseWrap-RoPE`. | Done |
| Create or connect the public GitHub repository. | Done |
| Push the prepared local repository. | Done |
| Confirm the public repository metadata. | Done |
| Tag the public release after final manuscript approval. | Done for prior release; standalone paper now withdrawn from current public branch. |
| Enable Zenodo integration and mint the release DOI. | Done |
| Preserve latest archive handle in public docs. | Done: concept DOI `10.5281/zenodo.20306786`. |
