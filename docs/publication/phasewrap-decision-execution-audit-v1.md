# PhaseWrap Decision Execution Audit v1

Status: `DECISION_MEMO_REPO_ACTIONS_EXECUTED_RELEASE_HELD`

Date: `2026-05-25`

## Purpose

This audit checks whether the actions in `phasewrap-research-program-decision-v1.md` have been executed in the repository.

## Requirement-by-Requirement Audit

| Decision memo requirement | Evidence | Status |
| --- | --- | --- |
| Stop treating PhaseWrap as an active positive RoPE-replacement or quantum-advantage program. | README, roadmap, quickstart, decision memo, methodology paper, and execution freeze all state that the positive replacement line is closed. | Executed |
| Publish the current body of work as negative-results and methodology. | `phasewrap-methodology-paper-v1.md`, `negative-results-publication-roadmap-v1.md`, release plan, README, CITATION, and Zenodo metadata use negative-results framing. | Executed locally |
| Prepare one focused methodology paper. | `phasewrap-methodology-paper-v1.md` exists with status `METHODOLOGY_PAPER_DRAFT_V1`. | Executed |
| Carry the Stage 67-96 arc. | The methodology paper evidence table and main result cover Stages 67, 74/75, 80, 81, 82, 93, 94, 96, and Stage 219 boundary context. | Executed |
| Use Stage 11 score theory as appendix material. | Methodology paper Appendix A summarizes period `24`, `10` distinct residue scores, alias growth, and Fourier support `[1, 2, 3, 5]`. | Executed |
| Include Stage 216-218 only as bounded hardware-audit evidence. | Methodology paper Appendix B includes Stage 216-218 as bounded two-qubit readout-audit evidence and explicitly excludes transformer evidence, RoPE replacement, and quantum advantage. | Executed |
| Keep Stage 219 limited to ranking parity with calibration degradation. | Stage 219 docs, README, method paper, code, manifest, and tests now use ranking-parity language and require probability/calibration degradation in the same boundary. | Executed |
| Preserve verifier scripts, frozen packets, manifests, raw counts, calibration checks, claim cards, and failed-run records. | Publication package verifier checks required files and Stage 216-219 manifests; regenerated Stage 70, 80, 81, 94, 96, 216, 217, 218, and 219 outputs are present. | Executed |
| Stop adding positive-replacement stages by default. | `phasewrap-execution-freeze-v1.md` freezes PhaseWrap-positive execution unless a reopen gate is predeclared. | Executed |
| Keep patent/IP posture factual and low-prominence. | `PATENTS.md`, `NOTICE`, patent status note, README, and release checklist describe patent status as a low-prominence legal mention, not scientific evidence. | Executed |
| Keep receipt-specific identifiers and confirmation numbers out of public materials. | Publication verifier and explicit public-file scans check forbidden receipt/confirmation fragments. | Executed |
| Prepare conservative release notes for the negative-results tag. | `release-notes-v0.3.0-negative-results.md` exists with support/non-support boundaries and verifier commands. | Executed |
| Release under a conservative negative-results tag only after wording is safe. | Release plan recommends `v0.3.0-negative-results`; package verifier passes. No local tag, GitHub release, push, DOI refresh, arXiv, or OSF publication has been performed. | Held pending explicit release approval |

## Verification Commands

Executed successfully:

```bash
python scripts/verify_publication_package.py
python -m pytest tests/test_publication_package_verifier.py tests/test_stage219_rope_substitution_gate.py
python scripts/check_readme_verifier_output.py
python scripts/run_stage11_phasewrap_theory.py
python scripts/run_stage70_strongest_honest_claim_synthesis.py
python scripts/run_stage80_support_routed_token_selector_audit.py
python scripts/run_stage81_soft_support_routed_token_selector_audit.py
python scripts/run_stage94_promotion_gate_readiness_audit.py
python scripts/run_stage96_claim_card_audit.py
python scripts/run_stage216_full_replacement_merged_result_counts.py
python scripts/run_stage217_full_replacement_calibration_validation.py
python scripts/run_stage218_full_replacement_hardware_metric_interpreter.py
python scripts/run_stage219_rope_substitution_gate.py
```

Public-facing receipt/confirmation scan returned no matches for the configured forbidden fragments.

## Release Boundary

The repository is locally prepared for a negative-results release, but no external release action has been executed.

External release actions require explicit approval because they change public state:

- committing the current working tree;
- creating a local or remote release tag;
- pushing to GitHub;
- creating a GitHub release;
- refreshing Zenodo metadata or DOI records;
- posting arXiv, OSF, blog, or public announcement material.

## Current Verdict

All repo-side actions in the decision memo are executed. The only held item is external publication/tagging, which is intentionally pending explicit release approval.
