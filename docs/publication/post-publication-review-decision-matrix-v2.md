# Post-Publication Review Decision Matrix v2

Status: `ANALYZED_FOR_RELEVANCE`

Date: `2026-05-25`

Repository: public `Quantyra/PhaseWrap`

Prior triage: [post-publication review triage v1](post-publication-review-triage-v1.md)

## Purpose

This document logs the second post-publication review batch from ChatGPT Pro, Grok, and Claude, then evaluates each recommendation on validity against the current repository evidence.

This is not an implementation-timing triage. The project is treated as open-ended, so long-running work can still be marked relevant if the feedback is technically or scientifically valid.

## Decision Labels

| Label | Meaning |
| --- | --- |
| `relevant` | The feedback is valid for the repository's scientific, reviewer, reproducibility, or maintainability goals. |
| `partially_relevant` | The underlying concern is valid, but the proposed remedy is too broad, already partly satisfied, or mixed with a weaker assumption. |
| `discard` | The feedback is factually wrong for the current repo, already resolved enough that no further action is justified, or conflicts with intentional project constraints. |

## Overall Analysis

The second review batch converges on one clear conclusion: PhaseWrap is credible as a negative-results, reproducibility, and benchmark-methodology package, but the public front door is still too large and too stage-heavy for busy reviewers.

The repo already has strong claim discipline and a no-credentials verification path. The remaining validity gaps are mostly reviewer ergonomics, repository information architecture, validation hardening, CI breadth, and supply-chain reproducibility.

The strongest new technical criticisms are valid:

- `src/qrope/run.py` is about 1 MB and is too large to review as a normal library module.
- `src/qrope/qsim.py` silently clamps qubit counts and silently assigns a fallback phase for unknown variants, which is risky in audit-oriented code.
- The fast CI path is useful but not sufficient as the only non-live evidence gate.
- The repo needs a smaller top-level reviewer entry point and a single obvious no-credential verification command.

The strongest already-addressed concern is hardware-overclaim wording. The prior pass added the Stage 218 public decision `IBM_FEZ_FROZEN_PACKET_READOUT_NOISE_DELTA_FAVORS_PHASEWRAP` and demoted hardware in the README. The remaining valid point is not that the repo lacks a bounded hardware caveat, but that the caveat should be even more visually prominent and old `advantage` strings should not be used in new public-facing artifacts.

## Decision Matrix

| ID | Source | Feedback | Decision | Evidence-based rationale |
| --- | --- | --- | --- | --- |
| R001 | ChatGPT Pro | Add a real `REVIEWER_START.md` that is actually short. | `relevant` | The current README and quickstart materials remain long. A compact top-level front door would reduce reviewer load without changing evidence. |
| R002 | ChatGPT Pro | Add a single no-credential verifier CLI such as `phasewrap-verify --profile public` or `python -m qrope.verify_publication --profile public`. | `relevant` | The repo has verifier ingredients but no single canonical package CLI. This is valid reviewer ergonomics work. |
| R003 | ChatGPT Pro | Move long command matrices and stage detail to a full stage index or reproduction matrix. | `relevant` | The stage-heavy design is useful as an audit archive but too dense as first-contact documentation. |
| R004 | ChatGPT Pro | Add a visible README callout defining "hardware-positive" as bounded two-qubit readout-audit evidence only. | `relevant` | Current README says this in prose, but the repeated hardware-positive artifacts can still be misread. A callout is warranted. |
| R005 | ChatGPT Pro, Claude | Split the monolithic `src/qrope/run.py`. | `relevant` | Local inspection confirms `run.py` is about 1 MB. That is a maintainability and reviewability problem even if historical code remains preserved. |
| R006 | ChatGPT Pro | Extract the reviewer/publication path into smaller `verify/`, `stages/`, and `cli.py` modules. | `relevant` | This is the right first seam because it protects the public reviewer path while leaving historical stage code intact. |
| R007 | ChatGPT Pro | Make `qsim.build_quantum_state()` and `build_branch_state()` fail loudly for invalid qubit counts instead of clamping. | `relevant` | Local inspection confirms silent `max(2, min(n_qubits, 6))` clamping. That is risky for reproducibility code. |
| R008 | ChatGPT Pro | Make `qsim.raw_variant_phases()` fail for unknown variants instead of defaulting to `0.04`. | `relevant` | Local inspection confirms the fallback. Unknown experiment variants should not silently become a different experiment. |
| R009 | ChatGPT Pro | Document or widen `stable_token_hash()` because it uses a 16-bit SHA-256 prefix. | `partially_relevant` | Valid if collisions affect experiments. It may be acceptable for toy deterministic bucketing, but that assumption should be explicit or tested. |
| R010 | ChatGPT Pro | Reject duplicate periods in `phase_margins()` because period-keyed dicts collapse duplicates. | `relevant` | The current custom-period API returns period-keyed dictionaries. Duplicate periods can collapse information and should raise `ValueError`. |
| R011 | ChatGPT Pro | Make `phasewrap_features()` compute score from already-computed margins instead of recomputing through `phasewrap_score()`. | `relevant` | Not a performance issue, but a single-pass data path is cleaner for audit-facing deterministic APIs. |
| R012 | ChatGPT Pro, Claude | Expand CI from selected critical-path tests to fast/full/manual-live lanes. | `relevant` | Current CI is a curated reviewer gate. A full non-live lane would reduce drift risk across historical stages. |
| R013 | ChatGPT Pro | Add explicit `permissions: contents: read` to the main CI workflow. | `relevant` | Secret-scan workflow already does this. Main CI should match least-privilege practice. |
| R014 | ChatGPT Pro | Add build checks, linting, permissive type checking, and a coverage floor. | `relevant` | Current CI uploads coverage for selected tests but does not build wheels, lint, type-check, or enforce coverage. |
| R015 | ChatGPT Pro | Improve supply-chain reproducibility with a hash-pinned lockfile or reviewer container. | `relevant` | `requirements-review.txt` pins versions but not hashes. A long-lived archived verifier benefits from stronger locking. |
| R016 | ChatGPT Pro | Verify Gitleaks release checksums or use a pinned action/package-manager path. | `relevant` | Current workflow downloads a tarball by version without checksum verification. This is a valid supply-chain hardening point. |
| R017 | ChatGPT Pro | Add Dependabot and CodeQL where applicable. | `relevant` | Valid general maintenance hardening for a public repo, especially with optional provider dependencies. |
| R018 | ChatGPT Pro, Claude | Clarify `PhaseWrap` repository name versus `qrope` package name. | `partially_relevant` | A top-line note already exists, but long-run package aliasing or a compatibility shim remains valid if reviewer friction persists. |
| R019 | Claude | Rename the Python package from `qrope` to `phasewrap` with shims. | `partially_relevant` | The concern is valid; immediate full rename risks artifact/import churn. A compatibility shim is the valid long-run variant. |
| R020 | ChatGPT Pro | Clarify package version, archive version, and paper version. | `partially_relevant` | README and API docs now mention package `0.1.0` versus evidence `0.3.1-negative-results`. A fuller versioning page may still help. |
| R021 | Grok | Add a top-level mathematical one-paragraph summary with `SQR = m8 * m12`, mod-24 periodicity, and aliasing. | `relevant` | The facts exist, but a compact mathematical abstract near the top would reduce first-read friction. |
| R022 | Grok | Add visuals in README for score aliasing, hardware pipeline, or retrieval tasks. | `relevant` | Figures exist; embedding one or two high-signal visuals would help non-coder reviewers. |
| R023 | Grok, Claude | Add a high-level stage overview / stage-to-claim map. | `relevant` | The README has a table, but the stage tree needs a dedicated map that separates headline evidence from the full audit tree. |
| R024 | Grok | README claim-status table appears cut off mid-sentence. | `discard` | Local README inspection does not show this problem; likely a fetch/truncation artifact from the reviewer tool. |
| R025 | Grok | Reduce boilerplate in stage files through shared abstractions. | `relevant` | Valid maintainability issue for the large stage surface, though it should not alter frozen evidence behavior. |
| R026 | Grok | Add more type hints throughout. | `relevant` | Valid for maintainability and refactoring safety, especially before splitting historical modules. |
| R027 | Grok | Publish or link coverage reports. | `relevant` | CI uploads coverage XML but there is no obvious public coverage badge/report. |
| R028 | Grok | Add `CONTRIBUTORS.md` or changelog for traceability. | `partially_relevant` | Release notes exist; a changelog/contributors file could improve external collaboration but is not core evidence. |
| R029 | Grok | Add "How to cite / how to review this" section. | `partially_relevant` | Citation metadata exists, but a tighter reviewer/citation section in `REVIEWER_START.md` would help. |
| R030 | Grok | Prepare arXiv/blog/summary post after stabilization. | `relevant` | This is external communication, not repo correctness, but valid for the negative-results publication strategy. |
| R031 | Claude | Treat the repo as lab notebook plus evidence archive; expose only 4-6 decisive stages in the main path. | `relevant` | This aligns with current evidence: Stage 5, 11, 12, 67, 80/81, 219 carry most of the methodology argument, while the full stage tree is provenance. |
| R032 | Claude | Move full stage tree to archive or branch. | `partially_relevant` | The information-architecture concern is valid, but moving tracked evidence may hurt reproducibility. Better first step: keep files, add archive/stage-index surfaces and a smaller front door. |
| R033 | Claude | Avoid using `advantage` in hardware public-facing labels. | `relevant` | The prior pass added a narrower public alias, but new artifacts and docs should avoid `advantage` language except when describing historical manifest aliases. |
| R034 | Claude | Rename old Stage 218 historical manifest flag. | `partially_relevant` | Public wording should avoid it, but rewriting historical evidence strings would weaken provenance. Preserve alias, stop promoting it. |
| R035 | Claude | State more bluntly that Stage 218 is an encoding/readout-noise comparison, not positional-encoding evidence for transformers. | `relevant` | Current claim boundary says this, but stronger upfront wording would reduce misreadings. |
| R036 | Claude | Consider a permissive license instead of `AGPL-3.0-only`. | `partially_relevant` | Valid reuse-friction concern. License selection is strategic/legal, not an evidence defect. It needs maintainer/legal decision. |
| R037 | Claude | Retire patent-posture surface area entirely. | `discard` | Current repo posture intentionally keeps patent material low-prominence and non-claim-bearing. Removing factual legal notices is not required for scientific honesty. |
| R038 | Claude | `PATENTS.md` in a negative-results repo sends mixed signals. | `partially_relevant` | The signaling concern is real, but the current low-prominence posture is an acceptable compromise unless legal strategy changes. |
| R039 | Claude | `autograd` is aging; use JAX/PyTorch or custom backprop for future ablations. | `partially_relevant` | Valid for future extension, less relevant to the archived negative-results evidence and public scoring API. |
| R040 | Claude | Curated CI means most evidence stages are not gated. | `relevant` | Same core issue as R012; a full non-live CI lane is valid. |
| R041 | Claude | Add pre-commit and type-checking config. | `relevant` | Valid maintainability hardening for a public methodology repo. |
| R042 | Claude | Stage 219 ranking parity should not be framed as useful without probability/calibration caveats. | `relevant` | Current Stage 219 already records degradation separately; docs should continue making the caveat load-bearing. |
| R043 | Claude | Pull Stage 5 exact-recovery self-refutation into the abstract/front door. | `relevant` | This is scientifically important: mod-24 lookup/direct features exactly solve the original synthetic target, limiting early positive interpretations. |
| R044 | Claude | Hardware result has no transformer positional-encoding hypothesis attached. | `relevant` | This is accurate and should remain explicit in all hardware summaries. |
| R045 | Claude | Seek at least one external replication or external stage review before formal publication. | `relevant` | External review reduces self-confirmation risk and is consistent with the repo's open-review goal. |
| R046 | Claude | Zero stars/forks/issues are a warning sign. | `partially_relevant` | Useful as a community-engagement signal, not as scientific evidence against the repo. |
| R047 | Claude | Main paper should be a short methods note centered on assistance-pipeline confounds. | `relevant` | This matches the strongest evidence and current publication roadmap. |
| R048 | ChatGPT Pro | PhaseWrap is not yet a polished Python library. | `relevant` | Accurate. The stable public API is small, but the repo is primarily evidence/methodology infrastructure. |
| R049 | Grok | Repo is publication-ready as negative-results/methodology venue. | `partially_relevant` | Directionally valid, but reviewer ergonomics and CI/repro hardening are still worth improving before formal submission. |
| R050 | Grok | No open issues/PRs is fine for a solo/closed research line. | `partially_relevant` | Accurate as description, but the open-review goal would benefit from external issues or review threads. |
| R051 | Claude supplement | The general methodology warning is not novel; it is an instance of shortcut-learning, control-task, spurious-cue, and NoPE/NoPos precedents. | `relevant` | Primary-source check supports this. PhaseWrap should frame its contribution as a worked example, not as discovery of the general concern. |
| R052 | Claude supplement | Cite Geirhos, Hewitt and Liang, McCoy, Niven and Kao, Sinha, Haviv, Kazemnejad, and Wang in the methodology paper. | `relevant` | The current paper needed a clearer related-work boundary. These references are directly relevant to shortcut learning, control tasks, and NoPE/NoPos baselines. |
| R053 | Claude supplement | Do not call specific external papers "suspect" without reproducing their experiments under stronger controls. | `relevant` | This is the correct scientific posture. The repo can make a category-level warning about missing controls, not allegations about particular papers. |
| R054 | Claude supplement | Position Stage 80/81 as a granular worked example of an established concern. | `relevant` | This preserves the value of the PhaseWrap evidence while avoiding novelty overclaiming. |
| R055 | Claude supplement | If the draft implies the warning itself is novel, reviewers will object. | `relevant` | The methodology paper should explicitly state the novelty boundary. |

## Items To Discard

Only two recommendations are discarded:

- `R024`: local README inspection does not confirm a cut-off claim-status row.
- `R037`: removing patent-status documentation entirely is not necessary for scientific claim hygiene because the repo already keeps it low-prominence and non-claim-bearing.

Everything else is at least partially relevant when judged against long-run repo quality rather than short-term implementation cost.

The novelty supplement adds no discarded items. Its main effect is to narrow the claimed contribution: PhaseWrap should be presented as an auditable worked example of established shortcut-learning/control-task/NoPE concerns.

## Highest-Value Backlog Themes

| Rank | Theme | Relevant items | Why it matters |
| --- | --- | --- | --- |
| 1 | Reviewer front door | R001-R004, R021-R023, R029, R043 | The evidence is strong but too spread out. First 15 minutes should be effortless. |
| 2 | Stage and evidence information architecture | R003, R005, R006, R023, R031, R032, R047 | The repo should distinguish headline evidence, full reproduction, historical archive, and live-provider code. |
| 3 | Validation hardening | R007-R011, R025, R026 | Silent fallbacks and duplicate-period edge cases are inconsistent with audit-oriented reproducibility. |
| 4 | CI and supply-chain hardening | R012-R017, R027, R040, R041 | Current CI protects the public path; long-run evidence maintenance needs broader non-live coverage and locked reviewer dependencies. |
| 5 | Hardware-language containment | R004, R033-R035, R042, R044 | Hardware-readout positives must never be confused with transformer, RoPE, or quantum-advantage claims. |
| 6 | External review and publication path | R030, R045-R050 | The repo's scientific value increases if external reviewers can independently walk the short path and open issues. |

## Recommended Next Decision

If choosing the next work package by relevance rather than timeline, the highest leverage is:

1. Add `REVIEWER_START.md`.
2. Add one canonical no-credential verifier CLI.
3. Add a dedicated stage-to-claim map that exposes only headline stages first.
4. Harden `qsim` and scoring edge cases.
5. Split CI into fast/full/manual-live lanes.

Those changes directly address the common critique across all three reviewers: the repo's evidence discipline is strong, but the reviewer path is still too noisy.
