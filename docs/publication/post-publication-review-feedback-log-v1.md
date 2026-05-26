# Post-Publication Review Feedback Log v1

Status: `CAPTURED_AND_TRIAGED`

Date: `2026-05-25`

Repository state reviewed: public `Quantyra/PhaseWrap` release with Zenodo version DOI `10.5281/zenodo.20387905`.

## Purpose

This document logs external reviewer feedback received after the public PhaseWrap negative-results release. It is the capture artifact; triage decisions are recorded separately in [post-publication review triage v1](post-publication-review-triage-v1.md).

## Review Sources

| Source | Overall assessment | Primary emphasis |
| --- | --- | --- |
| Claude | Strong epistemic discipline; strongest contribution is methodology, especially Stage 80/81. | Reorient public framing toward the assistance-pipeline confound, reduce hardware headline weight, rename overclaiming identifiers, cut README volume. |
| Grok | Publication-ready negative-results repo with excellent transparency and reproducibility. | Keep framing, improve packaging/API docs, move stage scripts out of the package over time, make next steps more visible. |
| ChatGPT Pro | Strong evidence/review repository with high-quality claim hygiene and reviewer pathway. | Fix public scoring robustness, centralize score implementation, clarify custom period API, align version semantics, split Stage 219 criteria, strengthen CI/repro/security. |

## Positive Feedback Captured

### Claim Discipline

- Claim boundary is unusually explicit and valuable.
- Public framing correctly rejects RoPE replacement, production transformer superiority, quantum advantage, entanglement-based advantage, and broad cross-backend robustness.
- Negative-results posture is viewed as credible and rare.

### Reproducibility And Evidence Hygiene

- Frozen packets, raw counts, provider-aware bitstring decoding, known-state calibration, offline verifiers, deterministic scripts, CI checks, and Zenodo archival are viewed as substantive rather than cosmetic.
- The no-credentials reviewer path and optional provider extras are considered the right split.
- Stage 217 known-state calibration gating Stage 218 interpretation is viewed as a strong pattern.

### Scientific Contribution

- Stage 80/81, and related Stage 87 evidence, are repeatedly identified as the most transferable result: support-routed repairs solve phase-cued retrieval for `no_position` too.
- The assistance-pipeline confound is viewed as a methodology warning relevant to positional-encoding benchmark design.
- Stage 11 score theory is considered useful as appendix-level mathematical characterization.

### Release Readiness

- Public GitHub release, Zenodo DOI, reviewer fast path, `CITATION.cff`, `.zenodo.json`, `PATENTS.md`, `SECURITY.md`, contribution rules, and reproducible environment are viewed as professional and review-ready.

## Feedback Items To Triage

| ID | Topic | Source(s) | Feedback captured | Triage status |
| --- | --- | --- | --- | --- |
| F001 | Public headline artifact | Claude | Treat the methodology paper, especially the Stage 67-96 arc and Stage 80/81 result, as the headline artifact. Hardware audit infrastructure should be secondary or separate. | Not triaged |
| F002 | Hardware decision string | Claude | `FULL_REPLACEMENT_HARDWARE_POSITIVE_PHASEWRAP_ADVANTAGE` is rhetorically stronger than the bounded result. Consider a narrower identifier such as `IBM_FEZ_FROZEN_PACKET_READOUT_NOISE_DELTA_FAVORS_PHASEWRAP`. | Not triaged |
| F003 | Hardware framing weight | Claude | README places theory/synthesis and hardware fast paths side by side, implicitly elevating hardware to peer status with methodology. Consider demoting hardware to provider-audit/readout-witness infrastructure. | Not triaged |
| F004 | Stage 219 decision string | Claude, ChatGPT Pro | `BOUNDED_PHASEWRAP_ROPE_SUBSTITUTION_SUPPORTED_WITH_MEASURED_CALIBRATION_DEGRADATION` conflicts with the closed replacement thesis. Rename toward ranking parity plus calibration/probability degradation. | Not triaged |
| F005 | Stage 219 criteria semantics | ChatGPT Pro | Split ranking parity from degradation observation. Do not make probability/calibration degradation required for a ranking-parity pass, because better PhaseWrap calibration would otherwise fail the gate. | Not triaged |
| F006 | Stage 219 field naming | ChatGPT Pro | `adequacy_criteria` conflicts with the claim boundary saying this is not substitution adequacy. Rename or remove the field. | Not triaged |
| F007 | README length | Claude | README is too long and stage-heavy. Consider cutting to about 200 lines and moving stage summaries into thematic docs. | Not triaged |
| F008 | README command matrix | ChatGPT Pro | Add a concise matrix with goal, command, expected time, and credential requirement. | Not triaged |
| F009 | qrope/PhaseWrap identity | Claude, Grok | Repo is `PhaseWrap` but package/stage IDs are `qrope`; this causes reviewer friction. Either add a top-line explanation or plan a compatibility-shim rename. | Not triaged |
| F010 | Stage-file organization | Grok | More than 100 `stage*.py` files directly under `src/qrope/` make the package feel flat. Consider moving experiment/stage modules to `experiments/`, `stages/`, or `scripts/stages/`. | Not triaged |
| F011 | API docs | Grok | Add generated API docs or expand `docs/api/` from docstrings. | Not triaged |
| F012 | Core dependency split | Grok | Consider a minimal dependency group for core scoring separate from full hardware/review stacks. | Not triaged |
| F013 | Public scoring robustness | ChatGPT Pro | Replace repeated-loop angle wrapping in public scoring with constant-time modular wrapping such as `math.remainder`. | Not triaged |
| F014 | Duplicate score implementations | ChatGPT Pro | Centralize PhaseWrap scoring in `qrope.scoring`; have stages import it unless they need explicitly named frozen legacy behavior. | Not triaged |
| F015 | Custom period API clarity | ChatGPT Pro | `phase_margins()` returns `m8` and `m12` even for custom period pairs. Consider `first_margin`/`second_margin` and period-keyed output, or only expose `m8`/`m12` for `(8, 12)`. | Not triaged |
| F016 | Version semantics | ChatGPT Pro | `pyproject.toml` package version and evidence release version differ. Either align them or document that package API version and evidence-release version are different. | Not triaged |
| F017 | CI tiers | ChatGPT Pro | Add a broader cheap CI tier: import all modules, run script `--help` where available, run tiny fixtures for selected stages, and verify artifact integrity. | Not triaged |
| F018 | Hardware verifier negative tests | ChatGPT Pro | Add synthetic tests for malformed counts, missing families, missing source artifacts, unknown bitstring orders, and bad shot-count fields. | Not triaged |
| F019 | Lockfile / hash locking | ChatGPT Pro | `requirements-review.txt` pins versions but does not hash-lock them. Consider `uv.lock`, hash-locked requirements, `conda-lock.yml`, or a container recipe. | Not triaged |
| F020 | Artifact path resolution | ChatGPT Pro | Default artifact paths rely on running from repo root. Resolve from a repo root constant, environment variable, or explicit CLI arguments. | Not triaged |
| F021 | Secret scanning | ChatGPT Pro | Add automated secret scanning in CI or pre-commit, such as `detect-secrets`, `gitleaks`, or GitHub secret scanning. | Not triaged |
| F022 | dotenv helper | ChatGPT Pro | `load_local_dotenv()` silently imports any key and does not handle full dotenv syntax. Restrict to provider credential allowlist or use `python-dotenv` in optional provider extras. | Not triaged |
| F023 | Patent/license README sentence | ChatGPT Pro | AGPL plus provisional patent posture is coherent, but downstream implications should be summarized in one README sentence instead of only in `PATENTS.md`. | Not triaged |
| F024 | Profile/org visibility | Grok | Check whether the repo appears on the Quantyra org overview page; GitHub may lag. | Not triaged |
| F025 | Community/promotion path | Grok | After repo stabilization, consider a short public thread or arXiv preprint to reach positional-encoding and quantum-ML reviewers. | Not triaged |

## Potential Work Buckets For Later Analysis

These buckets are for organizing the next pass only. No item is accepted by appearing here.

| Bucket | Candidate items |
| --- | --- |
| Immediate correctness/API | F013, F014, F015, F016 |
| Claim-language cleanup | F002, F004, F005, F006, F023 |
| Documentation information architecture | F001, F003, F007, F008, F009 |
| Packaging structure | F010, F011, F012 |
| CI and reproducibility | F017, F018, F019, F020 |
| Security hygiene | F021, F022 |
| External visibility | F024, F025 |

## Open Questions For Triage

- Should any decision-string rename be done as a new stage/result alias while preserving historical manifest values?
- Should the README be cut before any arXiv/OSF/blog step, or is the current reviewer-fast-path enough for the repository artifact?
- Should package versioning track evidence releases or remain a separate API version line?
- Is a `phasewrap` package alias worth the compatibility and maintenance cost, or is top-line documentation enough?
- Which changes justify a patch release and Zenodo version, versus normal `main` improvements only?

## Boundary For Next Step

The next step should be an explicit analysis document or issue triage that labels each item as one of:

- `accept_now`
- `accept_later`
- `defer`
- `reject`
- `needs_more_context`

No arXiv, OSF, blog, public announcement, tag movement, or new Zenodo version should be created merely because this feedback was logged.
