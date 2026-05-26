# Post-Publication Review Triage v1

Status: `TRIAGED_FOR_IMPLEMENTATION`

Date: `2026-05-25`

Source feedback log: `docs/publication/post-publication-review-feedback-log-v1.md`

Repository: public `Quantyra/PhaseWrap`

## Triage Policy

`accept_now` means the item is accepted for this repository pass and should be implemented before the next commit.

`defer` means the item is directionally reasonable but too disruptive, too large, or too dependent on external timing for this pass.

`reject` means the item is not the right move for this repository posture.

No item is marked `accept_later` in this pass. That avoids creating accepted work that is intentionally left incomplete.

## Decisions

| ID | Decision | Implementation scope |
| --- | --- | --- |
| F001 | `accept_now` | Reorient README and docs toward the Stage 67-96 methodology arc as the headline contribution; keep hardware as secondary audit evidence. |
| F002 | `accept_now` | Add a narrower public Stage 218 decision label while preserving the historical manifest decision for release integrity. |
| F003 | `accept_now` | Demote hardware wording in the reviewer fast path to bounded provider-audit/readout-witness evidence. |
| F004 | `accept_now` | Rename Stage 219 public decision language away from RoPE-substitution support and toward ranking parity with calibration/probability degradation. |
| F005 | `accept_now` | Split Stage 219 ranking-parity pass logic from degradation observations. |
| F006 | `accept_now` | Replace `adequacy_criteria` with ranking-parity terminology in Stage 219 outputs. |
| F007 | `defer` | A full README cut and thematic stage-summary migration is valuable but too large for this stabilization pass. |
| F008 | `accept_now` | Add a concise README command matrix with timing and credential requirements. |
| F009 | `accept_now` | Add a top-line PhaseWrap/qrope identity note; do not rename the Python package in this pass. |
| F010 | `defer` | Moving 100+ stage modules out of `src/qrope/` is a breaking package-structure change and should be planned separately. |
| F011 | `accept_now` | Add focused API documentation for the public scoring API and custom-period behavior. |
| F012 | `defer` | Dependency extras are already split enough for this release; a deeper core-only dependency-group cleanup can wait. |
| F013 | `accept_now` | Replace loop-based public angle wrapping with constant-time modular wrapping. |
| F014 | `accept_now` | Centralize reusable PhaseWrap formula calls in `qrope.scoring` for Stage 11 and automated-stage helpers while preserving legacy stage interfaces. |
| F015 | `accept_now` | Clarify `phase_margins()` custom-period output so `m8`/`m12` aliases only appear for the default `(8, 12)` periods. |
| F016 | `accept_now` | Document package API version versus evidence-release version semantics. |
| F017 | `accept_now` | Add a cheap public-surface smoke/integrity script and run it in CI. |
| F018 | `accept_now` | Add negative tests for hardware interpreter failure modes, including missing artifacts, invalid bitstring order, missing families, and malformed count records. |
| F019 | `defer` | Hash-locking requires selecting a lock tool and refreshing dependency policy; do not add an unverified lock artifact in this pass. |
| F020 | `accept_now` | Resolve Stage 218/219 default artifact paths from a repository-root helper instead of process CWD. |
| F021 | `accept_now` | Add automated secret-hygiene scanning to CI. |
| F022 | `accept_now` | Restrict local dotenv loading to an explicit provider credential allowlist and support common quoting/export syntax. |
| F023 | `accept_now` | Add one README sentence summarizing AGPL plus patent-file posture and point to `PATENTS.md`. |
| F024 | `defer` | Org-profile visibility is external GitHub UI behavior; direct repo URL is already public. Recheck manually after stabilization if needed. |
| F025 | `defer` | Public promotion should wait until this stabilization commit is merged and verified. |

## Rejected Options

| Option | Reason |
| --- | --- |
| Rename the Python package from `qrope` to `phasewrap` immediately. | Too disruptive for saved artifacts, imports, reviewer commands, and existing release evidence. A top-line identity note gives reviewers the needed context without breaking compatibility. |
| Replace historical Stage 218 manifests in-place with only the new public decision label. | Release integrity is stronger if old manifest values remain auditable and the narrower label is added as an interpretation alias. |
| Treat Stage 219 as a substitution-adequacy pass. | The documented result is ranking parity on selected bridges with RoPE retaining better probability/calibration, not substitution adequacy. |

## Verification Targets

This pass should end with:

- public scoring API tests passing;
- Stage 218 and Stage 219 interpreters regenerating current artifacts;
- publication verifier passing;
- public-surface smoke scan passing;
- secret-hygiene scan passing;
- changed files committed and pushed to `main`.

## Implementation Checklist

| Accepted item(s) | Implemented in |
| --- | --- |
| F001, F003 | README headline/fast-path/claim-status edits emphasizing the Stage 67-96 methodology arc and demoting hardware to secondary audit evidence. |
| F002 | Stage 218 `public_decision` alias `IBM_FEZ_FROZEN_PACKET_READOUT_NOISE_DELTA_FAVORS_PHASEWRAP`, regenerated Stage 218 artifacts, and updated publication text. |
| F004, F005, F006 | Stage 219 decision rename, split `ranking_criteria` from `degradation_observed`, removal of `adequacy_criteria`, regenerated Stage 219 artifacts, and updated tests/docs. |
| F008, F009, F016, F023 | README command matrix, top-line `PhaseWrap`/`qrope` identity note, version-semantics note, and patent/license posture sentence. |
| F011, F015 | Expanded `docs/api/scoring.md` and public tests for custom-period return semantics. |
| F013, F014 | Constant-time public wrapping and central scorer reuse from Stage 11/automated-stage helpers. |
| F017, F021 | `scripts/smoke_public_surface.py`, `scripts/scan_secret_hygiene.py`, and CI wiring. |
| F018 | Stage 218 negative tests for missing artifacts, invalid bitstring order, missing families, malformed counts, and bad shot fields. |
| F020 | `qrope.paths` repo-root helpers and Stage 218/219 default path resolution. |
| F022 | `load_local_dotenv()` allowlist, common `export`/quote parsing, and dotenv tests. |
